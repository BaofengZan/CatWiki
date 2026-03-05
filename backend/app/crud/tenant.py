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


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class CRUDTenant(CRUDBase[Tenant, TenantCreate, TenantUpdate]):
    """租户 CRUD 操作"""

    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Tenant | None:
        """根据 slug 获取租户"""
        result = await db.execute(select(Tenant).where(Tenant.slug == slug))
        return result.scalar_one_or_none()

    async def remove(self, db: AsyncSession, *, id: int) -> Tenant:
        """删除租户并清理相关向量数据"""
        # 1. 清理该租户下所有站点的向量数据
        try:
            from app.core.vector.vector_store import VectorStoreManager

            vector_mgr = await VectorStoreManager.get_instance()
            await vector_mgr.delete_by_metadata("tenant_id", id)
        except Exception as e:
            from app.core.infra.logging import logger

            logger.warning(f"⚠️ [Cleanup] 租户 {id} 向量清理失败: {e}")

        # 2. 执行数据库删除
        return await super().remove(db, id=id)


crud_tenant = CRUDTenant(Tenant)
