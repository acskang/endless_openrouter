// ===================================================================
// Enhanced Modals Control with Auto-Opening and Better UX
// ===================================================================

console.log("🔧 Enhanced modals.js 로드됨");

// 전역 모달 상태 관리
window.modalState = {
  currentModal: null,
  isAnimating: false,
  preventClose: false,
};

// 모달 초기화 함수
function resetModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) {
    console.error(`Modal with id '${modalId}' not found for reset`);
    return;
  }

  console.log(`🧹 모달 초기화: ${modalId}`);

  if (modalId === "loginModal") {
    // 로그인 모달 초기화
    const loginMessages = modal.querySelector("#loginMessages");
    const emailInput = modal.querySelector('input[name="email_or_username"]');
    const passwordInput = modal.querySelector('input[name="password"]');
    const submitButton = modal.querySelector('button[type="submit"]');

    // 메시지 영역 초기화
    if (loginMessages) {
      loginMessages.innerHTML = "";
      console.log("로그인 메시지 영역 초기화됨");
    }

    // 입력 필드 초기화
    if (emailInput) {
      emailInput.value = "";
      console.log("이메일/사용자명 입력 필드 초기화됨");
    }
    if (passwordInput) {
      passwordInput.value = "";
      console.log("비밀번호 입력 필드 초기화됨");
    }

    // 제출 버튼 초기화
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = "로그인";
      console.log("로그인 제출 버튼 초기화됨");
    }
  } else if (modalId === "signupModal") {
    // 회원가입 모달 초기화
    const signupMessages = modal.querySelector("#signupMessages");
    const usernameInput = modal.querySelector("#signupUsername");
    const emailInput = modal.querySelector("#signupEmail");
    const passwordInput = modal.querySelector("#signupPassword");
    const passwordConfirmInput = modal.querySelector("#signupPasswordConfirm");
    const submitButton = modal.querySelector('button[type="submit"]');

    // 메시지 영역 초기화
    if (signupMessages) {
      signupMessages.innerHTML = "";
      console.log("회원가입 메시지 영역 초기화됨");
    }

    // 입력 필드 초기화
    if (usernameInput) {
      usernameInput.value = "";
      console.log("사용자명 입력 필드 초기화됨");
    }
    if (emailInput) {
      emailInput.value = "";
      console.log("이메일 입력 필드 초기화됨");
    }
    if (passwordInput) {
      passwordInput.value = "";
      console.log("비밀번호 입력 필드 초기화됨");
    }
    if (passwordConfirmInput) {
      passwordConfirmInput.value = "";
      console.log("비밀번호 확인 입력 필드 초기화됨");
    }

    // 제출 버튼 초기화
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = "회원가입";
      console.log("회원가입 제출 버튼 초기화됨");
    }
  }

  // 모달 상태 초기화
  window.modalState.preventClose = false;

  console.log(`✅ 모달 초기화 완료: ${modalId}`);
}

// 모달 열기 - 개선된 버전 (초기화 포함)
function openModal(modalId) {
  console.log("🚀 모달 열기 시도:", modalId);

  if (window.modalState.isAnimating) {
    console.log("⏳ 모달 애니메이션 중이므로 대기...");
    setTimeout(() => openModal(modalId), 100);
    return;
  }

  const modal = document.getElementById(modalId);
  if (!modal) {
    console.error(`❌ Modal with id '${modalId}' not found`);
    return;
  }

  // 다른 모달이 열려있으면 먼저 닫기
  if (
    window.modalState.currentModal &&
    window.modalState.currentModal !== modalId
  ) {
    console.log("🔄 다른 모달 닫는 중:", window.modalState.currentModal);
    closeModal(window.modalState.currentModal);
  }

  // ⭐ 모달 초기화 (메시지와 입력값 클리어) - 가장 중요한 부분
  console.log("🧹 모달 초기화 실행");
  resetModal(modalId);

  window.modalState.isAnimating = true;
  window.modalState.currentModal = modalId;

  // 모달 표시
  modal.style.display = "block";
  document.body.style.overflow = "hidden";

  // 페이드인 효과를 위한 클래스 추가
  setTimeout(() => {
    modal.classList.add("modal-show");
    window.modalState.isAnimating = false;
  }, 10);

  // 포커스 관리 (초기화 후이므로 첫 번째 필드에 포커스)
  setTimeout(() => {
    setModalFocus(modalId);
  }, 100);

  console.log("✅ 모달 열기 완료:", modalId);
}

