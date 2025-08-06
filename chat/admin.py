# chat/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserQuestion, AIResponse


class AIResponseInline(admin.TabularInline):
    """UserQuestion 상세 페이지에서 AI 응답들을 인라인으로 표시"""

    model = AIResponse
    extra = 0
    readonly_fields = [
        "response_order",
        "response_time",
        "token_count",
        "created_at",
        "updated_at",
    ]
    fields = [
        "content",
        "ai_model",
        "response_type",
        "response_order",
        "response_time",
        "token_count",
        "user_rating",
        "user_feedback",
        "is_selected",
        "is_deleted",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


@admin.register(UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user_link",
        "content_preview",
        "question_type",
        "response_count",
        "is_processed",
        "is_deleted",
        "created_at",
    ]

    list_filter = [
        "question_type",
        "is_processed",
        "is_deleted",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "content",
        "user__username",
        "user__email",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "response_count",
    ]

    fieldsets = (
        ("기본 정보", {"fields": ("user", "content", "question_type")}),
        (
            "첨부 파일",
            {
                "fields": ("attached_file",),
                "classes": ("collapse",),
            },
        ),
        ("상태 정보", {"fields": ("is_processed", "is_deleted")}),
        (
            "시간 정보",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "통계",
            {
                "fields": ("response_count",),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [AIResponseInline]

    actions = ["mark_as_processed", "mark_as_unprocessed", "soft_delete", "restore"]

    def user_link(self, obj):
        """사용자 링크"""
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"

    user_link.short_description = "사용자"
    user_link.admin_order_field = "user__username"

    def content_preview(self, obj):
        """질문 내용 미리보기"""
        content = obj.content
        if len(content) > 100:
            return content[:100] + "..."
        return content

    content_preview.short_description = "질문 내용"
    content_preview.admin_order_field = "content"

    def get_queryset(self, request):
        """삭제되지 않은 질문만 기본 표시"""
        return super().get_queryset(request).select_related("user")

    # 커스텀 액션들
    def mark_as_processed(self, request, queryset):
        """선택된 질문들을 처리됨으로 표시"""
        updated = queryset.update(is_processed=True)
        self.message_user(request, f"{updated}개의 질문이 처리됨으로 표시되었습니다.")

    mark_as_processed.short_description = "선택된 질문을 처리됨으로 표시"

    def mark_as_unprocessed(self, request, queryset):
        """선택된 질문들을 미처리로 표시"""
        updated = queryset.update(is_processed=False)
        self.message_user(request, f"{updated}개의 질문이 미처리로 표시되었습니다.")

    mark_as_unprocessed.short_description = "선택된 질문을 미처리로 표시"

    def soft_delete(self, request, queryset):
        """선택된 질문들을 소프트 삭제"""
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f"{updated}개의 질문이 삭제되었습니다.")

    soft_delete.short_description = "선택된 질문 삭제"

    def restore(self, request, queryset):
        """선택된 질문들을 복원"""
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f"{updated}개의 질문이 복원되었습니다.")

    restore.short_description = "선택된 질문 복원"


@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "question_link",
        "user_name",
        "content_preview",
        "ai_model",
        "response_type",
        "response_order",
        "user_rating",
        "response_time",
        "is_selected",
        "is_deleted",
        "created_at",
    ]

    list_filter = [
        "ai_model",
        "response_type",
        "user_rating",
        "is_selected",
        "is_deleted",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "content",
        "question__content",
        "question__user__username",
        "ai_model",
        "user_feedback",
    ]

    readonly_fields = [
        "response_order",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("관련 질문", {"fields": ("question",)}),
        ("응답 내용", {"fields": ("content", "response_type")}),
        ("AI 모델 정보", {"fields": ("ai_model", "response_time", "token_count")}),
        (
            "사용자 피드백",
            {
                "fields": ("user_rating", "user_feedback"),
                "classes": ("collapse",),
            },
        ),
        (
            "메타데이터",
            {
                "fields": ("response_order", "is_selected"),
            },
        ),
        ("상태 정보", {"fields": ("is_deleted",)}),
        (
            "시간 정보",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["mark_as_selected", "mark_as_unselected", "soft_delete", "restore"]

    def question_link(self, obj):
        """관련 질문 링크"""
        if obj.question:
            url = reverse("admin:chat_userquestion_change", args=[obj.question.id])
            content_preview = obj.question.content[:50]
            if len(obj.question.content) > 50:
                content_preview += "..."
            return format_html('<a href="{}">{}</a>', url, content_preview)
        return "-"

    question_link.short_description = "관련 질문"
    question_link.admin_order_field = "question__content"

    def user_name(self, obj):
        """질문한 사용자 이름"""
        if obj.question and obj.question.user:
            return obj.question.user.username
        return "-"

    user_name.short_description = "사용자"
    user_name.admin_order_field = "question__user__username"

    def content_preview(self, obj):
        """응답 내용 미리보기"""
        content = obj.content
        if len(content) > 100:
            return content[:100] + "..."
        return content

    content_preview.short_description = "AI 응답 내용"
    content_preview.admin_order_field = "content"

    def response_time(self, obj):
        """응답 시간 포맷팅"""
        if obj.response_time:
            return f"{obj.response_time:.2f}초"
        return "-"

    response_time.short_description = "응답 시간"
    response_time.admin_order_field = "response_time"

    def get_queryset(self, request):
        """관련 객체들을 미리 로드"""
        return (
            super().get_queryset(request).select_related("question", "question__user")
        )

    # 커스텀 액션들
    def mark_as_selected(self, request, queryset):
        """선택된 응답들을 선택됨으로 표시"""
        for response in queryset:
            response.mark_as_selected()
        count = queryset.count()
        self.message_user(request, f"{count}개의 응답이 선택됨으로 표시되었습니다.")

    mark_as_selected.short_description = "선택된 응답을 선택됨으로 표시"

    def mark_as_unselected(self, request, queryset):
        """선택된 응답들을 미선택으로 표시"""
        updated = queryset.update(is_selected=False)
        self.message_user(request, f"{updated}개의 응답이 미선택으로 표시되었습니다.")

    mark_as_unselected.short_description = "선택된 응답을 미선택으로 표시"

    def soft_delete(self, request, queryset):
        """선택된 응답들을 소프트 삭제"""
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f"{updated}개의 응답이 삭제되었습니다.")

    soft_delete.short_description = "선택된 응답 삭제"

    def restore(self, request, queryset):
        """선택된 응답들을 복원"""
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f"{updated}개의 응답이 복원되었습니다.")

    restore.short_description = "선택된 응답 복원"


# 추가적인 관리자 기능들
admin.site.site_header = "Chat App 관리자"
admin.site.site_title = "Chat App"
admin.site.index_title = "Chat App 관리"
