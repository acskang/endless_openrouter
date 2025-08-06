"""
개발 환경 설정
"""

import os
from .base import *
from dotenv import load_dotenv

# Read and set environment variables for Local Development
ENV_DIR = BASE_DIR.parent
DOTENV_PATH = os.path.join(ENV_DIR, ".env_local")
load_dotenv(dotenv_path=DOTENV_PATH)

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

DEBUG = os.getenv("DEBUG", "True")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

# Development-specific apps
INSTALLED_APPS += [
    "django_extensions",  # 유용한 개발 도구
]


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    # "default": {
    #     "ENGINE": "django.db.backends.mysql",
    #     "NAME": os.getenv("DB_NAME"),
    #     "USER": os.getenv("DB_USER"),
    #     "PASSWORD": os.getenv("DB_PASSWORD"),
    #     "HOST": os.getenv("DB_HOST", "localhost"),
    #     "PORT": os.getenv("DB_PORT", "3306"),
    #     "OPTIONS": {
    #         "charset": "utf8mb4",
    #         "collation": "utf8mb4_unicode_ci",
    #         "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    #         "isolation_level": "read committed",
    #         # 연결 풀 설정
    #         "connect_timeout": 60,
    #         "read_timeout": 60,
    #         "write_timeout": 60,
    #     },
    #     # 연결 풀링 설정
    #     "CONN_MAX_AGE": 600,  # 10분
    #     "CONN_HEALTH_CHECKS": True,
    # }
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경에서만!

# Static files
STATIC_ROOT = BASE_DIR / "staticfiles"


# 이메일 백엔드 설정 (개발용)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "cskang@thesysm.com"

# Logging
# from base
