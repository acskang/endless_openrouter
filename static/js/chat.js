// ===================================================================
// Chat.js - Django Views API를 사용하는 WSGI 호환 버전
// ===================================================================

// Global Variables
let isLoggedIn = false;
let currentUser = null;
let conversationHistory = [];
let isProcessing = false;
let historyLoaded = false;

// DOM 로드 완료 후 초기화
document.addEventListener("DOMContentLoaded", function () {
  console.log("🚀 Chat.js initialized");
  initializeChat();
});

// 채팅 초기화
function initializeChat() {
  checkLoginStatus();
  setupChatButton();
  setupChatModal();
  console.log("✅ Chat system initialized");
}

// 서버에서 사용자별 대화 기록 로드
async function loadConversationHistoryFromServer() {
  if (!isLoggedIn || historyLoaded) {
    return;
  }

  try {
    console.log("📚 서버에서 대화 기록 로드 중...");

    // CSRF 토큰 가져오기
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
      console.error("CSRF 토큰을 찾을 수 없습니다");
      return;
    }

    // 서버에서 채팅 히스토리 요청
    const response = await fetch("/chat/history/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
    });

    if (response.ok) {
      const data = await response.json();

      if (data.success) {
        conversationHistory = data.history || [];
        historyLoaded = true;

        console.log(
          "📚 서버에서 대화 기록 로드 완료:",
          conversationHistory.length,
          "개 메시지"
        );

        // 로드된 히스토리를 화면에 표시
        displayConversationHistory();
      } else {
        console.error("서버 히스토리 로드 실패:", data.error);
        // 로컬 스토리지 폴백
        loadConversationHistoryFromLocal();
      }
    } else {
      console.error("히스토리 API 호출 실패:", response.status);
      // 로컬 스토리지 폴백
      loadConversationHistoryFromLocal();
    }
  } catch (error) {
    console.error("서버 히스토리 로드 오류:", error);
    // 로컬 스토리지 폴백
    loadConversationHistoryFromLocal();
  }
}

// 로컬 스토리지에서 대화 기록 로드 (폴백용)
function loadConversationHistoryFromLocal() {
  try {
    const saved = localStorage.getItem("chatHistory");
    if (saved) {
      const localHistory = JSON.parse(saved);
      // 서버에서 이미 로드된 히스토리가 없을 때만 로컬 히스토리 사용
      if (conversationHistory.length === 0) {
        conversationHistory = localHistory;
        console.log(
          "📚 로컬 대화 기록 로드됨:",
          conversationHistory.length,
          "개 메시지"
        );
      }
    }
  } catch (error) {
    console.error("로컬 대화 기록 로드 실패:", error);
    conversationHistory = [];
  }
}

// 대화 기록 저장 (로컬 스토리지 - 백업용)
function saveConversationHistory() {
  try {
    // 최근 50개 메시지만 저장
    const toSave = conversationHistory.slice(-50);
    localStorage.setItem("chatHistory", JSON.stringify(toSave));
  } catch (error) {
    console.error("대화 기록 저장 실패:", error);
  }
}

// CSRF 토큰 가져오기
function getCsrfToken() {
  // 페이지에 있는 CSRF 토큰 input 찾기
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
  if (csrfToken) {
    return csrfToken.value;
  }

  // 쿠키에서 CSRF 토큰 가져오기
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === "csrftoken") {
      return value;
    }
  }

  console.error("CSRF 토큰을 찾을 수 없습니다");
  return null;
}

