import json
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
import logging
import time
from django.conf import settings

# 새로운 모델 import
from chat.models import UserQuestion, AIResponse

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """WebSocket 연결 처리"""
        # 초기화
        self.room_group_name = None

        try:
            # scope에서 사용자 정보 가져오기
            self.user = self.scope.get("user")
            logger.info(
                f"WebSocket connection attempt. User: {self.user}, Authenticated: {getattr(self.user, 'is_authenticated', False)}"
            )

            # 사용자 인증 확인 (더 엄격한 체크)
            if (
                not self.user
                or not hasattr(self.user, "is_authenticated")
                or not self.user.is_authenticated
            ):
                logger.warning(f"Unauthenticated connection attempt. User: {self.user}")
                await self.close(code=4001)  # 인증 오류 코드
                return

            # 간단한 room name 설정
            self.room_group_name = f"user_{self.user.id}"

            # WebSocket 연결 수락 (그룹 추가 전에 수락)
            await self.accept()

            # 채널 레이어 그룹에 추가
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            # 연결 성공 메시지 전송
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "connection_established",
                        "message": "WebSocket 연결이 성공적으로 설정되었습니다!",
                        "timestamp": timezone.now().isoformat(),
                        "user_id": self.user.id,
                    }
                )
            )

            logger.info(
                f"WebSocket connection established successfully for user {self.user.username}"
            )

        except Exception as e:
            logger.error(f"Critical error in connect: {str(e)}", exc_info=True)
            # 에러 발생 시 안전하게 연결 종료
            try:
                await self.close(code=4000)  # 일반 오류 코드
            except Exception as close_error:
                logger.error(f"Error closing connection: {str(close_error)}")

    async def disconnect(self, close_code):
        """WebSocket 연결 해제 처리"""
        try:
            logger.info(f"WebSocket disconnecting with code: {close_code}")

            # room_group_name이 설정되어 있을 때만 그룹에서 제거
            if hasattr(self, "room_group_name") and self.room_group_name:
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )
                logger.info(f"Removed from group: {self.room_group_name}")
            else:
                logger.info("No room group to remove from")

        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}", exc_info=True)

    async def receive(self, text_data):
        """클라이언트로부터 메시지 수신"""
        try:
            logger.info(f"Received data: {text_data}")

            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "message":
                user_message = data.get("message", "").strip()

                if not user_message:
                    await self.send_error("메시지가 비어있습니다.")
                    return

                # 사용자 메시지를 먼저 채팅창에 표시
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "chat_message",
                            "message": {
                                "text": user_message,
                                "sender": "user",
                                "timestamp": timezone.now().isoformat(),
                            },
                        }
                    )
                )

                # 사용자 API 호출 제한 확인
                can_call_api = await self.check_api_limit()
                if not can_call_api:
                    await self.send_error(
                        "API 호출 제한에 도달했습니다. 제한이 리셋될 때까지 기다려주세요."
                    )
                    return

                # 동일한 질문이 있는지 확인하고 UserQuestion 가져오기 또는 생성
                user_question = await self.get_or_create_user_question(user_message)

                # 기존 AI 응답이 있는지 확인
                existing_response = await self.get_latest_ai_response(user_question)

                if existing_response:
                    # 기존 응답이 있으면 바로 전송 (API 호출 없음)
                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "chat_message",
                                "message": {
                                    "id": existing_response.id,
                                    "text": existing_response.content,
                                    "sender": "ai",
                                    "timestamp": existing_response.created_at.isoformat(),
                                    "cached": True,
                                    "ai_model": existing_response.ai_model,
                                },
                            }
                        )
                    )
                    logger.info(f"Used cached AI response: {existing_response.id}")
                else:
                    # 새 AI 응답 생성 (API 호출 횟수 증가)
                    await self.increment_api_calls()
                    await self.generate_new_ai_response(user_question)

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            await self.send_error("Invalid message format")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}", exc_info=True)
            await self.send_error(f"Error processing message: {str(e)}")

    @database_sync_to_async
    def check_api_limit(self):
        """API 호출 제한 확인"""
        try:
            return self.user.can_make_api_call()
        except Exception as e:
            logger.error(f"Error checking API limit: {str(e)}")
            return False

    @database_sync_to_async
    def increment_api_calls(self):
        """API 호출 횟수 증가"""
        try:
            self.user.increment_api_calls()
            logger.info(
                f"API calls incremented for user {self.user.username}: {self.user.api_calls_count}/{self.user.api_calls_limit}"
            )
        except Exception as e:
            logger.error(f"Error incrementing API calls: {str(e)}")

    @database_sync_to_async
    def get_or_create_user_question(self, content):
        """동일한 질문이 있는지 확인하고 UserQuestion 가져오기 또는 생성"""
        try:
            # 동일한 내용의 질문이 이미 있는지 확인 (대소문자 구분 없이, 공백 제거 후 비교)
            normalized_content = content.strip().lower()

            existing_question = UserQuestion.objects.filter(
                user=self.user,
                content__iexact=content.strip(),  # 대소문자 구분 없이 정확히 일치
                is_deleted=False,
            ).first()

            if existing_question:
                logger.info(f"Found existing question: {existing_question.id}")
                return existing_question

            # 새 질문 생성
            question = UserQuestion.objects.create(
                user=self.user, content=content.strip(), question_type="text"
            )
            logger.info(f"Created new question: {question.id}")
            return question

        except Exception as e:
            logger.error(f"Error getting/creating user question: {str(e)}")
            raise

    @database_sync_to_async
    def get_latest_ai_response(self, user_question):
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

    async def generate_new_ai_response(self, user_question):
        """새로운 AI 응답 생성"""
        try:
            # 처리 중 메시지 전송
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing_indicator",
                        "message": {
                            "text": "AI가 응답을 생성하고 있습니다...",
                            "sender": "system",
                            "timestamp": timezone.now().isoformat(),
                        },
                    }
                )
            )

            # AI 응답 생성
            start_time = time.time()
            ai_response_content = await self.get_ai_response(user_question.content)
            response_time = time.time() - start_time

            # AI 응답을 데이터베이스에 저장
            ai_response = await self.save_ai_response(
                user_question=user_question,
                content=ai_response_content,
                ai_model="openai/gpt-3.5-turbo",
                response_time=response_time,
            )

            # AI 응답을 채팅창에 표시
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat_message",
                        "message": {
                            "id": ai_response.id,
                            "text": ai_response_content,
                            "sender": "ai",
                            "timestamp": ai_response.created_at.isoformat(),
                            "response_time": round(response_time, 2),
                            "ai_model": ai_response.ai_model,
                            "cached": False,
                        },
                    }
                )
            )

            logger.info(f"Generated new AI response: {ai_response.id}")

        except Exception as e:
            logger.error(f"Error generating new AI response: {str(e)}", exc_info=True)
            await self.send_error("AI 응답 생성 중 오류가 발생했습니다.")

    @database_sync_to_async
    def save_ai_response(self, user_question, content, ai_model, response_time):
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

    async def get_ai_response(self, user_message):
        """OpenRouter AI에게 메시지를 보내고 응답을 받는 함수"""
        try:
            # OpenRouter API 설정
            api_key = "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"
            if not api_key:
                logger.error("OPENROUTER_API_KEY not found")
                return "죄송합니다. AI 서비스 설정에 문제가 있습니다."

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Django Chat App",
            }

            # 사용할 모델 - GPT-3.5 Turbo 사용
            model = "openai/gpt-3.5-turbo"

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 친절하고 정확하게 답변해주세요. 한국어로 답변해주세요.",
                    },
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
            }

            # OpenRouter API 호출
            timeout = aiohttp.ClientTimeout(total=30)  # 30초 타임아웃
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_message = result["choices"][0]["message"]["content"]
                        return ai_message.strip()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"OpenRouter API error: {response.status} - {error_text}"
                        )
                        return f"죄송합니다. AI 서비스에 일시적인 문제가 발생했습니다. (Status: {response.status})"

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            return "죄송합니다. 네트워크 연결에 문제가 있습니다."
        except KeyError as e:
            logger.error(f"Unexpected API response format: {str(e)}")
            return "죄송합니다. AI 서비스 응답 형식에 문제가 있습니다."
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return "죄송합니다. AI 서비스에 문제가 발생했습니다."

    async def send_error(self, error_message):
        """에러 메시지 전송"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "error",
                    "message": {
                        "text": error_message,
                        "sender": "system",
                        "timestamp": timezone.now().isoformat(),
                    },
                }
            )
        )
