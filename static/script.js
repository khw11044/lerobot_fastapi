document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const clearButton = document.getElementById('clear-btn');
    
    let isLoading = false;
    let sessionId = 'user_' + Math.random().toString(36).substr(2, 9);

    // 메시지 전송 함수
    async function sendMessage() {
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
        try {
            const response = await fetch('/chatbot/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                chatBox.innerHTML = `
                    <div class="message bot">
                        안녕하세요! 저는 AI 어시스턴트입니다. 궁금한 것이 있으시면 언제든 물어보세요! 😊
                    </div>
                `;
                
                // 새로운 세션 ID 생성
                sessionId = 'user_' + Math.random().toString(36).substr(2, 9);
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }

    // 이벤트 리스너 등록
    sendButton.addEventListener('click', sendMessage);
    clearButton.addEventListener('click', clearChat);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 입력창에 포커스
    userInput.focus();
});