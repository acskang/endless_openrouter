/* ===================================================================
   TheSysM 설정 파일
   Revolutionary AI-Collaborative Development
   =================================================================== */

// === 전역 설정 객체 ===
window.THESYSM_CONFIG = {
  // SVG 애니메이션 설정
  svg: {
    animationInterval: 20000, // 애니메이션 간격 (ms)
    animationDuration: 15000, // 애니메이션 지속시간 (ms)
    initialDelay: 3000, // 첫 애니메이션 딜레이 (ms)
    bouncyChance: 0.5, // 바운시 애니메이션 확률 (0.0 ~ 1.0)
    clickCooldown: 1000, // 클릭 후 쿨다운 (ms)
    enableHoverPause: true, // 호버 시 애니메이션 일시정지
  },

  // 말풍선 설정
  speechBubble: {
    enabled: true, // 말풍선 활성화/비활성화
    text: "Click Me!", // 기본 말풍선 텍스트
    randomMessages: true, // 랜덤 메시지 사용 여부
    showDelay: 1500, // 나타나는 딜레이 (ms)
    bounceStartDelay: 2000, // 바운스 시작 딜레이 (ms)
    pulseStartDelay: 4000, // 펄스 시작 딜레이 (ms)
    offsetY: 15, // SVG 위쪽 여백 (px)
    autoHide: true, // 애니메이션 종료 시 자동 숨김
  },

  // 네비게이션 설정
  navigation: {
    targetUrl: "/phrase/", // 클릭 시 이동할 URL
    celebrationDelay: 800, // 축하 메시지 후 이동 딜레이 (ms)
    celebrationMessage: "🎉 Navigating to Movie Search!",
    enableCelebration: true, // 축하 메시지 활성화/비활성화
    openInNewTab: false, // 새 탭에서 열기
  },

  // 반응형 설정
  responsive: {
    mobile: {
      maxWidth: 480, // 모바일 최대 너비 (px)
      svgSize: 60, // 모바일 SVG 크기 (px)
      bubbleFontSize: 11, // 모바일 말풍선 폰트 크기 (px)
      animationInterval: 15000, // 모바일 애니메이션 간격 (더 길게)
    },
    tablet: {
      maxWidth: 1024, // 태블릿 최대 너비 (px)
      svgSize: 80, // 태블릿 SVG 크기 (px)
      bubbleFontSize: 12, // 태블릿 말풍선 폰트 크기 (px)
      animationInterval: 13000, // 태블릿 애니메이션 간격
    },
    desktop: {
      svgSize: 100, // 데스크톱 SVG 크기 (px)
      bubbleFontSize: 14, // 데스크톱 말풍선 폰트 크기 (px)
      animationInterval: 10000, // 데스크톱 애니메이션 간격 (더 빠르게)
    },
  },

  // 접근성 설정
  accessibility: {
    enableKeyboardNavigation: true, // 키보드 네비게이션
    enableScreenReader: true, // 스크린 리더 지원
    reduceMotion: false, // 모션 감소 (사용자 설정 기반)
    highContrast: false, // 고대비 모드
  },

  // 성능 설정
  performance: {
    enableGPUAcceleration: true, // GPU 가속 사용
    limitFrameRate: false, // 프레임 레이트 제한
    maxFrameRate: 60, // 최대 프레임 레이트
    enableDebugMode: false, // 디버그 모드
  },

  // 사운드 설정 (미래 확장용)
  sound: {
    enabled: false, // 사운드 효과 활성화
    volume: 0.5, // 볼륨 (0.0 ~ 1.0)
    clickSound: "pop.mp3", // 클릭 사운드 파일
    hoverSound: "hover.mp3", // 호버 사운드 파일
  },
};

// === 다양한 말풍선 메시지 ===
window.SPEECH_MESSAGES = {
  korean: [
    "클릭하세요!",
    "영화 검색해보세요!",
    "영화를 찾아보세요!",
    "시작해볼까요!",
    "모험이 기다려요!",
    "여기를 클릭!",
    "영화 시간!",
    "탐험을 시작하세요!",
  ],
  english: [
    "Click Me!",
    "Try Movie Search!",
    "Discover Films!",
    "Let's Go!",
    "Adventure Awaits!",
    "Click Here!",
    "Movie Time!",
    "Start Exploring!",
  ],
  custom: [
    // 사용자 정의 메시지들을 여기에 추가
  ],
};

