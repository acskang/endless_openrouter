# chat/views.py
import json
import os
import requests
import logging
import time
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from dotenv import load_dotenv

# 모델 import 추가
from chat.models import UserQuestion, AIResponse

# 로거 설정
logger = logging.getLogger(__name__)

# 환경에 따른 .env 파일 로드
# settings.DEBUG를 사용하여 환경 판단
if settings.DEBUG:
    env_file = ".env_local"
else:
    env_file = ".env_prod"

# BASE_DIR 또는 BASE_DIR.parent에서 .env 파일 찾기
env_paths = [
    os.path.join(settings.BASE_DIR, env_file),
    os.path.join(settings.BASE_DIR.parent, env_file),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), env_file),
]

env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
        env_loaded = True
        break

if not env_loaded:
    logger.warning(f"Environment file {env_file} not found in any of the paths")
    logger.warning(f"Attempted paths: {env_paths}")

# API 키 확인 및 디버깅
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    logger.info(f"API key loaded successfully (first 10 chars): {api_key[:10]}...")
else:
    logger.error("OPENROUTER_API_KEY not found in environment variables")
    logger.error(f"Current environment variables: {list(os.environ.keys())}")


@login_required
@require_http_methods(["GET"])
def chat_history_api(request):
    """
    사용자의 채팅 히스토리를 반환하는 API
    최근 대화부터 페이지네이션으로 제공
    """
    try:
        # 페이지네이션 파라미터
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 50))

        # 사용자의 질문들을 최신순으로 가져오기
        questions = (
            UserQuestion.objects.filter(user=request.user, is_deleted=False)
            .prefetch_related("ai_responses")
            .order_by("-created_at")
        )

        # 페이지네이션 적용
        paginator = Paginator(questions, page_size)
        page_questions = paginator.get_page(page)

        # 대화 히스토리 구성
        conversation_history = []

        for question in reversed(page_questions.object_list):  # 시간순으로 정렬
            # 사용자 질문 추가
            conversation_history.append(
                {
                    "role": "user",
                    "content": question.content,
                    "timestamp": question.created_at.isoformat(),
                    "question_id": question.id,
                }
            )

            # 해당 질문의 최신 AI 응답 추가
            latest_response = (
                question.ai_responses.filter(is_deleted=False)
                .order_by("-created_at")
                .first()
            )
            if latest_response:
                conversation_history.append(
                    {
                        "role": "assistant",
                        "content": latest_response.content,
                        "timestamp": latest_response.created_at.isoformat(),
                        "response_id": latest_response.id,
                        "ai_model": latest_response.ai_model,
                        "cached": True,
                    }
                )

        logger.info(
            f"Chat history loaded for user {request.user.username}: {len(conversation_history)} messages"
        )

        return JsonResponse(
            {
                "success": True,
                "history": conversation_history,
                "pagination": {
                    "current_page": page_questions.number,
                    "total_pages": paginator.num_pages,
                    "has_next": page_questions.has_next(),
                    "has_previous": page_questions.has_previous(),
                    "total_items": paginator.count,
                },
                "timestamp": timezone.now().isoformat(),
            }
        )

    except ValueError as e:
        logger.error(f"Invalid pagination parameters: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "잘못된 페이지 파라미터입니다."}, status=400
        )

    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}", exc_info=True)
        return JsonResponse(
            {"success": False, "error": "채팅 히스토리 로드 중 오류가 발생했습니다."},
            status=500,
        )


