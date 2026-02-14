import json
import logging
import base64
import time
import string
import random
import httpx
from Crypto.Cipher import AES
from typing import Optional, Dict, Any, List

from fastapi.responses import StreamingResponse
from app.services.chat_service import ChatService
from app.schemas.chat import ChatCompletionRequest
from app.schemas.document import VectorRetrieveFilter
from app.models.site import Site

logger = logging.getLogger(__name__)

# 常量定义
BUFFER_CLEANUP_THRESHOLD = 60  # 清理频率（秒）
FINISHED_TASK_EXPIRY = 300  # 已完成任务保留时间（秒）
ACTIVE_TASK_EXPIRY = 1800  # 活跃任务强制过期时间（秒）


class WeComRobotService:
    """企业微信智能机器人业务逻辑"""

    # 任务状态缓冲区
    # 建议生产环境替换为 Redis
    _response_buffer: Dict[str, Dict[str, Any]] = {}
    _last_cleanup_time: float = time.time()

    @classmethod
    def _generate_stream_id(cls, length: int = 10) -> str:
        """生成随机流 ID"""
        letters = string.ascii_letters + string.digits
        return "".join(random.choice(letters) for _ in range(length))

    @classmethod
    def _cleanup_buffer(cls):
        """清理过期缓冲区"""
        now = time.time()
        if now - cls._last_cleanup_time < BUFFER_CLEANUP_THRESHOLD:
            return

        keys_to_remove = []
        for sid, task in cls._response_buffer.items():
            timestamp = task.get("timestamp", 0)
            is_finished = task.get("finish", False)

            if is_finished and (now - timestamp > FINISHED_TASK_EXPIRY):
                keys_to_remove.append(sid)
            elif now - timestamp > ACTIVE_TASK_EXPIRY:
                keys_to_remove.append(sid)

        for k in keys_to_remove:
            cls._response_buffer.pop(k, None)

        cls._last_cleanup_time = now
        if keys_to_remove:
            logger.info(f"清理了 {len(keys_to_remove)} 个过期的企业微信流式任务。")

    @classmethod
    def _create_stream_error_msg(cls, stream_id: str, content: str) -> Dict[str, Any]:
        """构造流式错误响应"""
        return {
            "msgtype": "stream",
            "stream": {"id": stream_id, "finish": True, "content": content},
        }

    @classmethod
    async def process_text_message(
        cls, site: Site, from_user: str, content: str, background_tasks: Any
    ) -> Dict[str, Any]:
        """处理文本消息：启动异步 AI 任务"""
        cls._cleanup_buffer()
        stream_id = cls._generate_stream_id()

        cls._response_buffer[stream_id] = {
            "content": "正在思考中...",
            "finish": False,
            "timestamp": time.time(),
        }

        async def _run_ai_task():
            try:
                chat_request = ChatCompletionRequest(
                    message=content,
                    thread_id=f"wecom-robot-{from_user}",
                    user=from_user,
                    stream=True,
                    filter=VectorRetrieveFilter(site_id=site.id),
                )
                response = await ChatService.process_chat_request(chat_request, background_tasks)

                full_text = ""
                if isinstance(response, StreamingResponse):
                    line_buffer = ""
                    async for chunk in response.body_iterator:
                        chunk_str = chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk
                        line_buffer += chunk_str

                        while "\n" in line_buffer:
                            line, line_buffer = line_buffer.split("\n", 1)
                            line = line.strip()
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data_json = json.loads(data_str)
                                    delta = data_json.get("choices", [{}])[0].get("delta", {})
                                    token = delta.get("content", "")
                                    if token:
                                        full_text += token
                                        cls._response_buffer[stream_id]["content"] = full_text
                                except (json.JSONDecodeError, KeyError, IndexError):
                                    continue

                cls._response_buffer[stream_id].update(
                    {
                        "content": full_text or "抱歉，我暂时无法回答这个问题。",
                        "finish": True,
                        "timestamp": time.time(),
                    }
                )
            except Exception as e:
                logger.error(f"企业微信 AI 任务出错: {e}", exc_info=True)
                cls._response_buffer[stream_id].update(
                    {
                        "content": "服务暂时繁忙，请稍后再试。",
                        "finish": True,
                        "timestamp": time.time(),
                    }
                )

        background_tasks.add_task(_run_ai_task)

        return {
            "msgtype": "stream",
            "stream": {"id": stream_id, "finish": False, "content": "已收到，正在为您写答案..."},
        }

    @classmethod
    def get_stream_response(cls, stream_id: str) -> Dict[str, Any]:
        """获取流式进度"""
        task = cls._response_buffer.get(stream_id)
        if not task:
            return cls._create_stream_error_msg(stream_id, "任务已过期，请重新提问。")

        return {
            "msgtype": "stream",
            "stream": {"id": stream_id, "finish": task["finish"], "content": task["content"]},
        }

    @classmethod
    async def process_image_message(cls, image_url: str, aes_key_base64: str) -> Dict[str, Any]:
        """处理加密图片消息"""
        cls._cleanup_buffer()
        temp_id = cls._generate_stream_id()

        try:
            async with httpx.AsyncClient() as client:
                # 企业微信图片地址有效期通常较短，超时设为 15s
                resp = await client.get(image_url, timeout=15)
                resp.raise_for_status()
                encrypted_data = resp.content

            # AES 加解密逻辑
            # 处理 Base64 补位
            missing_padding = len(aes_key_base64) % 4
            if missing_padding:
                aes_key_base64 += "=" * (4 - missing_padding)
            aes_key = base64.b64decode(aes_key_base64)

            # 使用 AES-CBC 模式解密，IV 取 Key 的前 16 位
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
            decrypted_data = cipher.decrypt(encrypted_data)

            # 移除 PKCS7 填充
            pad_len = decrypted_data[-1]
            if not (1 <= pad_len <= 32):
                raise ValueError("无效的填充模式")
            decrypted_data = decrypted_data[:-pad_len]

            logger.info(f"图片解密成功: {len(decrypted_data)} 字节")
            return {
                "msgtype": "stream",
                "stream": {
                    "id": temp_id,
                    "finish": True,
                    "content": "已收到图片。目前智能机器人主要处理文本咨询，后续将支持图片分析。",
                },
            }
        except Exception as e:
            logger.error(f"图片处理失败: {e}")
            return cls._create_stream_error_msg(temp_id, "图片处理失败，请检查网络或稍后重试。")
