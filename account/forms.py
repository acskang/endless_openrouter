#account/forms.py
from django import forms
from .models import User
from django.core.exceptions import ValidationError

class UserLoginForm(forms.Form):
    """사용자 로그인 폼 - 이메일 또는 사용자명 지원"""
    email_or_username = forms.CharField(
        label='이메일 또는 사용자명',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '이메일 또는 사용자명을 입력하세요'
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요'
        })
    )
    remember_me = forms.BooleanField(
        label='로그인 상태 유지',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserSignupForm(forms.Form):
    """사용자 회원가입 폼"""
    username = forms.CharField(
        label='사용자명',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '사용자명을 입력하세요'
        })
    )
    email = forms.EmailField(
        label='이메일',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '이메일을 입력하세요'
        })
    )
    password = forms.CharField(
        label='비밀번호',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요 (최소 6자)'
        })
    )
    password_confirm = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 다시 입력하세요'
        })
    )

    def clean_username(self):
        """사용자명 중복 검사"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('이미 사용 중인 사용자명입니다.')
        return username

    def clean_email(self):
        """이메일 중복 검사"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('이미 사용 중인 이메일입니다.')
        return email

    def clean(self):
        """비밀번호 일치 검사"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('비밀번호가 일치하지 않습니다.')

        return cleaned_data