# chat/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings


class UserQuestion(models.Model):
    """사용자 질문 모델 (Parent Table)"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="사용자",
    )

    # 질문 내용
    content = models.TextField(verbose_name="질문 내용")

    # 질문 메타데이터
    question_type = models.CharField(
        max_length=20,
        choices=[
            ("text", "텍스트"),
            ("image", "이미지 포함"),
            ("file", "파일 포함"),
        ],
        default="text",
        verbose_name="질문 유형",
    )

    # 추가 파일 정보 (필요시)
    attached_file = models.FileField(
        upload_to="question_files/", null=True, blank=True, verbose_name="첨부 파일"
    )

    # 상태 정보
    is_processed = models.BooleanField(default=False, verbose_name="처리됨")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제됨")

    # 시간 정보
    created_at = models.DateTimeField(default=timezone.now, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "user_questions"
        verbose_name = "사용자 질문"
        verbose_name_plural = "사용자 질문들"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["is_processed"]),
        ]

    def __str__(self):
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"{self.user.username}: {content_preview}"

    @property
    def response_count(self):
        """이 질문에 대한 AI 응답 개수"""
        return self.ai_responses.filter(is_deleted=False).count()

    def get_latest_response(self):
        """가장 최근 AI 응답 가져오기"""
        return (
            self.ai_responses.filter(is_deleted=False).order_by("-created_at").first()
        )


class AIResponse(models.Model):
    """AI 응답 모델 (Child Table)"""

    question = models.ForeignKey(
        UserQuestion,
        on_delete=models.CASCADE,
        related_name="ai_responses",
        verbose_name="관련 질문",
    )

    # 응답 내용
    content = models.TextField(verbose_name="AI 응답 내용")

    # AI 모델 정보
    ai_model = models.CharField(
        max_length=50,
        verbose_name="AI 모델",
        help_text="예: gpt-4, claude-3, gemini-pro 등",
    )

    # 응답 메타데이터
    response_type = models.CharField(
        max_length=20,
        choices=[
            ("text", "텍스트"),
            ("code", "코드"),
            ("markdown", "마크다운"),
            ("json", "JSON"),
            ("error", "오류 응답"),
        ],
        default="text",
        verbose_name="응답 유형",
    )

    # 성능 및 품질 지표
    response_time = models.FloatField(
        null=True, blank=True, verbose_name="응답 시간(초)"
    )
    token_count = models.IntegerField(null=True, blank=True, verbose_name="토큰 수")

    # 사용자 피드백
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i}점") for i in range(1, 6)],
        verbose_name="사용자 평점 (1-5)",
    )
    user_feedback = models.TextField(blank=True, verbose_name="사용자 피드백")

    # 응답 순서 (같은 질문에 대한 여러 응답의 순서)
    response_order = models.PositiveIntegerField(default=1, verbose_name="응답 순서")

    # 상태 정보
    is_selected = models.BooleanField(
        default=False,
        verbose_name="선택된 응답",
        help_text="사용자가 선택한 최적의 응답인지 여부",
    )
    is_deleted = models.BooleanField(default=False, verbose_name="삭제됨")

    # 시간 정보
    created_at = models.DateTimeField(default=timezone.now, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "ai_responses"
        verbose_name = "AI 응답"
        verbose_name_plural = "AI 응답들"
        ordering = ["question", "response_order", "-created_at"]
        unique_together = ["question", "response_order"]
        indexes = [
            models.Index(fields=["question", "created_at"]),
            models.Index(fields=["ai_model", "created_at"]),
            models.Index(fields=["is_selected"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["response_order"]),
        ]

    def __str__(self):
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"{self.ai_model}({self.response_order}): {content_preview}"

    def save(self, *args, **kwargs):
        # 응답 순서 자동 설정
        if not self.response_order:
            last_response = (
                AIResponse.objects.filter(question=self.question)
                .order_by("-response_order")
                .first()
            )

            self.response_order = (
                (last_response.response_order + 1) if last_response else 1
            )

        super().save(*args, **kwargs)

        # 질문의 처리 상태 업데이트
        if self.question and not self.question.is_processed:
            self.question.is_processed = True
            self.question.save(update_fields=["is_processed"])

    def mark_as_selected(self):
        """이 응답을 선택된 응답으로 표시"""
        # 같은 질문의 다른 응답들의 선택 해제
        AIResponse.objects.filter(question=self.question, is_selected=True).update(
            is_selected=False
        )

        # 현재 응답을 선택으로 표시
        self.is_selected = True
        self.save(update_fields=["is_selected"])