// 로그인 상태 확인
function checkLoginStatus() {
  console.log("🔐 로그인 상태 확인");

  // Django 템플릿에서 이미 버튼이 표시되어 있다면 로그인 상태로 간주
  const chatFloatingBtn = document.getElementById("chatFloatingBtn");
  if (
    chatFloatingBtn &&
    window.getComputedStyle(chatFloatingBtn).display === "flex"
  ) {
    isLoggedIn = true;
    currentUser = { username: "user" };
    console.log("✅ Django 템플릿에서 로그인 상태 확인됨");
    return;
  }

  // 환영 메시지에서 사용자 확인
  const userElement = document.querySelector(".welcome-section p");
  if (userElement && userElement.textContent.includes("환영합니다")) {
    isLoggedIn = true;
    const username = userElement.textContent.match(/환영합니다, (.+)님!/)?.[1];
    if (username) {
      currentUser = { username: username };
    }
    showChatButton();
    return;
  }

  // 네비게이션에서 로그아웃 링크 확인
  const logoutLink = document.querySelector('a[href*="logout"]');
  if (logoutLink) {
    isLoggedIn = true;
    currentUser = { username: "user" };
    showChatButton();
    return;
  }

  // 로그아웃 상태
  isLoggedIn = false;
  currentUser = null;
  hideChatButton();
}

// 채팅 버튼 표시
function showChatButton() {
  const chatFloatingBtn = document.getElementById("chatFloatingBtn");
  if (chatFloatingBtn) {
    chatFloatingBtn.style.display = "flex";
    setTimeout(() => {
      chatFloatingBtn.classList.add("show");
    }, 100);
    console.log("💬 채팅 버튼 표시됨");
  }
}

// 채팅 버튼 숨김
function hideChatButton() {
  const chatFloatingBtn = document.getElementById("chatFloatingBtn");
  if (chatFloatingBtn) {
    chatFloatingBtn.classList.remove("show");
    setTimeout(() => {
      chatFloatingBtn.style.display = "none";
    }, 300);
    console.log("🚫 채팅 버튼 숨겨짐");
  }
}

// 채팅 버튼 설정
function setupChatButton() {
  const chatFloatingBtn = document.getElementById("chatFloatingBtn");
  const chatModal = document.getElementById("chatModal");

  if (!chatFloatingBtn || !chatModal) {
    console.log("⚠️ 채팅 요소를 찾을 수 없음");
    return;
  }

  // 채팅 버튼 클릭 이벤트
  chatFloatingBtn.addEventListener("click", function () {
    console.log("💬 채팅 버튼 클릭됨");
    toggleChatModal();
  });
}

// 채팅 모달 설정
function setupChatModal() {
  const chatModal = document.getElementById("chatModal");
  const closeChat = document.getElementById("closeChat");
  const sendMessage = document.getElementById("sendMessage");
  const messageInput = document.getElementById("messageInput");

  if (!chatModal) {
    console.log("⚠️ 채팅 모달을 찾을 수 없음");
    return;
  }

  // 모달 닫기 버튼
  if (closeChat) {
    closeChat.addEventListener("click", function () {
      console.log("❌ 채팅 모달 닫기 버튼 클릭됨");
      closeChatModal();
    });
  }

  // 메시지 전송 설정
  if (sendMessage && messageInput) {
    const sendUserMessage = async function () {
      const messageText = messageInput.value.trim();
      if (!messageText) return;

      // 처리 중이면 무시
      if (isProcessing) {
        console.log("⏳ 이미 처리 중입니다");
        return;
      }

      // 로그인 확인
      if (!isLoggedIn) {
        displaySystemMessage("로그인이 필요합니다.");
        return;
      }

      console.log("📤 메시지 전송:", messageText);

      // 입력창 초기화
      messageInput.value = "";

      // 사용자 메시지 표시
      displayMessage(messageText, "sent");

      // 대화 기록에 추가
      const userMessage = {
        role: "user",
        content: messageText,
        timestamp: new Date().toISOString(),
      };
      conversationHistory.push(userMessage);

      // AI 응답 요청
      await getAIResponse(messageText);
    };

    // 전송 버튼 클릭
    sendMessage.addEventListener("click", sendUserMessage);

    // Enter 키 입력
    messageInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendUserMessage();
      }
    });
  }
}

