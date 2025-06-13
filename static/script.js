document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const clearButton = document.getElementById('clear-btn');
    const micButton = document.getElementById('mic-btn');
    const audioStatus = document.getElementById('audio-status');
    const volumeBar = document.getElementById('volume-bar');
    const volumeText = document.getElementById('volume-text');
    const listeningStatus = document.getElementById('listening-status');
    
    // 사용자 ID 관련 요소들
    const userIdInput = document.getElementById('user-id');
    const loginButton = document.getElementById('login-btn');
    const currentUserDiv = document.getElementById('current-user');
    const currentUserName = document.getElementById('current-user-name');
    const logoutButton = document.getElementById('logout-btn');
    
    let isLoading = false;
    let currentUserId = null;
    let sessionId = null;
    let audioSocket = null;
    let isListening = false;

    // 초기 상태: 채팅 비활성화
    setChatDisabled(true);

    // 사용자 로그인
    async function loginUser() {
        const userId = userIdInput.value.trim();
        
        if (!userId) {
            alert('사용자 ID를 입력해주세요.');
            return;
        }
        
        if (userId.length < 2) {
            alert('사용자 ID는 2글자 이상이어야 합니다.');
            return;
        }

        currentUserId = userId;
        sessionId = `user_${userId}`;
        
        // UI 업데이트
        userIdInput.style.display = 'none';
        loginButton.style.display = 'none';
        currentUserDiv.style.display = 'flex';
        currentUserName.textContent = userId;
        
        // 채팅 활성화
        setChatDisabled(false);
        
        // 음성 인식 시작/중지
    function toggleSpeechRecognition() {
        if (!currentUserId) {
            alert('먼저 로그인해주세요.');
            return;
        }

        if (isListening) {
            stopSpeechRecognition();
        } else {
            startSpeechRecognition();
        }
    }

    // 음성 인식 시작
    function startSpeechRecognition() {
        // Web Speech API 지원 확인
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
            return;
        }

        if (audioSocket) {
            audioSocket.close();
        }

        // Web Speech API 초기화
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'ko-KR';
        recognition.interimResults = true;
        recognition.continuous = true;
        recognition.maxAlternatives = 1;

        // WebSocket 연결
        audioSocket = new WebSocket(`ws://${window.location.host}/audio/ws/audio`);
        
        audioSocket.onopen = function() {
            console.log('Audio WebSocket connected');
            isListening = true;
            updateMicButton();
            audioStatus.style.display = 'block';
            listeningStatus.textContent = '🎤 음성을 듣고 있습니다...';
            
            // 음성 인식 시작
            recognition.start();
        };

        audioSocket.onmessage = function(event) {
            const data = event.data;
            
            if (data.startsWith('volume:')) {
                const volume = parseInt(data.split(':')[1]);
                volumeBar.style.width = `${Math.min(volume, 100)}%`;
                volumeText.textContent = `${volume}%`;
                
            } else if (data.startsWith('text:')) {
                const text = data.split(':')[1];
                if (text && text.trim()) {
                    userInput.value = text;
                    listeningStatus.textContent = `✅ 인식 완료: "${text}"`;
                    
                    // 자동으로 메시지 전송
                    setTimeout(() => {
                        sendMessage();
                        stopSpeechRecognition();
                    }, 1000);
                }
                
            } else if (data.startsWith('error:')) {
                const error = data.split(':')[1];
                listeningStatus.textContent = `❌ 오류: ${error}`;
                console.error('Speech recognition error:', error);
            }
        };

        // 음성 인식 이벤트 핸들러
        recognition.onresult = function(event) {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // 중간 결과 표시
            if (interimTranscript) {
                listeningStatus.textContent = `🎤 인식 중: "${interimTranscript}"`;
                // 가상 볼륨 효과
                const volume = Math.min(interimTranscript.length * 10, 100);
                volumeBar.style.width = `${volume}%`;
                volumeText.textContent = `${volume}%`;
                audioSocket.send(`volume:${volume}`);
            }

            // 최종 결과 처리
            if (finalTranscript) {
                console.log('Final transcript:', finalTranscript);
                audioSocket.send(`speech_result:${finalTranscript}`);
            }
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            listeningStatus.textContent = `❌ 음성 인식 오류: ${event.error}`;
            audioSocket.send(`speech_error:${event.error}`);
        };

        recognition.onend = function() {
            console.log('Speech recognition ended');
            if (isListening) {
                // 자동으로 재시작 (연속 인식)
                setTimeout(() => {
                    if (isListening) {
                        recognition.start();
                    }
                }, 100);
            }
        };

        audioSocket.onclose = function() {
            console.log('Audio WebSocket closed');
            recognition.stop();
            stopSpeechRecognition();
        };

        audioSocket.onerror = function(error) {
            console.error('Audio WebSocket error:', error);
            listeningStatus.textContent = '❌ 음성 인식 연결 오류';
            recognition.stop();
            stopSpeechRecognition();
        };

        // recognition 객체를 나중에 정리할 수 있도록 저장
        audioSocket.recognition = recognition;
    }

    // 음성 인식 중지
    function stopSpeechRecognition() {
        if (audioSocket) {
            if (audioSocket.recognition) {
                audioSocket.recognition.stop();
            }
            audioSocket.close();
            audioSocket = null;
        }
        
        isListening = false;
        updateMicButton();
        audioStatus.style.display = 'none';
        
        // 입력창 효과 제거
        userInput.style.borderColor = '#e9ecef';
        userInput.style.boxShadow = 'none';
    }

    // 마이크 버튼 상태 업데이트
    function updateMicButton() {
        if (isListening) {
            micButton.classList.add('active');
            micButton.textContent = '🔴';
            micButton.title = '음성 인식 중지';
        } else {
            micButton.classList.remove('active');
            micButton.textContent = '🎤';
            micButton.title = '음성 인식 시작';
        }
    }
        await loadChatHistory();
        
        addMessage('bot', `안녕하세요 ${userId}님! 저는 로봇 사탕가게 직원입니다. 빨간색 사탕(딸기), 파란 사탕(소다), 노란 사탕(레몬), 오렌지 주스를 판매합니다. 무엇을 주문하시겠어요? 🍭🤖`);
        
        userInput.focus();
    }

    // 사용자 로그아웃
    function logoutUser() {
        currentUserId = null;
        sessionId = null;
        
        // UI 초기화
        userIdInput.style.display = 'block';
        loginButton.style.display = 'block';
        userIdInput.value = '';
        currentUserDiv.style.display = 'none';
        
        // 채팅 비활성화 및 초기화
        setChatDisabled(true);
        chatBox.innerHTML = `
            <div class="message bot">
                안녕하세요! 저는 로봇 사탕가게 직원입니다. 먼저 사용자 ID를 입력해주세요! 🍭🤖
            </div>
        `;
        
        userIdInput.focus();
    }

    // 채팅 활성화/비활성화
    function setChatDisabled(disabled) {
        const chatInputDiv = document.querySelector('.chat-input');
        if (disabled) {
            chatInputDiv.classList.add('chat-disabled');
            userInput.disabled = true;
            sendButton.disabled = true;
        } else {
            chatInputDiv.classList.remove('chat-disabled');
            userInput.disabled = false;
            sendButton.disabled = false;
        }
    }

    // 이전 대화 기록 불러오기
    async function loadChatHistory() {
        if (!sessionId) return;
        
        try {
            const response = await fetch(`/chatbot/history/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                const history = data.history;
                
                if (history && history.length > 0) {
                    // 채팅박스 초기화 (환영 메시지 제거)
                    chatBox.innerHTML = '';
                    
                    // 최근 10개 대화만 표시 (역순으로 정렬되어 있으므로 reverse)
                    history.reverse().forEach(([userMsg, aiMsg, timestamp]) => {
                        addMessage('user', userMsg);
                        addMessage('bot', aiMsg);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // 메시지 전송 함수
    async function sendMessage() {
        if (!currentUserId || !sessionId) {
            alert('먼저 로그인해주세요.');
            return;
        }
        
        const message = userInput.value.trim();
        
        if (!message || isLoading) return;
        
        // 사용자 메시지 추가
        addMessage('user', message);
        userInput.value = '';
        
        // 로딩 상태 설정
        setLoading(true);
        
        // 로딩 메시지 표시
        const loadingDiv = addLoadingMessage();
        
        try {
            const response = await fetch('/chatbot/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // 로딩 메시지 제거
            if (loadingDiv) {
                loadingDiv.remove();
            }
            
            // AI 응답 추가
            addMessage('bot', data.response);
            
        } catch (error) {
            console.error('Error:', error);
            
            // 로딩 메시지 제거
            if (loadingDiv) {
                loadingDiv.remove();
            }
            
            addMessage('bot', '죄송합니다. 응답을 가져오는 중에 오류가 발생했습니다. 다시 시도해주세요.');
        } finally {
            setLoading(false);
        }
    }

    // 메시지 추가 함수
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        // 줄바꿈 처리: \n을 실제 줄바꿈으로 변환
        messageDiv.textContent = text;
        
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 로딩 메시지 추가 함수
    function addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot loading-message';
        loadingDiv.innerHTML = `
            <span>AI가 응답을 생성하고 있습니다</span>
            <div class="loading"></div>
            <div class="loading"></div>
            <div class="loading"></div>
        `;
        
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        return loadingDiv;
    }

    // 로딩 상태 설정 함수
    function setLoading(loading) {
        isLoading = loading;
        sendButton.disabled = loading;
        userInput.disabled = loading;
        
        if (loading) {
            sendButton.textContent = '전송중...';
            userInput.placeholder = 'AI가 응답을 생성하고 있습니다...';
        } else {
            sendButton.textContent = '전송';
            userInput.placeholder = '메시지를 입력하세요...';
            userInput.focus();
        }
    }

    // 대화 기록 초기화 함수
    async function clearChat() {
        if (!currentUserId || !sessionId) {
            alert('먼저 로그인해주세요.');
            return;
        }
        
        if (!confirm('정말로 대화 기록을 삭제하시겠습니까?')) {
            return;
        }
        
        try {
            const response = await fetch('/chatbot/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (response.ok) {
                chatBox.innerHTML = `
                    <div class="message bot">
                        안녕하세요 ${currentUserId}님! 저는 로봇 사탕가게 직원입니다. 빨간색 사탕(딸기), 파란 사탕(소다), 노란 사탕(레몬), 오렌지 주스를 판매합니다. 무엇을 주문하시겠어요? 🍭🤖
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            alert('대화 기록 삭제 중 오류가 발생했습니다.');
        }
    }

    // 이벤트 리스너 등록
    sendButton.addEventListener('click', sendMessage);
    clearButton.addEventListener('click', clearChat);
    loginButton.addEventListener('click', loginUser);
    logoutButton.addEventListener('click', logoutUser);
    micButton.addEventListener('click', toggleSpeechRecognition);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    userIdInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            loginUser();
        }
    });

    // 페이지 언로드 시 WebSocket 정리
    window.addEventListener('beforeunload', function() {
        if (audioSocket) {
            audioSocket.close();
        }
    });

    // 초기 포커스를 사용자 ID 입력창에
    userIdInput.focus();
});