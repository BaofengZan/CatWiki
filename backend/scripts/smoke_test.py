#!/usr/bin/env python3
"""
CatWiki 冒烟测试脚本

覆盖核心 CRUD 操作：登录 → 站点 → 合集 → 文档 → 用户 → 缓存失效 → AI 向量化 → 清理
用于验证缓存失效、事务提交等基础链路是否正常。

用法:
    # 容器内执行
    docker compose -f docker-compose.dev.yml exec backend uv run python scripts/smoke_test.py

    # 指定地址
    python scripts/smoke_test.py --base-url http://localhost:3000

    # 跳过 AI 测试（未配置模型时）
    python scripts/smoke_test.py --skip-ai
"""

import argparse
import sys
import time

import httpx

# ==================== 配置 ====================

DEFAULT_BASE = "http://localhost:3000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN_API = "/admin/v1"
CLIENT_API = "/v1"


# ==================== 测试运行器 ====================


class SmokeTest:
    def __init__(self, base_url: str):
        self.client = httpx.Client(base_url=base_url, timeout=30)
        self.passed = 0
        self.failed = 0
        # 记录所有创建的资源 ID，确保清理
        self._cleanup_stack: list[tuple[str, str]] = []  # (method_path, label)

    def api(self, method: str, path: str, prefix: str = ADMIN_API, **kwargs) -> dict:
        """发起 API 请求并返回 data 字段"""
        url = f"{prefix}{path}"
        resp = self.client.request(method, url, **kwargs)
        body = resp.json()
        if resp.status_code >= 400:
            raise AssertionError(f"{method} {url} → {resp.status_code}: {body}")
        return body.get("data")

    def step(self, name: str, fn):
        """执行一个测试步骤"""
        try:
            result = fn()
            print(f"  ✅ {name}")
            self.passed += 1
            return result
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            self.failed += 1
            return None

    def assert_field(self, name: str, data: dict | None, field: str, expected):
        """断言字段值，失败计入测试结果"""
        if data is None:
            return
        actual = data.get(field)
        if actual != expected:
            print(f"  ❌ {name}: 期望 {field}={expected!r}，实际={actual!r}")
            self.failed += 1
        else:
            print(f"  ✅ {name}")
            self.passed += 1

    def expect_status(self, name: str, method: str, path: str, status_code: int):
        """断言 HTTP 状态码"""
        def _check():
            resp = self.client.request(method, f"{ADMIN_API}{path}")
            if resp.status_code != status_code:
                raise AssertionError(f"期望 {status_code}，实际 {resp.status_code}")
            return True
        return self.step(name, _check)

    def cleanup(self):
        """执行清理栈中所有资源删除"""
        if not self._cleanup_stack:
            return
        print("\n📋 清理")
        for path, label in reversed(self._cleanup_stack):
            self.step(f"删除{label}", lambda p=path: self.api("DELETE", p))

    def run(self, skip_ai: bool = False) -> bool:
        ts = int(time.time())

        print(f"\n🚀 CatWiki 冒烟测试 ({self.client.base_url})")
        print("=" * 50)

        try:
            self._run_tests(ts, skip_ai)
        except KeyboardInterrupt:
            print("\n\n⚠️  测试中断，执行清理...")
        finally:
            self.cleanup()
            self.client.close()

        # 结果
        print("\n" + "=" * 50)
        total = self.passed + self.failed
        if self.failed:
            print(f"📊 结果: {self.passed}/{total} 通过, {self.failed} 失败 ❌")
        else:
            print(f"📊 结果: {self.passed}/{total} 通过 ✅")
        print()
        return self.failed == 0

    def _run_tests(self, ts: int, skip_ai: bool):
        # 1. 登录
        print("\n📋 认证")
        token = self.step("登录", lambda: self.api(
            "POST", "/users:login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )["token"])
        if not token:
            print("\n💀 登录失败，终止测试")
            return
        self.client.headers["Authorization"] = f"Bearer {token}"

        # 2. 站点 CRUD
        print("\n📋 站点")
        site = self.step("创建站点", lambda: self.api(
            "POST", "/sites",
            json={"name": f"测试站点_{ts}", "slug": f"test-{ts}", "status": "active"},
        ))
        site_id = site["id"] if site else None
        if site_id:
            self._cleanup_stack.append((f"/sites/{site_id}", "站点"))

        if site_id:
            self.step("查询站点", lambda: self.api("GET", f"/sites/{site_id}"))
            self.step("Slug查询", lambda: self.api("GET", f"/sites:bySlug/test-{ts}"))
            self.step("更新站点", lambda: self.api(
                "PUT", f"/sites/{site_id}",
                json={"name": f"测试站点_{ts}_updated", "description": "冒烟测试"},
            ))
            updated = self.step("查询更新结果", lambda: self.api("GET", f"/sites/{site_id}"))
            self.assert_field("缓存验证-站点更新", updated, "name", f"测试站点_{ts}_updated")

        # 3. 合集 CRUD
        print("\n📋 合集")
        collection = None
        if site_id:
            collection = self.step("创建合集", lambda: self.api(
                "POST", "/collections",
                json={"title": f"测试合集_{ts}", "site_id": site_id},
            ))
        col_id = collection["id"] if collection else None
        if col_id:
            self._cleanup_stack.append((f"/collections/{col_id}", "合集"))

        if col_id:
            self.step("查询合集", lambda: self.api("GET", f"/collections/{col_id}"))
            self.step("更新合集", lambda: self.api(
                "PUT", f"/collections/{col_id}",
                json={"title": f"测试合集_{ts}_updated"},
            ))
            self.step("合集树", lambda: self.api("GET", f"/collections:tree?site_id={site_id}"))

        # 4. 文档 CRUD
        print("\n📋 文档")
        doc = None
        if site_id and col_id:
            doc = self.step("创建文档", lambda: self.api(
                "POST", "/documents",
                json={
                    "title": f"测试文档_{ts}",
                    "site_id": site_id,
                    "collection_id": col_id,
                    "author": "smoke_test",
                    "content": "# 冒烟测试\n\n这是一篇测试文档。",
                    "status": "published",
                },
            ))
        doc_id = doc["id"] if doc else None
        if doc_id:
            self._cleanup_stack.append((f"/documents/{doc_id}", "文档"))

        if doc_id:
            self.step("查询文档", lambda: self.api("GET", f"/documents/{doc_id}"))
            self.step("更新文档", lambda: self.api(
                "PUT", f"/documents/{doc_id}",
                json={"title": f"测试文档_{ts}_updated", "content": "# 更新后\n\n内容已更新。"},
            ))
            self.step("文档列表", lambda: self.api(
                "GET", f"/documents?site_id={site_id}&page=1&size=10",
            ))

        # 5. 用户 CRUD + 缓存失效
        print("\n📋 用户")
        user = self.step("创建用户", lambda: self.api(
            "POST", "/users",
            json={"name": f"smoke_{ts}", "email": f"smoke_{ts}@test.com",
                  "password": "Test@12345", "role": "site_admin"},
        ))
        user_id = user["id"] if user else None
        if user_id:
            self._cleanup_stack.append((f"/users/{user_id}", "用户"))

        if user_id:
            self.step("查询用户", lambda: self.api("GET", f"/users/{user_id}"))
            self.step("更新用户", lambda: self.api(
                "PUT", f"/users/{user_id}", json={"name": f"smoke_{ts}_updated"},
            ))
            u = self.step("查询更新结果", lambda: self.api("GET", f"/users/{user_id}"))
            self.assert_field("缓存验证-用户更新", u, "name", f"smoke_{ts}_updated")

        # 6. 客户端 API 缓存验证
        print("\n📋 客户端缓存")
        if site_id:
            def client_get_site():
                return self.api("GET", f"/sites:bySlug/test-{ts}", prefix=CLIENT_API)

            c_site = self.step("客户端-Slug查站点", client_get_site)
            self.assert_field("客户端-数据一致性", c_site, "name", f"测试站点_{ts}_updated")

            self.step("管理端-二次更新站点", lambda: self.api(
                "PUT", f"/sites/{site_id}", json={"name": f"测试站点_{ts}_v2"},
            ))
            c_site2 = self.step("客户端-更新后查询", client_get_site)
            self.assert_field("客户端-缓存失效验证", c_site2, "name", f"测试站点_{ts}_v2")

        # 7. AI & 向量化（使用默认站点）
        if skip_ai:
            print("\n📋 AI & 向量化 (已跳过)")
        else:
            self._run_ai_tests()

        # 8. 缓存统计
        print("\n📋 缓存")
        self.step("缓存统计", lambda: self.api("GET", "/cache:stats"))

    def _run_ai_tests(self):
        """AI 相关测试，使用默认站点（租户1）"""
        print("\n📋 AI & 向量化 (默认站点)")

        ai_site = self.step("查找默认站点", lambda: self.api("GET", "/sites:bySlug/health"))
        ai_site_id = ai_site["id"] if ai_site else None
        ai_doc_id = None

        if ai_site_id:
            docs = self.step("查询站点文档", lambda: self.api(
                "GET", f"/documents?site_id={ai_site_id}&page=1&size=1",
            ))
            if docs and docs.get("list"):
                ai_doc_id = docs["list"][0]["id"]

        # 向量化
        if ai_doc_id:
            vec_doc = self.step("触发向量化", lambda: self.api(
                "POST", f"/documents/{ai_doc_id}:vectorize",
            ))
            if vec_doc:
                def wait_vectorize():
                    for _ in range(30):
                        d = self.api("GET", f"/documents/{ai_doc_id}")
                        vs = d.get("vector_status")
                        if vs == "completed":
                            return d
                        if vs == "failed":
                            raise AssertionError("向量化失败")
                        time.sleep(2)
                    raise AssertionError(f"向量化超时，当前状态: {vs}")
                self.step("等待向量化完成", wait_vectorize)

            self.step("查询文档切片", lambda: self.api("GET", f"/documents/{ai_doc_id}/chunks"))

        # 语义检索
        if ai_site_id:
            self.step("语义检索", lambda: self.api(
                "POST", "/documents/retrieve",
                json={"query": "健康", "k": 3, "filter": {"site_id": ai_site_id}},
            ))

        # AI 对话
        if ai_site_id:
            def do_chat():
                resp = self.client.post(f"{CLIENT_API}/chat/completions", json={
                    "message": "你好，请简单介绍一下这个知识库的内容",
                    "stream": False,
                    "filter": {"site_id": ai_site_id},
                }, timeout=60)
                body = resp.json()
                if resp.status_code >= 400:
                    raise AssertionError(f"{resp.status_code}: {body}")
                choices = body.get("choices", [])
                if not choices:
                    raise AssertionError("返回空 choices")
                content = choices[0].get("message", {}).get("content", "")
                if not content:
                    raise AssertionError("返回空内容")
                print(f"        💬 AI: {content[:80]}...")
                return body
            self.step("AI 对话(非流式)", do_chat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CatWiki 冒烟测试")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help=f"API 地址 (默认: {DEFAULT_BASE})")
    parser.add_argument("--skip-ai", action="store_true", help="跳过 AI 相关测试")
    args = parser.parse_args()

    test = SmokeTest(args.base_url)
    ok = test.run(skip_ai=args.skip_ai)
    sys.exit(0 if ok else 1)