// === 테마 설정 ===
window.THESYSM_THEMES = {
  default: {
    primaryColor: "#a3a3ff",
    secondaryColor: "#8b8bff",
    backgroundColor: "#1a1a1a",
    textColor: "#ffffff",
  },
  dark: {
    primaryColor: "#6b73ff",
    secondaryColor: "#5a61ff",
    backgroundColor: "#0d1117",
    textColor: "#f0f6fc",
  },
  light: {
    primaryColor: "#5d67aa",
    secondaryColor: "#4c5899",
    backgroundColor: "#ffffff",
    textColor: "#24292f",
  },
};

// === 설정 변경 헬퍼 함수들 ===
window.TheSysMConfigHelper = {
  // 언어 변경
  setLanguage: function (lang) {
    if (window.SPEECH_MESSAGES[lang]) {
      window.THESYSM_CONFIG.speechBubble.currentLanguage = lang;
      console.log(`언어가 ${lang}로 변경되었습니다.`);
    }
  },

  // 말풍선 텍스트 변경
  updateSpeechBubbleText: function (newText) {
    window.THESYSM_CONFIG.speechBubble.text = newText;
    console.log(`말풍선 텍스트가 "${newText}"로 변경되었습니다.`);
  },

  // 네비게이션 URL 변경
  updateNavigationUrl: function (newUrl) {
    window.THESYSM_CONFIG.navigation.targetUrl = newUrl;
    console.log(`네비게이션 URL이 "${newUrl}"로 변경되었습니다.`);
  },

  // 애니메이션 간격 변경
  updateAnimationInterval: function (intervalMs) {
    window.THESYSM_CONFIG.svg.animationInterval = intervalMs;
    console.log(`애니메이션 간격이 ${intervalMs}ms로 변경되었습니다.`);
  },

  // 테마 변경
  setTheme: function (themeName) {
    if (window.THESYSM_THEMES[themeName]) {
      window.THESYSM_CONFIG.currentTheme = themeName;
      const theme = window.THESYSM_THEMES[themeName];

      // CSS 변수 업데이트
      document.documentElement.style.setProperty(
        "--primary-purple",
        theme.primaryColor
      );
      document.documentElement.style.setProperty(
        "--accent-purple",
        theme.secondaryColor
      );
      document.documentElement.style.setProperty(
        "--background-dark",
        theme.backgroundColor
      );
      document.documentElement.style.setProperty(
        "--text-white",
        theme.textColor
      );

      console.log(`테마가 "${themeName}"로 변경되었습니다.`);
    }
  },

  // 전체 설정 초기화
  resetConfig: function () {
    location.reload();
    console.log("설정이 기본값으로 초기화되었습니다.");
  },

  // 현재 설정 출력
  showCurrentConfig: function () {
    console.log("현재 TheSysM 설정:", window.THESYSM_CONFIG);
  },

  // 설정 내보내기 (JSON)
  exportConfig: function () {
    const config = JSON.stringify(window.THESYSM_CONFIG, null, 2);
    console.log("현재 설정 (복사해서 사용하세요):\n", config);
    return config;
  },

  // 설정 가져오기 (JSON)
  importConfig: function (configJson) {
    try {
      const newConfig = JSON.parse(configJson);
      Object.assign(window.THESYSM_CONFIG, newConfig);
      console.log("설정을 성공적으로 가져왔습니다.");
      return true;
    } catch (error) {
      console.error("설정 가져오기 실패:", error);
      return false;
    }
  },
};

// === 미리 정의된 설정 프리셋 ===
window.THESYSM_PRESETS = {
  // 기본 설정
  default: function () {
    window.TheSysMConfigHelper.updateAnimationInterval(13000);
    window.TheSysMConfigHelper.updateSpeechBubbleText("Click Me!");
    window.TheSysMConfigHelper.setLanguage("english");
  },

  // 한국어 설정
  korean: function () {
    window.TheSysMConfigHelper.setLanguage("korean");
    window.TheSysMConfigHelper.updateSpeechBubbleText("클릭하세요!");
    window.THESYSM_CONFIG.navigation.celebrationMessage =
      "🎉 영화 검색 페이지로 이동합니다!";
  },

  // 빠른 애니메이션
  fast: function () {
    window.TheSysMConfigHelper.updateAnimationInterval(8000);
    window.THESYSM_CONFIG.svg.animationDuration = 5000;
    window.THESYSM_CONFIG.svg.initialDelay = 1000;
  },

  // 느린 애니메이션
  slow: function () {
    window.TheSysMConfigHelper.updateAnimationInterval(20000);
    window.THESYSM_CONFIG.svg.animationDuration = 12000;
    window.THESYSM_CONFIG.svg.initialDelay = 5000;
  },

  // 접근성 모드
  accessibility: function () {
    window.THESYSM_CONFIG.accessibility.reduceMotion = true;
    window.THESYSM_CONFIG.accessibility.highContrast = true;
    window.THESYSM_CONFIG.svg.animationInterval = 30000; // 매우 느린 애니메이션
    window.THESYSM_CONFIG.speechBubble.enabled = true;
  },

  // 성능 모드 (저사양 기기용)
  performance: function () {
    window.THESYSM_CONFIG.performance.limitFrameRate = true;
    window.THESYSM_CONFIG.performance.maxFrameRate = 30;
    window.THESYSM_CONFIG.svg.bouncyChance = 0.2; // 바운시 애니메이션 줄임
    window.TheSysMConfigHelper.updateAnimationInterval(15000);
  },
};

