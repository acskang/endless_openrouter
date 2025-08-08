# chat/admin.py - 실제 모델에 맞춰 수정된 버전
from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .models import UserQuestion, AIResponse

# 커스텀 User 모델 가져오기
User = get_user_model()


class AIResponseInline(admin.TabularInline):
    """UserQuestion 상세페이지에서 AI 응답들을 인라인으로 표시"""

    model = AIResponse
    extra = 0
    readonly_fields = ["created_at", "response_time", "token_count"]
    fields = [
        "ai_model",
        "response_type",
        "content",
        "user_rating",
        "is_selected",
        "created_at",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


@admin.register(UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    """사용자 질문 Admin - 실제 모델 필드에 맞춤"""

    # ✅ 실제 모델 필드명 사용
    list_display = [
        "id",
        "get_user_info",
        "get_content_preview",
        "question_type",
        "get_response_count",
        "is_processed",
        "is_deleted",
        "created_at",
    ]

    list_filter = [
        "question_type",
        "is_processed",
        "is_deleted",
        "created_at",
        "user__is_premium",  # 커스텀 User 모델의 필드 활용
    ]

    search_fields = [
        "content",  # ✅ question이 아닌 content 필드
        "user__username",
        "user__email",
        "user__nickname",  # 커스텀 User 모델의 필드
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "get_user_info_detailed",
        "get_response_count",
        "get_latest_response_preview",
    ]

    fieldsets = (
        ("기본 정보", {"fields": ("user", "content", "question_type")}),
        ("첨부 파일", {"fields": ("attached_file",), "classes": ("collapse",)}),
        ("상태", {"fields": ("is_processed", "is_deleted")}),
        (
            "시간 정보",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        (
            "추가 정보",
            {
                "fields": (
                    "get_user_info_detailed",
                    "get_response_count",
                    "get_latest_response_preview",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [AIResponseInline]

    list_per_page = 25
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    # 액션들
    actions = ["mark_as_processed", "mark_as_unprocessed", "soft_delete", "restore"]

    def get_user_info(self, obj):
        """사용자 기본 정보 표시 (목록용)"""
        if not obj.user:
            return format_html('<span style="color: #999;">익명 사용자</span>')

        # 프리미엄 사용자 표시
        premium_badge = ""
        if hasattr(obj.user, "is_premium") and obj.user.is_premium:
            premium_badge = ' <span style="background: gold; color: black; padding: 2px 6px; border-radius: 10px; font-size: 10px;">PRO</span>'

        # 사용자 정보 구성
        display_name = obj.user.nickname or obj.user.username

        return format_html(
            "<strong>{}</strong>{}<br>"
            '<small style="color: #666;">ID: {} | {}</small>',
            display_name,
            premium_badge,
            obj.user.id,
            obj.user.email[:20] + "..." if len(obj.user.email) > 20 else obj.user.email,
        )

    get_user_info.short_description = "사용자"
    get_user_info.admin_order_field = "user__username"

    def get_user_info_detailed(self, obj):
        """사용자 상세 정보 (상세페이지용)"""
        if not obj.user:
            return "익명 사용자"

        user = obj.user
        info_parts = [
            f"<strong>사용자명:</strong> {user.username}",
            f"<strong>이메일:</strong> {user.email}",
        ]

        if hasattr(user, "nickname") and user.nickname:
            info_parts.append(f"<strong>닉네임:</strong> {user.nickname}")

        if hasattr(user, "is_premium"):
            info_parts.append(
                f"<strong>프리미엄:</strong> {'예' if user.is_premium else '아니오'}"
            )

        if hasattr(user, "api_calls_count"):
            info_parts.append(
                f"<strong>API 호출:</strong> {user.api_calls_count}/{user.api_calls_limit}"
            )

        info_parts.append(
            f"<strong>가입일:</strong> {user.date_joined.strftime('%Y-%m-%d %H:%M')}"
        )

        return format_html("<br>".join(info_parts))

    get_user_info_detailed.short_description = "사용자 상세 정보"

    def get_content_preview(self, obj):
        """질문 내용 미리보기"""
        if not obj.content:
            return format_html('<span style="color: #999;">내용 없음</span>')

        # 50자 미리보기
        preview = obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

        # 파일이 첨부된 경우 표시
        file_indicator = ""
        if obj.attached_file:
            file_indicator = " 📎"

        return format_html(
            '<span title="{}">{}{}</span>',
            obj.content,  # 전체 내용을 툴팁으로
            preview,
            file_indicator,
        )

    get_content_preview.short_description = "질문 내용"
    get_content_preview.admin_order_field = "content"

    def get_response_count(self, obj):
        """AI 응답 개수"""
        count = obj.response_count
        if count == 0:
            return format_html('<span style="color: #999;">0개</span>')
        else:
            return format_html(
                '<span style="color: #0066cc; font-weight: bold;">{}개</span>', count
            )

    get_response_count.short_description = "응답 수"

    def get_latest_response_preview(self, obj):
        """최근 응답 미리보기"""
        latest_response = obj.get_latest_response()
        if not latest_response:
            return "응답 없음"

        preview = (
            latest_response.content[:100] + "..."
            if len(latest_response.content) > 100
            else latest_response.content
        )

        return format_html(
            "<strong>{}:</strong><br>"
            '<span style="color: #666;">{}</span><br>'
            "<small>평점: {} | {}</small>",
            latest_response.ai_model,
            preview,
            latest_response.user_rating or "없음",
            latest_response.created_at.strftime("%m/%d %H:%M"),
        )

    get_latest_response_preview.short_description = "최근 응답"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("ai_responses")
        )

    # 커스텀 액션들
    @admin.action(description="선택된 질문을 처리됨으로 표시")
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f"{updated}개의 질문이 처리됨으로 표시되었습니다.")

    @admin.action(description="선택된 질문을 미처리로 표시")
    def mark_as_unprocessed(self, request, queryset):
        updated = queryset.update(is_processed=False)
        self.message_user(request, f"{updated}개의 질문이 미처리로 표시되었습니다.")

    @admin.action(description="선택된 질문을 소프트 삭제")
    def soft_delete(self, request, queryset):
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f"{updated}개의 질문이 삭제되었습니다.")

    @admin.action(description="선택된 질문을 복원")
    def restore(self, request, queryset):
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f"{updated}개의 질문이 복원되었습니다.")


@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    """AI 응답 Admin"""

    list_display = [
        "id",
        "get_question_preview",
        "ai_model",
        "response_type",
        "get_content_preview",
        "user_rating",
        "is_selected",
        "response_time",
        "created_at",
    ]

    list_filter = [
        "ai_model",
        "response_type",
        "user_rating",
        "is_selected",
        "is_deleted",
        "created_at",
    ]

    search_fields = [
        "content",
        "question__content",
        "question__user__username",
        "ai_model",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "response_order",
        "get_question_info",
    ]

    fieldsets = (
        ("기본 정보", {"fields": ("question", "ai_model", "response_type", "content")}),
        (
            "성능 지표",
            {
                "fields": ("response_time", "token_count", "response_order"),
                "classes": ("collapse",),
            },
        ),
        ("사용자 피드백", {"fields": ("user_rating", "user_feedback", "is_selected")}),
        ("상태", {"fields": ("is_deleted",)}),
        (
            "시간 정보",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
        ("관련 정보", {"fields": ("get_question_info",), "classes": ("collapse",)}),
    )

    list_per_page = 30
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    actions = ["mark_as_selected", "mark_as_unselected", "soft_delete", "restore"]

    def get_question_preview(self, obj):
        """관련 질문 미리보기"""
        if not obj.question:
            return "질문 없음"

        preview = (
            obj.question.content[:30] + "..."
            if len(obj.question.content) > 30
            else obj.question.content
        )
        user_name = obj.question.user.username if obj.question.user else "익명"

        return format_html(
            "<strong>{}:</strong><br>" '<span style="color: #666;">{}</span>',
            user_name,
            preview,
        )

    get_question_preview.short_description = "관련 질문"
    get_question_preview.admin_order_field = "question__created_at"

    def get_content_preview(self, obj):
        """응답 내용 미리보기"""
        if not obj.content:
            return "내용 없음"

        preview = obj.content[:60] + "..." if len(obj.content) > 60 else obj.content

        # 선택된 응답인 경우 하이라이트
        style = "background: #e8f5e8; padding: 2px;" if obj.is_selected else ""

        return format_html(
            '<span style="{}" title="{}">{}</span>',
            style,
            obj.content[:200],  # 툴팁용 더 긴 미리보기
            preview,
        )

    get_content_preview.short_description = "응답 내용"
    get_content_preview.admin_order_field = "content"

    def get_question_info(self, obj):
        """질문 상세 정보"""
        if not obj.question:
            return "질문 정보 없음"

        q = obj.question
        info_parts = [
            f"<strong>질문 ID:</strong> {q.id}",
            f"<strong>사용자:</strong> {q.user.username if q.user else '익명'}",
            f"<strong>질문 타입:</strong> {q.get_question_type_display()}",
            f"<strong>처리 상태:</strong> {'처리됨' if q.is_processed else '미처리'}",
            f"<strong>생성일:</strong> {q.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        return format_html("<br>".join(info_parts))

    get_question_info.short_description = "질문 정보"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return (
            super().get_queryset(request).select_related("question", "question__user")
        )

    # 커스텀 액션들
    @admin.action(description="선택된 응답을 대표 응답으로 설정")
    def mark_as_selected(self, request, queryset):
        count = 0
        for response in queryset:
            response.mark_as_selected()
            count += 1
        self.message_user(request, f"{count}개의 응답이 대표 응답으로 설정되었습니다.")

    @admin.action(description="선택된 응답의 대표 응답 해제")
    def mark_as_unselected(self, request, queryset):
        updated = queryset.update(is_selected=False)
        self.message_user(
            request, f"{updated}개의 응답이 대표 응답에서 해제되었습니다."
        )

    @admin.action(description="선택된 응답을 소프트 삭제")
    def soft_delete(self, request, queryset):
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f"{updated}개의 응답이 삭제되었습니다.")

    @admin.action(description="선택된 응답을 복원")
    def restore(self, request, queryset):
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f"{updated}개의 응답이 복원되었습니다.")


# ================================================================
# 🔧 Admin Site 커스터마이징
# ================================================================

# Admin 사이트 제목 설정
admin.site.site_header = "TheSysM 관리자"
admin.site.site_title = "TheSysM Admin"
admin.site.index_title = "환영합니다, TheSysM 관리자 페이지입니다"


# ================================================================
# 🚀 디버깅 및 진단 도구
# ================================================================


def debug_models():
    """모델 필드 확인용 함수"""
    print("🔍 UserQuestion 모델 필드:")
    for field in UserQuestion._meta.get_fields():
        print(f"  - {field.name}: {field.__class__.__name__}")

    print("\n🔍 AIResponse 모델 필드:")
    for field in AIResponse._meta.get_fields():
        print(f"  - {field.name}: {field.__class__.__name__}")

    print(f"\n🔍 User 모델: {User.__name__}")
    for field in User._meta.get_fields():
        if hasattr(field, "name"):
            print(f"  - {field.name}: {field.__class__.__name__}")


if __name__ == "__main__":
    debug_models()