@login_required
@require_http_methods(["POST"])
def chat_api(request):
    """
    OpenRouter API를 통해 AI 응답을 생성하는 뷰
    클라이언트에서 메시지를 받아 OpenRouter API로 전달하고 응답을 반환
    UserQuestion과 AIResponse 모델에 데이터 저장
    """
    try:
        # 요청 본문 파싱
        body = json.loads(request.body.decode("utf-8"))
        user_message = body.get("message", "").strip()
        conversation_history = body.get("history", [])

        # 메시지 검증
        if not user_message:
            return JsonResponse(
                {"success": False, "error": "메시지가 비어있습니다."}, status=400
            )

        # 메시지 길이 제한
        if len(user_message) > 2000:
            return JsonResponse(
                {
                    "success": False,
                    "error": "메시지가 너무 깁니다. 2000자 이내로 입력해주세요.",
                },
                status=400,
            )

        # API 호출 제한 확인 (사용자 모델에 해당 메서드가 있는 경우)
        if (
            hasattr(request.user, "can_make_api_call")
            and not request.user.can_make_api_call()
        ):
            return JsonResponse(
                {
                    "success": False,
                    "error": "API 호출 제한에 도달했습니다. 제한이 리셋될 때까지 기다려주세요.",
                },
                status=429,
            )

        # 1. 사용자 질문을 데이터베이스에 저장 (기존 질문 확인)
        user_question = get_or_create_user_question(request.user, user_message)

        # 2. 기존 AI 응답이 있는지 확인
        existing_response = get_latest_ai_response(user_question)

        if existing_response:
            # 기존 응답이 있으면 바로 반환 (API 호출 없음)
            logger.info(f"Used cached AI response: {existing_response.id}")
            return JsonResponse(
                {
                    "success": True,
                    "message": existing_response.content,
                    "timestamp": existing_response.created_at.isoformat(),
                    "cached": True,
                    "ai_model": existing_response.ai_model,
                    "response_id": existing_response.id,
                }
            )

        # 3. API 호출 횟수 증가 (사용자 모델에 해당 메서드가 있는 경우)
        if hasattr(request.user, "increment_api_calls"):
            request.user.increment_api_calls()

        # 환경 변수에서 API 키 가져오기
        api_key = os.getenv("OPENROUTER_API_KEY")

        # API 키가 없으면 하드코딩된 키 사용 (임시 - 프로덕션에서는 제거)
        if not api_key:
            # 개발 중 임시로 사용 - 프로덕션에서는 반드시 환경 변수 사용
            api_key = "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"
            logger.warning(
                "Using hardcoded API key - this should be fixed in production!"
            )

        if not api_key:
            logger.error("OPENROUTER_API_KEY not found")
            return JsonResponse(
                {
                    "success": False,
                    "error": "API 키가 설정되지 않았습니다. 관리자에게 문의하세요.",
                },
                status=500,
            )

        # 4. OpenRouter API 호출
        start_time = time.time()
        api_response = call_openrouter_api(
            api_key=api_key,
            user_message=user_message,
            conversation_history=conversation_history,
            request=request,
        )
        response_time = time.time() - start_time

        if api_response["success"]:
            # 5. AI 응답을 데이터베이스에 저장
            ai_response = save_ai_response(
                user_question=user_question,
                content=api_response["message"],
                ai_model="openai/gpt-3.5-turbo",
                response_time=response_time,
            )

            logger.info(f"Generated and saved new AI response: {ai_response.id}")

            # 성공 응답
            return JsonResponse(
                {
                    "success": True,
                    "message": api_response["message"],
                    "timestamp": ai_response.created_at.isoformat(),
                    "cached": False,
                    "ai_model": ai_response.ai_model,
                    "response_id": ai_response.id,
                    "response_time": round(response_time, 2),
                }
            )
        else:
            # API 호출 실패
            return JsonResponse(
                {"success": False, "error": api_response["error"]},
                status=api_response.get("status", 500),
            )

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse(
            {"success": False, "error": "잘못된 요청 형식입니다."}, status=400
        )

    except Exception as e:
        logger.error(f"Unexpected error in chat_api: {str(e)}", exc_info=True)
        return JsonResponse(
            {"success": False, "error": "서버 오류가 발생했습니다."}, status=500
        )


# 헬퍼 함수: 사용자 질문 가져오기 또는 생성
def get_or_create_user_question(user, content):
    """동일한 질문이 있는지 확인하고 UserQuestion 가져오기 또는 생성"""
    try:
        # 동일한 내용의 질문이 이미 있는지 확인 (대소문자 구분 없이, 공백 제거 후 비교)
        existing_question = UserQuestion.objects.filter(
            user=user,
            content__iexact=content.strip(),  # 대소문자 구분 없이 정확히 일치
            is_deleted=False,
        ).first()

        if existing_question:
            logger.info(f"Found existing question: {existing_question.id}")
            return existing_question

        # 새 질문 생성
        question = UserQuestion.objects.create(
            user=user, content=content.strip(), question_type="text"
        )
        logger.info(f"Created new question: {question.id}")
        return question

    except Exception as e:
        logger.error(f"Error getting/creating user question: {str(e)}")
        raise


