"""
Django 공통 설정
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "account",
    "chat",
    "phrase",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ASGI 설정
ASGI_APPLICATION = "project.asgi.application"
# WSGI 설정
WSGI_APPLICATION = "project.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "static_phrase",
]
STATIC_ROOT = STATIC_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = STATIC_DIR / "mediafiles"


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# 커스텀 사용자 모델 설정 추가
AUTH_USER_MODEL = "account.User"

# 로그인/로그아웃 후 리디렉션 URL
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}


# ===== 세션 설정 - 자동 로그아웃 =====

# 1. 브라우저 종료 시 세션 만료
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 2. 세션 타임아웃 (초단위) - 매우 짧게 설정
SESSION_COOKIE_AGE = 3600

# 3. 세션을 데이터베이스에 저장 (기본값이지만 명시)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# 4. 매 요청마다 세션 갱신하지 않음 (빠른 만료를 위해)
SESSION_SAVE_EVERY_REQUEST = True

# 5. 쿠키 설정
SESSION_COOKIE_HTTPONLY = True  # JavaScript로 쿠키 접근 불가
SESSION_COOKIE_SECURE = False  # HTTPS가 아닌 경우 False (개발환경)
SESSION_COOKIE_SAMESITE = "Lax"

# 세션 설정 강화
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # 데이터베이스에 세션 저장
SESSION_COOKIE_AGE = 86400  # 24시간 (초 단위)
SESSION_SAVE_EVERY_REQUEST = True  # 매 요청마다 세션 저장
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 브라우저 종료 시 세션 만료 (기본값)
SESSION_COOKIE_SECURE = False  # HTTPS에서만 쿠키 전송 (프로덕션에서는 True)
SESSION_COOKIE_HTTPONLY = True  # JavaScript에서 쿠키 접근 방지
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF 공격 방지

# 세션 쿠키 이름 (선택사항)
SESSION_COOKIE_NAME = "thesysm_sessionid"

# 세션 데이터 직렬화 방식
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"
# ===== 추가 보안 설정 =====

# CSRF 쿠키도 브라우저 종료 시 만료
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
CSRF_COOKIE_AGE = None  # 세션과 동일한 수명
# CSRF 설정 (보안 강화)
CSRF_COOKIE_SECURE = False  # 프로덕션에서는 True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_AGE = 86400  # 24시간

# 로깅 설정 - 자세한 디버그 정보 출력
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "channels": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "chat": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "daphne": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "api": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
