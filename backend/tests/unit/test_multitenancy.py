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
多租户隔离逻辑单元测试
"""

from app.core.infra.cache import generate_cache_key
from app.core.infra.tenant import (
    get_current_tenant,
    set_current_tenant,
    temporary_tenant_context,
)


class TestTenantContext:
    def test_set_and_get_tenant(self):
        set_current_tenant(123)
        assert get_current_tenant() == 123

        set_current_tenant(None)
        assert get_current_tenant() is None

        set_current_tenant(456)
        assert get_current_tenant() == 456

    def test_temporary_context(self):
        set_current_tenant(1)
        assert get_current_tenant() == 1

        with temporary_tenant_context(2):
            assert get_current_tenant() == 2

        assert get_current_tenant() == 1

    def test_nested_temporary_context(self):
        set_current_tenant(1)
        with temporary_tenant_context(2):
            assert get_current_tenant() == 2
            with temporary_tenant_context(3):
                assert get_current_tenant() == 3
            assert get_current_tenant() == 2
        assert get_current_tenant() == 1


class TestCacheIsolation:
    def test_cache_key_isolation_by_tenant(self):
        # 租户 1 的 Key
        set_current_tenant(1)
        key1 = generate_cache_key("test_prefix", param="val")

        # 租户 2 的 Key (参数相同)
        set_current_tenant(2)
        key2 = generate_cache_key("test_prefix", param="val")

        # 全局 (None) 的 Key
        set_current_tenant(None)
        key_none = generate_cache_key("test_prefix", param="val")

        assert key1 != key2
        assert key1 != key_none
        assert "t1" in key1
        assert "t2" in key2
        assert "tall" in key_none

    def test_cache_key_consistency_within_tenant(self):
        set_current_tenant(1)
        key_a = generate_cache_key("test_prefix", a=1, b=2)
        key_b = generate_cache_key("test_prefix", b=2, a=1)  # 参数顺序不同但内容相同

        assert key_a == key_b

    def test_cache_key_complex_objects(self):
        set_current_tenant(1)
        # 验证复杂对象嵌套时的稳定性
        key1 = generate_cache_key("complex", data={"list": [1, 2, {"x": 10}]})
        key2 = generate_cache_key("complex", data={"list": [1, 2, {"x": 10}]})

        assert key1 == key2


class TestDatabaseInterceptors:
    """测试数据库拦截器逻辑 (app.db.events)"""

    def test_tenant_filter_criteria(self):
        from sqlalchemy import BinaryExpression

        from app.db.events import _tenant_filter_criteria
        from app.models.site import Site

        # 1. 设置租户 1
        set_current_tenant(1)
        criterion = _tenant_filter_criteria(Site)
        assert isinstance(criterion, BinaryExpression)
        # 验证绑定了正确的租户 ID (内部比较逻辑)
        assert criterion.right.value == 1

        # 2. 未设置租户 (应该返回 true)
        set_current_tenant(None)
        criterion_none = _tenant_filter_criteria(Site)

        # true() 在 SQLAlchemy 中通常是这种类型
        assert not hasattr(criterion_none, "left")

    def test_apply_tenant_on_insert(self):
        from app.db.events import apply_tenant_on_insert
        from app.models.site import Site

        target_site = Site(name="Test Site")

        # 1. 模拟设置租户 100
        set_current_tenant(100)
        apply_tenant_on_insert(None, None, target_site)
        assert target_site.tenant_id == 100

        # 2. 如果已经手动设置了 tenant_id，不应覆盖
        target_site_2 = Site(name="Manual Site", tenant_id=200)
        apply_tenant_on_insert(None, None, target_site_2)
        assert target_site_2.tenant_id == 200