// 모달 닫기 - 개선된 버전
function closeModal(modalId) {
  console.log("🔒 모달 닫기:", modalId);

  if (window.modalState.preventClose) {
    console.log("🚫 모달 닫기가 일시적으로 방지됨");
    return;
  }

  const modal = document.getElementById(modalId);
  if (!modal || modal.style.display === "none") {
    return;
  }

  window.modalState.isAnimating = true;

  // 페이드아웃 효과
  modal.classList.remove("modal-show");

  setTimeout(() => {
    modal.style.display = "none";
    document.body.style.overflow = "auto";

    if (window.modalState.currentModal === modalId) {
      window.modalState.currentModal = null;
    }

    window.modalState.isAnimating = false;
    console.log("✅ 모달 닫기 완료:", modalId);
  }, 300);
}

// 모달 포커스 관리 (초기화 후에는 항상 첫 번째 필드)
function setModalFocus(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;

  let focusElement = null;

  if (modalId === "loginModal") {
    // 초기화 후에는 항상 첫 번째 입력 필드(이메일/사용자명)에 포커스
    focusElement = modal.querySelector('input[name="email_or_username"]');
  } else if (modalId === "signupModal") {
    // 회원가입 모달에서는 첫 번째 필드(사용자명)에 포커스
    focusElement = modal.querySelector("#signupUsername");
  }

  if (focusElement) {
    focusElement.focus();
    console.log("🎯 포커스 설정됨:", focusElement.name || focusElement.id);
  }
}

// 모든 모달 닫기
function closeAllModals() {
  const modals = ["loginModal", "signupModal"];
  modals.forEach((modalId) => {
    closeModal(modalId);
  });
}

// 모달 상태 확인
function isModalOpen() {
  return window.modalState.currentModal !== null;
}

// 현재 열린 모달 반환
function getCurrentModal() {
  return window.modalState.currentModal;
}

// 모달 외부 클릭 시 닫기
window.addEventListener("click", function (e) {
  const loginModal = document.getElementById("loginModal");
  const signupModal = document.getElementById("signupModal");

  // 정확히 모달 배경을 클릭했을 때만 닫기
  if (e.target === loginModal) {
    closeModal("loginModal");
  } else if (e.target === signupModal) {
    closeModal("signupModal");
  }
});

// ESC 키로 모달 닫기
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape" && isModalOpen()) {
    closeModal(getCurrentModal());
  }
});

// Tab 키 트래핑 (접근성 향상)
document.addEventListener("keydown", function (e) {
  if (e.key === "Tab" && isModalOpen()) {
    const modal = document.getElementById(getCurrentModal());
    if (modal) {
      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }
  }
});

// 폼 제출 전 검증
function validateSignupForm(formData) {
  const username = formData.get("username")?.trim();
  const email = formData.get("email")?.trim();
  const password = formData.get("password");
  const passwordConfirm = formData.get("password_confirm");

  if (!username || !email || !password || !passwordConfirm) {
    showToast("모든 필드를 입력해주세요.", "error");
    return false;
  }

  if (password !== passwordConfirm) {
    showToast("비밀번호가 일치하지 않습니다.", "error");
    document.getElementById("signupPasswordConfirm").focus();
    return false;
  }

  if (password.length < 6) {
    showToast("비밀번호는 최소 6자 이상이어야 합니다.", "error");
    document.getElementById("signupPassword").focus();
    return false;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showToast("올바른 이메일 주소를 입력해주세요.", "error");
    document.getElementById("signupEmail").focus();
    return false;
  }

  return true;
}

// 간단한 토스트 알림 함수
function showToast(message, type = "info", duration = 3000) {
  // 기존 토스트 제거
  const existingToast = document.querySelector(".custom-toast");
  if (existingToast) {
    existingToast.remove();
  }

  const toast = document.createElement("div");
  toast.className = `custom-toast custom-toast-${type}`;
  toast.textContent = message;

  // 스타일 설정
  Object.assign(toast.style, {
    position: "fixed",
    top: "20px",
    right: "20px",
    padding: "12px 20px",
    borderRadius: "4px",
    color: "white",
    fontSize: "14px",
    zIndex: "10000",
    opacity: "0",
    transition: "opacity 0.3s ease",
    maxWidth: "300px",
    wordWrap: "break-word",
  });

  // 타입별 색상 설정
  const colors = {
    success: "#28a745",
    error: "#dc3545",
    warning: "#ffc107",
    info: "#17a2b8",
  };

  toast.style.backgroundColor = colors[type] || colors.info;

  document.body.appendChild(toast);

  // 페이드인
  setTimeout(() => {
    toast.style.opacity = "1";
  }, 10);

  // 자동 제거
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, duration);
}

