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

from sqlalchemy import event, true
from sqlalchemy.orm import Session, with_loader_criteria

from app.db.base import Base


def _tenant_filter_criteria(cls):
    """
    租户过滤准则函数（全局具名以支持序列化）
    """
    from sqlalchemy import bindparam

    from app.core.infra.tenant import get_current_tenant

    tenant_id = get_current_tenant()
    if tenant_id is not None:
        if hasattr(cls, "tenant_id"):
            # 使用 bindparam 确保 tenant_id 作为一个绑定的变量在 SQL 中，
            # 并通过 execution_options 中的 tenant_id 确保不同租户的 SQL 缓存隔离。
            return cls.tenant_id == bindparam("current_tenant_id", value=tenant_id)
    return true()


def apply_tenant_filter(execute_state):
    """
    在 ORM 执行前拦截并注入 tenant_id 过滤条件
    """
    from app.core.infra.tenant import get_current_tenant

    tenant_id = get_current_tenant()
    if tenant_id is not None:
        # 仅对支持 options 的语句注入过滤准则（主要是 ORM 语句）
        if hasattr(execute_state.statement, "options"):
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Base,
                    _tenant_filter_criteria,
                    include_aliases=True,
                )
            )

        # 核心修复：SQLAlchemy 会缓存带有 with_loader_criteria 的语句。
        # 由于我们的过滤准则依赖于外部状态 (tenant_id)，必须确保不同租户的语句具有不同的缓存键。
        # 仅对支持 where 的 Generative 语句（Select, Update, Delete）注入指纹。
        # 这确保了不同租户生成的 SQL 在缓存中是相互独立的。
        if hasattr(execute_state.statement, "where"):
            from sqlalchemy import literal_column

            execute_state.statement = execute_state.statement.where(
                literal_column(str(tenant_id)) == literal_column(str(tenant_id))
            )


@event.listens_for(Base, "before_insert", propagate=True)
def apply_tenant_on_insert(mapper, connection, target):
    """
    在数据入库前自动填充 tenant_id
    """
    if hasattr(target, "tenant_id") and getattr(target, "tenant_id") is None:
        from app.core.infra.tenant import get_current_tenant

        tenant_id = get_current_tenant()  # In OSS, this returns 1
        if tenant_id is not None:
            setattr(target, "tenant_id", tenant_id)


def register_core_db_events():
    """
    Register core database events.
    In Community Edition, this handles basic tenant_id population and filtration (defaulting to 1).
    """
    event.listen(Session, "do_orm_execute", apply_tenant_filter)