// === 자동 설정 감지 ===
(function () {
  // 사용자의 모션 감소 설정 감지
  if (
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    window.THESYSM_CONFIG.accessibility.reduceMotion = true;
    console.log("모션 감소 설정이 감지되어 적용되었습니다.");
  }

  // 터치 기기 감지
  if ("ontouchstart" in window || navigator.maxTouchPoints > 0) {
    window.THESYSM_CONFIG.responsive.touchDevice = true;
    console.log("터치 기기가 감지되었습니다.");
  }
})();

// === 콘솔 도움말 ===
console.log(
  "%c🎨 TheSysM 커스터마이징 옵션이 로드되었습니다!",
  "color: #a3a3ff; font-size: 14px; font-weight: bold;"
);
console.log("%c사용법:", "color: #8b8bff; font-weight: bold;");
console.log("• TheSysMConfigHelper.showCurrentConfig() - 현재 설정 보기");
console.log('• TheSysMConfigHelper.setLanguage("korean") - 한국어로 변경');
console.log("• THESYSM_PRESETS.korean() - 한국어 프리셋 적용");
console.log("• THESYSM_PRESETS.fast() - 빠른 애니메이션 프리셋");
console.log('• TheSysMConfigHelper.setTheme("dark") - 다크 테마 적용');