// Django API를 통한 AI 응답 받기
async function getAIResponse(userMessage) {
  if (isProcessing) return;

  isProcessing = true;

  // 타이핑 인디케이터 표시
  const typingId = displaySystemMessage(
    "AI가 응답을 생성하고 있습니다...",
    "typing-indicator"
  );

  try {
    // CSRF 토큰 가져오기
    const csrfToken = getCsrfToken();

    if (!csrfToken) {
      throw new Error("CSRF 토큰을 찾을 수 없습니다.");
    }

    // Django API 호출
    const response = await fetch("/chat/api/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
      body: JSON.stringify({
        message: userMessage,
        history: conversationHistory.slice(-10), // 최근 10개 대화만 전송
      }),
    });

    // 타이핑 인디케이터 제거
    removeSystemMessage(typingId);

    const data = await response.json();

    if (response.ok && data.success) {
      const aiMessage = data.message;

      // AI 응답 표시
      displayMessage(aiMessage, "received");

      // 대화 기록에 추가
      const aiResponse = {
        role: "assistant",
        content: aiMessage,
        timestamp: data.timestamp || new Date().toISOString(),
        response_id: data.response_id,
        ai_model: data.ai_model,
        cached: data.cached || false,
      };
      conversationHistory.push(aiResponse);

      // 로컬 스토리지에 백업 저장
      saveConversationHistory();

      console.log("✅ AI 응답 받음");
    } else {
      // 에러 처리
      const errorMessage = data.error || "AI 서비스에 문제가 발생했습니다.";

      if (response.status === 401) {
        displaySystemMessage("로그인이 필요합니다. 다시 로그인해주세요.");
        // 로그인 페이지로 리다이렉트 또는 모달 표시
        setTimeout(() => {
          window.location.href = "/account/login/";
        }, 2000);
      } else if (response.status === 429) {
        displaySystemMessage(
          "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
        );
      } else {
        displaySystemMessage(errorMessage);
      }

      console.error("❌ API 에러:", errorMessage);
    }
  } catch (error) {
    console.error("❌ AI 응답 오류:", error);

    // 타이핑 인디케이터 제거
    removeSystemMessage(typingId);

    // 에러 메시지 표시
    let errorMessage = "AI 서비스에 문제가 발생했습니다.";

    if (error.message.includes("Failed to fetch")) {
      errorMessage = "네트워크 연결에 문제가 있습니다. 연결을 확인해주세요.";
    } else if (error.message.includes("CSRF")) {
      errorMessage =
        "보안 토큰 오류가 발생했습니다. 페이지를 새로고침해주세요.";
    }

    displaySystemMessage(errorMessage);
  } finally {
    isProcessing = false;
  }
}

// 채팅 모달 토글
function toggleChatModal() {
  const chatModal = document.getElementById("chatModal");
  const messageInput = document.getElementById("messageInput");

  if (chatModal.classList.contains("show")) {
    closeChatModal();
  } else {
    openChatModal();
    // 입력창에 포커스
    if (messageInput) {
      setTimeout(() => {
        messageInput.focus();
      }, 300);
    }
  }
}

// 채팅 모달 열기
function openChatModal() {
  const chatModal = document.getElementById("chatModal");
  if (chatModal) {
    chatModal.classList.add("show");
    console.log("🔓 채팅 모달 열림");

    // 서버에서 대화 기록 로드 (처음 한 번만)
    if (isLoggedIn && !historyLoaded) {
      loadConversationHistoryFromServer();
    } else {
      // 이미 로드된 대화 기록 표시
      displayConversationHistory();
    }

    // 상태 표시 업데이트
    updateConnectionStatus("ready");
  }
}

// 채팅 모달 닫기
function closeChatModal() {
  const chatModal = document.getElementById("chatModal");
  if (chatModal) {
    chatModal.classList.remove("show");
    console.log("🔒 채팅 모달 닫힘");
  }
}

// 저장된 대화 기록 표시
function displayConversationHistory() {
  const chatMessages = document.getElementById("chatMessages");
  if (!chatMessages) return;

  // 기존 메시지 클리어 (환영 메시지 유지)
  const welcomeMessage = chatMessages.querySelector(".message.received");
  const welcomeMessageClone = welcomeMessage
    ? welcomeMessage.cloneNode(true)
    : null;

  chatMessages.innerHTML = "";

  // 환영 메시지 다시 추가
  if (welcomeMessageClone) {
    chatMessages.appendChild(welcomeMessageClone);
  }

  // 대화 기록이 있을 때만 표시
  if (conversationHistory.length > 0) {
    conversationHistory.forEach((msg) => {
      if (msg.role === "user") {
        displayMessage(msg.content, "sent", false);
      } else if (msg.role === "assistant") {
        displayMessage(msg.content, "received", false);
      }
    });

    console.log(
      "📜 대화 기록 표시 완료:",
      conversationHistory.length,
      "개 메시지"
    );
  }

  // 스크롤을 맨 아래로
  setTimeout(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }, 100);
}

