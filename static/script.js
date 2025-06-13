document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const clearButton = document.getElementById('clear-btn');
    
    // 사용자 ID 관련 요소들
    const userIdInput = document.getElementById('user-id');
    const loginButton = document.getElementById('login-btn');
    const currentUserDiv = document.getElementById('current-user');
    const currentUserName = document.getElementById('current-user-name');
    const logoutButton = document.getElementById('logout-btn');
    
    let isLoading = false;
    let currentUserId = null;
    let sessionId = null;

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
        
        // 이전 대화 기록 불러오기
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

    // 초기 포커스를 사용자 ID 입력창에
    userIdInput.focus();
});