// 페이지 로드 완료 후 초기화
document.addEventListener("DOMContentLoaded", function () {
  console.log("🚀 Enhanced modals DOM 초기화 시작");

  // body overflow 초기화
  document.body.style.overflow = "auto";

  // 모든 모달 초기 상태 설정
  const modals = document.querySelectorAll(".modal");
  modals.forEach((modal) => {
    modal.style.display = "none";
    modal.classList.remove("modal-show");
  });

  // 테스트를 위한 전역 함수 추가
  window.testModalReset = function (modalId) {
    console.log(`🧪 테스트: ${modalId} 모달 초기화`);
    resetModal(modalId);
  };

  window.testModalOpen = function (modalId) {
    console.log(`🧪 테스트: ${modalId} 모달 열기`);
    openModal(modalId);
  };

  // 회원가입 폼 검증 이벤트 리스너
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", function (e) {
      console.log("회원가입 폼 제출 시도");

      const formData = new FormData(this);
      if (!validateSignupForm(formData)) {
        e.preventDefault();
        return false;
      }

      // 제출 중 모달 닫기 방지
      window.modalState.preventClose = true;

      // 제출 버튼 비활성화
      const submitButton = this.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "처리 중...";
      }

      console.log("회원가입 폼 제출 허용");
    });
  }

  // 로그인 폼에도 유사한 처리 추가
  const loginModal = document.getElementById("loginModal");
  if (loginModal) {
    const loginForm = loginModal.querySelector("form");
    if (loginForm) {
      loginForm.addEventListener("submit", function (e) {
        console.log("로그인 폼 제출 시도");

        const emailOrUsername = this.querySelector(
          'input[name="email_or_username"]'
        ).value.trim();
        const password = this.querySelector('input[name="password"]').value;

        if (!emailOrUsername || !password) {
          e.preventDefault();
          showToast("이메일/사용자명과 비밀번호를 입력해주세요.", "error");
          return false;
        }

        // 제출 중 모달 닫기 방지
        window.modalState.preventClose = true;

        // 제출 버튼 비활성화
        const submitButton = this.querySelector('button[type="submit"]');
        if (submitButton) {
          submitButton.disabled = true;
          submitButton.textContent = "로그인 중...";
        }

        console.log("로그인 폼 제출 허용");
      });
    }
  }

  console.log("✅ Enhanced modals 초기화 완료");
  console.log("🧪 테스트 함수 사용법:");
  console.log("  - testModalReset('loginModal') : 로그인 모달 초기화");
  console.log("  - testModalOpen('loginModal') : 로그인 모달 열기");
  console.log("  - resetModal('loginModal') : 직접 초기화");
});

// CSS 스타일을 동적으로 추가
const modalStyles = `
  .modal {
    transition: opacity 0.3s ease;
    opacity: 0;
  }
  
  .modal.modal-show {
    opacity: 1;
  }
  
  .modal-content {
    transform: translateY(-20px);
    transition: transform 0.3s ease;
  }
  
  .modal.modal-show .modal-content {
    transform: translateY(0);
  }
  
  .custom-toast {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
`;

// 스타일 추가
const styleSheet = document.createElement("style");
styleSheet.textContent = modalStyles;
document.head.appendChild(styleSheet);

// 전역 함수로 내보내기
window.openModal = openModal;
window.closeModal = closeModal;
window.closeAllModals = closeAllModals;
window.isModalOpen = isModalOpen;
window.getCurrentModal = getCurrentModal;
window.showToast = showToast;
window.resetModal = resetModal; // 모달 초기화 함수도 전역으로 내보내기
window.testModalReset = testModalReset;
window.testModalOpen = testModalOpen;

console.log("✅ Enhanced modals.js 로드 완료");