// 메시지 표시
function displayMessage(messageText, messageType, shouldScroll = true) {
  const chatMessages = document.getElementById("chatMessages");
  if (!chatMessages) {
    console.error("❌ chatMessages 요소를 찾을 수 없습니다");
    return;
  }

  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${messageType}`;

  const timestamp = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageDiv.innerHTML = `
    <div class="message-content">
      <p>${escapeHtml(messageText)}</p>
      <span class="timestamp">${timestamp}</span>
    </div>
  `;

  chatMessages.appendChild(messageDiv);

  // 스크롤을 맨 아래로
  if (shouldScroll) {
    setTimeout(() => {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 10);
  }

  console.log(`💬 메시지 표시됨 (${messageType})`);
}

// 시스템 메시지 표시 (ID 반환)
function displaySystemMessage(messageText, className = "") {
  const chatMessages = document.getElementById("chatMessages");
  if (!chatMessages) return null;

  const messageId = `system-message-${Date.now()}`;
  const messageDiv = document.createElement("div");
  messageDiv.className = `message system ${className}`;
  messageDiv.id = messageId;

  const timestamp = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageDiv.innerHTML = `
    <div class="message-content" style="background: rgba(0, 0, 0, 0.05); color: #666; font-size: 14px; padding: 8px 16px; border-radius: 12px; max-width: 90%; text-align: center;">
      <p>${escapeHtml(messageText)}</p>
      <span class="timestamp">${timestamp}</span>
    </div>
  `;

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  console.log("📢 시스템 메시지 표시:", messageText);
  return messageId;
}

// 시스템 메시지 제거
function removeSystemMessage(messageId) {
  if (!messageId) return;
  const message = document.getElementById(messageId);
  if (message) {
    message.remove();
  }
}

// 연결 상태 업데이트
function updateConnectionStatus(status) {
  const chatTitle = document.querySelector(".chat-title");
  if (chatTitle) {
    switch (status) {
      case "ready":
        chatTitle.textContent = "TheSysM Support";
        break;
      case "processing":
        chatTitle.textContent = "TheSysM Support (처리중...)";
        break;
      case "error":
        chatTitle.textContent = "TheSysM Support (오류)";
        break;
      default:
        chatTitle.textContent = "TheSysM Support";
    }
  }
  console.log("📊 상태 업데이트:", status);
}

// HTML 이스케이프 (XSS 방지)
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// 대화 기록 초기화
function clearConversationHistory() {
  conversationHistory = [];
  historyLoaded = false;
  localStorage.removeItem("chatHistory");

  const chatMessages = document.getElementById("chatMessages");
  if (chatMessages) {
    // 환영 메시지만 남기고 초기화
    const welcomeMessage = chatMessages.querySelector(".message.received");
    chatMessages.innerHTML = "";
    if (welcomeMessage) {
      chatMessages.appendChild(welcomeMessage.cloneNode(true));
    }
  }
  displaySystemMessage("대화 기록이 초기화되었습니다.");
  console.log("🗑️ 대화 기록 초기화됨");
}

// 외부에서 호출 가능한 함수들
window.chatSystem = {
  showButton: showChatButton,
  hideButton: hideChatButton,
  openModal: openChatModal,
  closeModal: closeChatModal,
  clearHistory: clearConversationHistory,
  loadHistory: loadConversationHistoryFromServer,
  isLoggedIn: () => isLoggedIn,
  currentUser: () => currentUser,
  isProcessing: () => isProcessing,
};

console.log("💬 Chat.js 로드 완료 - Django API 모드");
