# Copyright 2026 CatWiki Authors

import logging
from typing import Any

from app.core.integration.robot.base import BaseRobotAdapter, RobotInboundEvent, RobotSession

logger = logging.getLogger(__name__)


class WeComKefuAdapter(BaseRobotAdapter):
    """企业微信客服适配器。"""

    def get_provider_name(self) -> str:
        return "企业微信客服"

    def get_provider_id(self) -> str:
        return "wecom_kefu"

    def parse_inbound_text_event(self, data: Any, site_id: int) -> RobotInboundEvent | None:
        """微信客服目前在 Service 层手动解析。"""
        raise NotImplementedError("微信客服暂时由 Service 直接解析")

    def is_streaming_supported(self, session: RobotSession | None = None) -> bool:
        """不支持流式"""
        return False

    async def reply(
        self,
        session: RobotSession,
        content: str,
        is_finish: bool = False,
        is_error: bool = False,
    ) -> None:
        """
        客服消息回复逻辑。
        微信客服回复通过 API 发送，而非 Webhook 响应。
        """
        if not is_finish and not is_error:
            # 微信客服通常不支持流式，我们只在完成或错误时发送完整回复
            return

        # 获取配置
        config = session.config
        if not config or not isinstance(config, dict):
            logger.error("WeComKefuAdapter: 缺失配置信息")
            return

        corp_id = config.get("corp_id")
        secret = config.get("secret")

        # 从会话中获取原始事件信息
        inbound_event = session.event
        open_kfid = inbound_event.extra.get("open_kfid")
        external_userid = inbound_event.from_user

        if not open_kfid or not external_userid:
            logger.error("WeComKefuAdapter: 缺失 open_kfid 或 external_userid")
            return

        # 发送客服消息
        from app.core.integration.robot.services.wecom_kefu import WeComKefuService

        await WeComKefuService.send_message(
            corp_id=corp_id,
            secret=secret,
            open_kfid=open_kfid,
            external_userid=external_userid,
            content=content,
        )