// === FLOATING SVG ANIMATION (향상된 버전) ===
function initializeFloatingSvgAdvanced() {
  const floatingSvg = document.getElementById("floatingSvg");

  if (!floatingSvg) {
    console.warn("Floating SVG element not found");
    return;
  }

  let animationTimeout;
  let isAnimating = false;
  let speechBubble = null;
  let clickCooldown = false;

  // 랜덤 메시지 선택
  function getRandomMessage() {
    return SPEECH_MESSAGES[Math.floor(Math.random() * SPEECH_MESSAGES.length)];
  }

  // 디바이스 타입 감지
  function getDeviceType() {
    const width = window.innerWidth;
    if (width <= 480) return "mobile";
    if (width <= 1024) return "tablet";
    return "desktop";
  }

  // 반응형 크기 적용
  function applyResponsiveSettings() {
    const deviceType = getDeviceType();
    const settings = THESYSM_CONFIG.responsive[deviceType];

    floatingSvg.style.width = settings.svgSize + "px";
    floatingSvg.style.height = settings.svgSize + "px";

    if (speechBubble) {
      speechBubble.style.fontSize = settings.bubbleFontSize + "px";
    }
  }

  // 향상된 말풍선 생성
  function createAdvancedSpeechBubble() {
    if (speechBubble) {
      return speechBubble;
    }

    speechBubble = document.createElement("div");
    speechBubble.className = "speech-bubble";
    speechBubble.textContent = getRandomMessage();
    document.body.appendChild(speechBubble);

    // 반응형 설정 적용
    applyResponsiveSettings();

    return speechBubble;
  }

  // 말풍선 위치 업데이트
  function updateSpeechBubblePosition() {
    if (!speechBubble || !isAnimating) return;

    const svgRect = floatingSvg.getBoundingClientRect();
    const bubbleWidth = speechBubble.offsetWidth;
    const bubbleHeight = speechBubble.offsetHeight;

    speechBubble.style.left =
      svgRect.left + svgRect.width / 2 - bubbleWidth / 2 + "px";
    speechBubble.style.top =
      svgRect.top - bubbleHeight - THESYSM_CONFIG.speechBubble.offsetY + "px";
  }

  // 말풍선 표시 (향상된 버전)
  function showAdvancedSpeechBubble() {
    const bubble = createAdvancedSpeechBubble();
    updateSpeechBubblePosition();

    // 단계별 애니메이션
    setTimeout(() => {
      bubble.classList.add("show");
    }, THESYSM_CONFIG.speechBubble.showDelay);

    setTimeout(() => {
      bubble.classList.add("bounce");
    }, THESYSM_CONFIG.speechBubble.bounceStartDelay);

    setTimeout(() => {
      bubble.classList.remove("bounce");
      bubble.classList.add("pulse");
    }, THESYSM_CONFIG.speechBubble.pulseStartDelay);
  }

  // 말풍선 숨기기
  function hideSpeechBubble() {
    if (speechBubble) {
      speechBubble.classList.remove("show", "bounce", "pulse");
      setTimeout(() => {
        if (speechBubble && document.body.contains(speechBubble)) {
          document.body.removeChild(speechBubble);
          speechBubble = null;
        }
      }, 300);
    }
  }

  // 랜덤 Y 위치 계산
  function getRandomYPosition() {
    const minY = window.innerHeight * 0.1;
    const maxY = window.innerHeight * 0.9;
    return Math.random() * (maxY - minY) + minY;
  }

  // 향상된 애니메이션 시작
  function startAdvancedFloatingAnimation() {
    if (isAnimating) return;

    isAnimating = true;

    // 랜덤 Y 위치 설정
    const randomY = getRandomYPosition();
    floatingSvg.style.top = randomY + "px";

    // 애니메이션 타입 선택
    const isBouncy = Math.random() > 1 - THESYSM_CONFIG.svg.bouncyChance;
    floatingSvg.className = `floating-svg active ${isBouncy ? "bouncy" : ""}`;

    // 말풍선 표시
    showAdvancedSpeechBubble();

    // 위치 업데이트 간격
    const positionUpdateInterval = setInterval(() => {
      if (isAnimating) {
        updateSpeechBubblePosition();
      } else {
        clearInterval(positionUpdateInterval);
      }
    }, 50);

    // 애니메이션 종료
    animationTimeout = setTimeout(() => {
      isAnimating = false;
      floatingSvg.classList.remove("active", "bouncy");
      hideSpeechBubble();
      clearInterval(positionUpdateInterval);

      // 다음 애니메이션 예약
      setTimeout(() => {
        startAdvancedFloatingAnimation();
      }, THESYSM_CONFIG.svg.animationInterval - THESYSM_CONFIG.svg.animationDuration);
    }, THESYSM_CONFIG.svg.animationDuration);
  }

  // 향상된 클릭 핸들러
  function handleAdvancedClick() {
    if (clickCooldown) return;

    clickCooldown = true;
    setTimeout(() => {
      clickCooldown = false;
    }, THESYSM_CONFIG.svg.clickCooldown);

    if (isAnimating) {
      // 클릭 효과
      floatingSvg.style.transform += " scale(1.2)";
      setTimeout(() => {
        floatingSvg.style.transform = floatingSvg.style.transform.replace(
          " scale(1.2)",
          ""
        );
      }, 200);

      // 축하 메시지
      showToast(THESYSM_CONFIG.navigation.celebrationMessage, "success");

      // 페이지 이동
      setTimeout(() => {
        const currentHost = window.location.origin;
        window.location.href =
          currentHost + THESYSM_CONFIG.navigation.targetUrl;
      }, THESYSM_CONFIG.navigation.celebrationDelay);
    }
  }

  // 이벤트 리스너 등록
  floatingSvg.addEventListener("click", handleAdvancedClick);

  // 말풍선 클릭 이벤트 (이벤트 위임)
  document.addEventListener("click", (e) => {
    if (speechBubble && speechBubble.contains(e.target)) {
      handleAdvancedClick();
    }
  });

  // 반응형 이벤트
  window.addEventListener("resize", () => {
    if (!isAnimating) {
      const randomY = getRandomYPosition();
      floatingSvg.style.top = randomY + "px";
    } else {
      updateSpeechBubblePosition();
    }
    applyResponsiveSettings();
  });

  // 호버 이벤트
  floatingSvg.addEventListener("mouseenter", () => {
    if (isAnimating) {
      floatingSvg.style.animationPlayState = "paused";
      if (speechBubble) {
        speechBubble.style.animationPlayState = "paused";
      }
    }
  });

  floatingSvg.addEventListener("mouseleave", () => {
    if (isAnimating) {
      floatingSvg.style.animationPlayState = "running";
      if (speechBubble) {
        speechBubble.style.animationPlayState = "running";
      }
    }
  });

  // 초기 설정 적용
  applyResponsiveSettings();

  // 첫 애니메이션 시작
  setTimeout(() => {
    startAdvancedFloatingAnimation();
  }, THESYSM_CONFIG.svg.initialDelay);
}

// === 설정 변경 헬퍼 함수들 ===
function updateSpeechBubbleText(newText) {
  THESYSM_CONFIG.speechBubble.text = newText;
  SPEECH_MESSAGES[0] = newText; // 기본 메시지 업데이트
}

function updateNavigationUrl(newUrl) {
  THESYSM_CONFIG.navigation.targetUrl = newUrl;
}

function updateAnimationInterval(intervalMs) {
  THESYSM_CONFIG.svg.animationInterval = intervalMs;
}