# 헬퍼 함수: 최신 AI 응답 가져오기
def get_latest_ai_response(user_question):
    """해당 질문에 대한 최신 AI 응답 가져오기"""
    try:
        return (
            user_question.ai_responses.filter(is_deleted=False)
            .order_by("-created_at")
            .first()
        )
    except Exception as e:
        logger.error(f"Error getting latest AI response: {str(e)}")
        return None


# 헬퍼 함수: AI 응답을 데이터베이스에 저장
def save_ai_response(user_question, content, ai_model, response_time):
    """AI 응답을 데이터베이스에 저장"""
    try:
        # 동일한 내용의 AI 응답이 이미 있는지 확인
        existing_response = AIResponse.objects.filter(
            question=user_question,
            content__iexact=content.strip(),  # 대소문자 구분 없이 정확히 일치
            is_deleted=False,
        ).first()

        if existing_response:
            logger.info(f"Found existing AI response: {existing_response.id}")
            return existing_response

        # 새 AI 응답 생성
        ai_response = AIResponse.objects.create(
            question=user_question,
            content=content.strip(),
            ai_model=ai_model,
            response_time=response_time,
            response_type="text",
        )
        logger.info(f"Created new AI response: {ai_response.id}")
        return ai_response

    except Exception as e:
        logger.error(f"Error saving AI response: {str(e)}")
        raise


# 헬퍼 함수: OpenRouter API 호출
def call_openrouter_api(api_key, user_message, conversation_history, request):
    """
    OpenRouter API를 호출하는 헬퍼 함수
    """
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        # 메시지 구성
        messages = [
            {
                "role": "system",
                "content": "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 친절하고 정확하게 답변해주세요. 한국어로 답변해주세요.",
            }
        ]

        # 대화 기록 추가 (최근 10개만)
        for msg in conversation_history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # role 검증
            if role in ["user", "assistant"]:
                messages.append({"role": role, "content": content[:2000]})

        # 현재 메시지 추가
        messages.append({"role": "user", "content": user_message})

        # API 요청 헤더
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": request.META.get(
                "HTTP_REFERER", request.build_absolute_uri("/")
            ),
            "X-Title": "Django Chat App",
        }

        # API 요청 본문
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
        }

        logger.info(f"Calling OpenRouter API for user {request.user.username}")

        # API 호출
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        # 응답 처리
        if response.status_code == 200:
            result = response.json()

            if result.get("choices") and len(result["choices"]) > 0:
                ai_message = result["choices"][0]["message"]["content"]

                logger.info(
                    f"Successfully generated AI response for user {request.user.username}"
                )

                return {"success": True, "message": ai_message.strip()}
            else:
                logger.error(f"Unexpected API response format: {result}")
                return {
                    "success": False,
                    "error": "AI 응답 형식이 올바르지 않습니다.",
                    "status": 500,
                }

        elif response.status_code == 429:
            logger.warning(f"Rate limit exceeded for user {request.user.username}")
            return {
                "success": False,
                "error": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                "status": 429,
            }

        elif response.status_code == 401:
            logger.error(f"API authentication failed. Status: {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return {
                "success": False,
                "error": "API 인증에 실패했습니다. API 키를 확인해주세요.",
                "status": 401,
            }

        else:
            logger.error(
                f"OpenRouter API error: {response.status_code} - {response.text[:200]}"
            )
            return {
                "success": False,
                "error": f"AI 서비스 오류가 발생했습니다. (코드: {response.status_code})",
                "status": response.status_code,
            }

    except requests.exceptions.Timeout:
        logger.error("OpenRouter API timeout")
        return {
            "success": False,
            "error": "AI 서비스 응답 시간이 초과되었습니다.",
            "status": 504,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        return {
            "success": False,
            "error": "네트워크 오류가 발생했습니다.",
            "status": 503,
        }

    except Exception as e:
        logger.error(
            f"Unexpected error in call_openrouter_api: {str(e)}", exc_info=True
        )
        return {
            "success": False,
            "error": "AI 서비스 호출 중 오류가 발생했습니다.",
            "status": 500,
        }
