from __future__ import annotations

from fastapi import HTTPException

from app.core.integration.robot.registry.context_registry import register_robot_context_resolver


async def _resolver(kind: str, site_id: int, db):
    raise HTTPException(status_code=501, detail="机器人平台尚未接入")


register_robot_context_resolver(
    "dingtalk_app",
    _resolver,
    override=True,
    source="builtin",
)
