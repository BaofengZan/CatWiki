# Copyright 2026 CatWiki Authors
#
# Licensed under the CatWiki Open Source License (Modified Apache 2.0);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/CatWiki/CatWiki/blob/main/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""健康检查服务"""

import logging
from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infra.config import settings
from app.db.database import get_db


class HealthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_health_status(self) -> dict:
        """获取系统健康状态"""
        logger = logging.getLogger(__name__)

        try:
            from app.ee.license import license_service

            is_licensed = license_service.is_valid
        except ImportError:
            is_licensed = False

        status = "healthy"
        checks = {}

        # 检查缓存
        try:
            from app.core.infra.cache import get_cache

            cache = get_cache()
            stats = cache.stats()
            checks["cache"] = stats.get("backend", "unknown")
        except Exception as e:
            checks["cache"] = f"error: {str(e)}"
            status = "degraded"
            logger.error(f"健康检查: 缓存检查失败 - {e}")

        return {
            "status": status,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "edition": settings.CATWIKI_EDITION if is_licensed else "community",
            "is_licensed": is_licensed,
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": checks,
        }


def get_health_service(db: AsyncSession = Depends(get_db)) -> HealthService:
    """获取 HealthService 实例的依赖注入函数"""
    return HealthService(db)
