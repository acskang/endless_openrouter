# account/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """확장된 사용자 모델 - 프로필 정보와 API 기능을 통합"""
    
    # 기본 사용자 정보
    email = models.EmailField(unique=True, verbose_name='이메일')
    nickname = models.CharField(max_length=30, blank=True, verbose_name='닉네임')
    bio = models.TextField(blank=True, verbose_name='자기소개')
    
    # 연락처 정보
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="전화번호는 '+999999999' 형식으로 입력해주세요. 최대 15자리까지 허용됩니다."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        verbose_name='전화번호'
    )
    
    # 프로필 정보
    profile_image = models.ImageField(
        upload_to='profile/%Y/%m/', 
        blank=True, 
        null=True, 
        verbose_name='프로필 이미지'
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='생년월일')
    
    # 계정 상태
    is_verified = models.BooleanField(default=False, verbose_name='인증된 사용자')
    is_premium = models.BooleanField(default=False, verbose_name='프리미엄 사용자')
    
    # API 관련 필드
    api_key = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        unique=True, 
        verbose_name='API 키'
    )
    api_calls_limit = models.IntegerField(default=1000, verbose_name='API 호출 제한')
    api_calls_count = models.IntegerField(default=0, verbose_name='API 호출 횟수')
    api_calls_reset_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name='API 호출 횟수 리셋 날짜'
    )
    
    # 시간 정보
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    last_api_call = models.DateTimeField(null=True, blank=True, verbose_name='마지막 API 호출')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['api_key']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def save(self, *args, **kwargs):
        # API 키가 없으면 자동 생성
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    def generate_api_key(self):
        """고유한 API 키 생성"""
        return f"ak_{uuid.uuid4().hex[:24]}"
    
    def reset_api_calls(self):
        """API 호출 횟수 리셋"""
        self.api_calls_count = 0
        self.api_calls_reset_date = timezone.now()
        self.save(update_fields=['api_calls_count', 'api_calls_reset_date'])
    
    def can_make_api_call(self):
        """API 호출 가능 여부 확인"""
        return self.api_calls_count < self.api_calls_limit
    
    def increment_api_calls(self):
        """API 호출 횟수 증가"""
        self.api_calls_count += 1
        self.last_api_call = timezone.now()
        self.save(update_fields=['api_calls_count', 'last_api_call'])
    
    @property
    def api_calls_remaining(self):
        """남은 API 호출 횟수"""
        return max(0, self.api_calls_limit - self.api_calls_count)
    
    @property
    def full_name(self):
        """전체 이름 (닉네임 우선, 없으면 username)"""
        return self.nickname or self.username