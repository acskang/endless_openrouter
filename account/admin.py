# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """확장된 사용자 관리자"""

    # 목록 페이지 설정
    list_display = [
        "username",
        "email",
        "full_name_display",
        "is_verified",
        "is_premium",
        "api_calls_status",
        "last_login_display",
        "is_active",
        "is_staff",
        "created_at",
    ]

    list_filter = [
        "is_verified",
        "is_premium",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "last_login",
        "last_api_call",
    ]

    search_fields = [
        "username",
        "email",
        "nickname",
        "first_name",
        "last_name",
        "api_key",
        "phone",
    ]

    ordering = ["-created_at"]

    # 상세 페이지 필드셋 설정
    fieldsets = (
        ("기본 정보", {"fields": ("username", "email", "password")}),
        (
            "개인 정보",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "nickname",
                    "bio",
                    "phone",
                    "birth_date",
                    "profile_image",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "계정 상태",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "is_premium",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "API 설정",
            {
                "fields": (
                    "api_key",
                    "api_calls_limit",
                    "api_calls_count",
                    "api_calls_reset_date",
                    "last_api_call",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "권한",
            {
                "fields": ("groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        (
            "중요한 날짜",
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # 사용자 추가 시 필드셋
    add_fieldsets = (
        (
            "필수 정보",
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
        (
            "선택 정보",
            {
                "classes": ("wide", "collapse"),
                "fields": ("first_name", "last_name", "nickname"),
            },
        ),
    )

    readonly_fields = [
        "created_at",
        "updated_at",
        "date_joined",
        "last_login",
        "last_api_call",
        "api_calls_reset_date",
    ]

    actions = [
        "verify_users",
        "unverify_users",
        "make_premium",
        "remove_premium",
        "reset_api_calls",
        "regenerate_api_keys",
        "deactivate_users",
        "activate_users",
    ]

    # 커스텀 필드 디스플레이 메서드들
    def full_name_display(self, obj):
        """전체 이름 표시"""
        if obj.nickname:
            return f"{obj.nickname} ({obj.get_full_name()})"
        return obj.get_full_name() or "-"

    full_name_display.short_description = "이름/닉네임"
    full_name_display.admin_order_field = "nickname"

    def api_calls_status(self, obj):
        """API 호출 상태 표시"""
        remaining = obj.api_calls_remaining
        total = obj.api_calls_limit
        used = obj.api_calls_count

        # 사용률에 따른 색상 결정
        usage_percent = (used / total) * 100 if total > 0 else 0

        if usage_percent >= 90:
            color = "red"
        elif usage_percent >= 70:
            color = "orange"
        else:
            color = "green"

        return format_html(
            '<span style="color: {};">{}/{}</span><br><small>{}개 남음</small>',
            color,
            used,
            total,
            remaining,
        )

    api_calls_status.short_description = "API 호출 상태"
    api_calls_status.admin_order_field = "api_calls_count"

    def last_login_display(self, obj):
        """마지막 로그인 시간 표시"""
        if obj.last_login:
            # 현재 시간과의 차이 계산
            now = timezone.now()
            diff = now - obj.last_login

            if diff.days > 30:
                color = "red"
                text = f"{diff.days}일 전"
            elif diff.days > 7:
                color = "orange"
                text = f"{diff.days}일 전"
            elif diff.days > 0:
                color = "blue"
                text = f"{diff.days}일 전"
            else:
                color = "green"
                hours = diff.seconds // 3600
                if hours > 0:
                    text = f"{hours}시간 전"
                else:
                    minutes = diff.seconds // 60
                    text = f"{minutes}분 전"

            return format_html('<span style="color: {};">{}</span>', color, text)
        return format_html('<span style="color: gray;">없음</span>')

    last_login_display.short_description = "마지막 로그인"
    last_login_display.admin_order_field = "last_login"

    # 커스텀 액션들
    def verify_users(self, request, queryset):
        """선택된 사용자들을 인증된 사용자로 표시"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated}명의 사용자가 인증되었습니다.")

    verify_users.short_description = "선택된 사용자를 인증된 사용자로 표시"

    def unverify_users(self, request, queryset):
        """선택된 사용자들의 인증을 해제"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated}명의 사용자 인증이 해제되었습니다.")

    unverify_users.short_description = "선택된 사용자의 인증 해제"

    def make_premium(self, request, queryset):
        """선택된 사용자들을 프리미엄 사용자로 설정"""
        updated = queryset.update(is_premium=True, api_calls_limit=10000)
        self.message_user(
            request, f"{updated}명의 사용자가 프리미엄으로 업그레이드되었습니다."
        )

    make_premium.short_description = "선택된 사용자를 프리미엄으로 업그레이드"

    def remove_premium(self, request, queryset):
        """선택된 사용자들의 프리미엄 상태를 해제"""
        updated = queryset.update(is_premium=False, api_calls_limit=1000)
        self.message_user(
            request, f"{updated}명의 사용자가 일반 사용자로 변경되었습니다."
        )

    remove_premium.short_description = "선택된 사용자의 프리미엄 상태 해제"

    def reset_api_calls(self, request, queryset):
        """선택된 사용자들의 API 호출 횟수 리셋"""
        count = 0
        for user in queryset:
            user.reset_api_calls()
            count += 1
        self.message_user(
            request, f"{count}명의 사용자 API 호출 횟수가 리셋되었습니다."
        )

    reset_api_calls.short_description = "선택된 사용자의 API 호출 횟수 리셋"

    def regenerate_api_keys(self, request, queryset):
        """선택된 사용자들의 API 키 재생성"""
        count = 0
        for user in queryset:
            user.api_key = user.generate_api_key()
            user.save(update_fields=["api_key"])
            count += 1
        self.message_user(request, f"{count}명의 사용자 API 키가 재생성되었습니다.")

    regenerate_api_keys.short_description = "선택된 사용자의 API 키 재생성"

    def deactivate_users(self, request, queryset):
        """선택된 사용자들을 비활성화"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated}명의 사용자가 비활성화되었습니다.")

    deactivate_users.short_description = "선택된 사용자 비활성화"

    def activate_users(self, request, queryset):
        """선택된 사용자들을 활성화"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated}명의 사용자가 활성화되었습니다.")

    activate_users.short_description = "선택된 사용자 활성화"

    # 추가 메서드들
    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request)

    def has_delete_permission(self, request, obj=None):
        """삭제 권한 제한 (슈퍼유저만 가능)"""
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        """모델 저장 시 추가 처리"""
        # 새 사용자인 경우 API 키 자동 생성
        if not change and not obj.api_key:
            obj.api_key = obj.generate_api_key()
        super().save_model(request, obj, form, change)


# 사용자 통계를 위한 추가 관리 뷰 (선택사항)
class UserStatistics:
    """사용자 통계 정보"""

    @staticmethod
    def get_user_stats():
        """사용자 통계 반환"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        premium_users = User.objects.filter(is_premium=True).count()

        # 최근 30일 내 가입한 사용자
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_users = User.objects.filter(created_at__gte=thirty_days_ago).count()

        # 최근 7일 내 로그인한 사용자
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_login_users = User.objects.filter(last_login__gte=seven_days_ago).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "premium_users": premium_users,
            "recent_users": recent_users,
            "recent_login_users": recent_login_users,
        }


# Admin 사이트 커스터마이징
admin.site.site_header = "사용자 관리 시스템"
admin.site.site_title = "User Admin"
admin.site.index_title = "사용자 및 계정 관리"
