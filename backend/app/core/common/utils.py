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

"""
通用工具函数

子模块:
- auth: JWT 认证 (create_access_token, decode_access_token, verify_token)
- document_utils: 文档处理 (build_collection_map, enrich_document_dict)
- masking: 数据脱敏 (mask_bot_config_inplace, filter_client_site_data, mask_variable)
"""

import hashlib
import re
import secrets
import uuid
from contextvars import ContextVar
from datetime import datetime, timedelta
from typing import Any

from app.core.infra.config import settings  # noqa: F401 (部分调用方通过 utils 间接依赖)

# 用于跨层级收集 RAG 统计信息以便在回合结束时进行汇总打印
rag_stats_var: ContextVar[dict | None] = ContextVar("rag_stats", default=None)

NAMESPACE_CATWIKI = uuid.uuid5(uuid.NAMESPACE_DNS, "catwiki.com")


def get_vector_id(doc_id: int) -> str:
    """生成确定性的 UUID（基于文档 ID）"""
    return str(uuid.uuid5(NAMESPACE_CATWIKI, str(doc_id)))


def generate_token(length: int = 32) -> str:
    """生成随机令牌"""
    return secrets.token_urlsafe(length)


def hash_string(text: str) -> str:
    """生成字符串的 SHA256 哈希"""
    return hashlib.sha256(text.encode()).hexdigest()


def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(dt_str, fmt)


