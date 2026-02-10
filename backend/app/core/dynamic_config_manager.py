# Copyright 2024 CatWiki Authors
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

"""全局动态配置管理器

提供对数据库中 ai_config 的统一访问和时间缓存 (TTL)，减少重复数据库查询。
"""

import logging
import time
from typing import Dict, Any, Optional

from app.db.database import AsyncSessionLocal
from app.crud.system_config import crud_system_config

logger = logging.getLogger(__name__)

AI_CONFIG_KEY = "ai_config"


class DynamicConfigManager:
    """动态配置管理器 (单例)"""

    _instance: Optional["DynamicConfigManager"] = None

    def __init__(self, cache_ttl: int = 300):
        self._config_cache: Dict[str, Any] = {}
        self._last_update: float = 0
        self._cache_ttl = cache_ttl  # 默认 5 分钟缓存

    @classmethod
    def get_instance(cls) -> "DynamicConfigManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def _ensure_config(self) -> Dict[str, Any]:
        """确保缓存的消息是最新的"""
        now = time.time()
        if now - self._last_update < self._cache_ttl and self._config_cache:
            return self._config_cache

        async with AsyncSessionLocal() as db:
            try:
                config = await crud_system_config.get_by_key(db, config_key=AI_CONFIG_KEY)
                self._last_update = now

                if config and config.config_value:
                    self._config_cache = config.config_value
                    logger.debug(
                        f"🔄 [ConfigManager] Cache updated from DB (TTL: {self._cache_ttl}s)"
                    )
                else:
                    logger.warning(
                        f"⚠️ [ConfigManager] System config '{AI_CONFIG_KEY}' not found in DB."
                    )
                    # 如果 DB 没有，保留旧缓存或设为空 dict
                    if not self._config_cache:
                        self._config_cache = {}
            except Exception as e:
                logger.error(f"❌ [ConfigManager] Failed to fetch config from DB: {e}")
                # 出现异常时缩短重试跨度
                self._last_update = now - self._cache_ttl + 10

        return self._config_cache

    def _extract_section(self, config: Dict[str, Any], section: str) -> Dict[str, Any]:
        """提取特定的配置段并兼容旧结构"""
        # 1. 尝试直接读取扁平结构
        data = config.get(section, {})

        # 2. 兼容 manualConfig 嵌套结构
        if not data and "manualConfig" in config:
            data = config.get("manualConfig", {}).get(section, {})

        return data if isinstance(data, dict) else {}

    async def get_chat_config(self) -> Dict[str, Any]:
        """获取聊天配置"""
        config = await self._ensure_config()
        chat_conf = self._extract_section(config, "chat")

        return {
            "provider": chat_conf.get("provider", "openai"),
            "model": chat_conf.get("model", ""),
            "apiKey": chat_conf.get("apiKey", ""),
            "baseUrl": chat_conf.get("baseUrl", ""),
        }

    async def get_embedding_config(self) -> Dict[str, Any]:
        """获取嵌入配置"""
        config = await self._ensure_config()
        return self._extract_section(config, "embedding")

    async def get_rerank_config(self) -> Dict[str, Any]:
        """获取重排序配置"""
        config = await self._ensure_config()
        return self._extract_section(config, "rerank")


# 全局单例
dynamic_config_manager = DynamicConfigManager.get_instance()
