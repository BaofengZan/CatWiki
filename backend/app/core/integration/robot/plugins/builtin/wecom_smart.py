from __future__ import annotations

from app.core.integration.robot.contexts.wecom import get_wecom_smart_context
from app.core.integration.robot.registry.context_registry import register_robot_context_resolver


async def _resolver(kind: str, site_id: int, db):
    return await get_wecom_smart_context(site_id, db)


register_robot_context_resolver(
    "wecom_smart",
    _resolver,
    override=True,
    source="builtin",
)