def get_future_datetime(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    """获取未来的日期时间"""
    return datetime.utcnow() + timedelta(days=days, hours=hours, minutes=minutes)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断字符串"""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def strip_markdown(text: str) -> str:
    """
    [✨ 亮点] 去除文字中的 Markdown 格式，降级为文字。
    常用于不支持 Markdown 渲染的推送通道（如微信客服、短信、飞书非 Markdown 模式等）。

    逻辑规则:
    1. 标题 (#) -> 去除 #
    2. 加粗/斜体 (**/*) -> 去除 *
    3. 行内代码 (`) -> 去除 `
    4. 代码块 (```) -> 去除 ```
    5. 链接 ([desc](url)) -> desc (url)
    6. 图片 (![desc](url)) -> [图片: desc]
    """
    if not text:
        return ""

    # 1. 链接 [desc](url) -> desc (url)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"\1 (\2)", text)

    # 2. 图片 ![desc](url) -> [图片: desc]
    text = re.sub(r"!\[([^\]]*)\]\((https?://[^\)]+)\)", r"[图片: \1]", text)

    # 3. 标题 # 标题 -> 标题
    text = re.sub(r"^#+\s*(.*)$", r"\1", text, flags=re.MULTILINE)

    # 4. 加粗/斜体 **text** or *text* -> text
    text = re.sub(r"[*_]{1,3}(.*?)[*_]{1,3}", r"\1", text)

    # 5. 行内代码 `code` -> code
    text = re.sub(r"`(.*?)`", r"\1", text)

    # 6. 代码块 ```code``` -> code
    # 尽可能保留缩进，并移除开头的语言标识
    text = re.sub(r"```(?:\w+\n)?([\s\S]*?)```", r"\1", text)

    # 7. 清理多余的连续空白行
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """移除字典中的 None 值"""
    return {k: v for k, v in data.items() if v is not None}


class Paginator:
    """分页器"""

    def __init__(self, page: int = 1, size: int = 10, total: int = 0, is_pager: int = 1):
        self.is_pager = is_pager
        if is_pager == 0:
            self.page = 1
            self.size = None
        else:
            self.page = max(1, page)
            self.size = max(1, size)
        self.total = max(0, total)

    @property
    def skip(self) -> int:
        """跳过的记录数"""
        if self.is_pager == 0:
            return 0
        return (self.page - 1) * self.size

    @property
    def total_pages(self) -> int:
        """总页数"""
        if self.is_pager == 0:
            return 1
        return (self.total + self.size - 1) // self.size if self.total > 0 else 0

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        if self.is_pager == 0:
            return False
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        if self.is_pager == 0:
            return False
        return self.page > 1

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "page": self.page,
            "size": self.size if self.size is not None else self.total,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }

    def to_pagination_info(self):
        """转换为 PaginationInfo 模型"""
        from app.schemas.response import PaginationInfo

        if self.is_pager == 0:
            return PaginationInfo(is_pager=0, page=1, size=self.total, total=self.total)
        return PaginationInfo(
            is_pager=1,
            page=self.page,
            size=self.size,
            total=self.total,
        )


def log_ai_config_card(section: str, config: dict[str, Any], title: str = "Active Config"):
    """[✨ 亮点] 统一打印 AI 配置可视化卡片"""
    import json
    import logging

    from app.core.common.masking import mask_sensitive_data

    logger = logging.getLogger(f"app.core.ai.config.{section}")
    masked = mask_sensitive_data(config)

    model = masked.get("model", "N/A")
    provider = masked.get("provider", "N/A")
    extra_body = masked.get("extra_body")
    h = config.get("_hash", "N/A")

    try:
        pretty_json = json.dumps(masked, indent=4, ensure_ascii=False)
    except Exception:
        pretty_json = str(masked)

    log_msg = (
        f"\n{'=' * 60}\n"
        f"🔍 [{section.upper()}] -> {title}\n"
        f"   - 哈希指纹: {h}\n"
        f"   - 核心模型: {provider} | {model}\n"
        f"   - 扩展参数 (extra_body): {json.dumps(extra_body, ensure_ascii=False) if extra_body else 'None'}\n"
        f"   - 配置快照:\n{pretty_json}\n"
        f"{'=' * 60}"
    )
    logger.debug(log_msg)


def log_ai_usage_signal(
    section: str,
    model: str,
    h: str,
    is_hit: bool = True,
    tenant_id: Any = None,
    extra: dict[str, Any] | None = None,
    purpose: str | None = None,
):
    """[✨ 亮点] 统一打印 AI 模型使用/复用信号 (采用 Mini-Card 格式，极高辨识度)"""
    import logging

    logger = logging.getLogger(f"app.core.ai.usage.{section}")

    icon = "♻️ " if is_hit else "🚀"
    status_text = "CACHE HIT (Reusing)" if is_hit else "NEW LOAD (Initializing)"
    h_brief = h[:8] if h else "N/A"
    tenant_info = f" | Tenant: {tenant_id}" if tenant_id is not None else ""

    # 构建扩展信息行
    extra_lines = ""
    if extra:
        for key, value in extra.items():
            if value is not None and value != "":
                # 💡 [优化] 缓存命中时，隐藏一些冗余的静态配置信息，保持日志清爽
                if is_hit and key in ["Base URL", "Source", "Dimension", "Provider", "Fingerprint"]:
                    continue
                extra_lines += f"   - {key}: {value}\n"

    purpose_str = f"   - Purpose: {purpose}\n" if purpose else ""

    line_color = "-" * 80 if not is_hit else "-" * 40
    msg = (
        f"\n{line_color}\n"
        f"{icon} [{section.upper():9}] {status_text}\n"
        f"   - Model: {model}\n"
        f"{purpose_str}"
        f"   - Fingerprint: {h_brief}{tenant_info}\n"
        f"{extra_lines}"
        f"{line_color}"
    )
    logger.debug(msg)


def log_process_step_card(
    section: str, title: str, step: int, total: int, details: str | None = None
):
    """[✨ 亮点] 统一打印过程/进度卡片 (如 Graph 迭代)"""
    import logging

    logger = logging.getLogger(f"app.core.process.{section}")

    progress_bar = "■" * step + "□" * (total - step)
    line = "═" * 80
    detail_line = f"   - Context: {details}\n" if details else ""

    msg = (
        f"\n{line}\n"
        f"🔄 [{section.upper():9}] {title}\n"
        f"   - Progress: {step}/{total} [{progress_bar}]\n"
        f"{detail_line}"
        f"{line}"
    )
    logger.debug(msg)
