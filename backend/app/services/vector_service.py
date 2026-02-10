import logging
import time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.core.config import settings
from app.core.vector_store import VectorStoreManager
from app.core.reranker import reranker
from app.schemas.document import VectorRetrieveResponse, VectorRetrieveFilter

logger = logging.getLogger(__name__)


class VectorService:
    """向量检索服务 (RAG的核心逻辑)"""

    @classmethod
    async def retrieve(
        cls,
        query: str,
        k: int = 5,
        threshold: float = 0.0,
        filter: Optional[VectorRetrieveFilter] = None,
        enable_rerank: Optional[bool] = None,
        rerank_k: Optional[int] = None,
    ) -> List[VectorRetrieveResponse]:
        """
        执行语义检索（包含 召回 + 重排序）
        """
        logger.info(
            "\n"
            + "=" * 80
            + f"\n🚀 [VECTOR RETRIEVAL START]\n"
            + f"   Query: '{query}'\n"
            + f"   Params: k={k}, threshold={threshold}\n"
            + f"   Filter: {filter.model_dump() if filter else 'None'}\n"
            + "=" * 80
        )
        start_time = time.time()

        try:
            vector_store = await VectorStoreManager.get_instance()

            # 1. 构建动态过滤器
            filter_dict = {}
            if filter:
                # 只有当 site_id > 0 时才过滤站点；0 表示全局搜索
                if filter.site_id is not None and filter.site_id > 0:
                    filter_dict["site_id"] = filter.site_id
                if filter.id is not None:
                    filter_dict["id"] = str(filter.id)
                if filter.source is not None:
                    filter_dict["source"] = filter.source

            # 2. 决定检索数量
            # 确保 Reranker 配置是最新的
            await reranker._ensure_config()

            # 不需要合并时，召回深度可以适度减小，或者维持现状给精排留空间
            do_rerank = enable_rerank if enable_rerank is not None else reranker.is_enabled
            recall_k = rerank_k * 5 if (do_rerank and rerank_k) else k * 10
            recall_k = min(max(recall_k, 50), 100)  # 保持在 50-100 之间

            logger.debug(f"🔍 [Retrieve] 初始召回深度: {recall_k} | Rerank: {do_rerank}")

            # 3. 执行相似度搜索
            results = await vector_store.similarity_search_with_score(
                query=query, k=recall_k, filter=filter_dict if filter_dict else None
            )

            # 4. 转换候选集 (直接转换，不进行合并)
            candidate_list = []
            if results:
                for doc, distance in results:
                    similarity = 1.0 - distance
                    if similarity < threshold:
                        continue

                    candidate_list.append(
                        {
                            "content": doc.page_content,
                            "score": similarity,
                            "document_id": int(doc.metadata.get("id", 0)),
                            "document_title": doc.metadata.get("title"),
                            "metadata": doc.metadata,
                            "original_score": similarity,
                        }
                    )

            # 5. 执行重排序 (如果启用)
            final_list = []
            if do_rerank and candidate_list:
                final_k = rerank_k or k
                final_list = await reranker.rerank(
                    query=query, documents=candidate_list, top_n=final_k
                )
            else:
                # 没启用 Rerank 则按分数排序取 top k
                candidate_list.sort(key=lambda x: x["score"], reverse=True)
                final_list = candidate_list[:k]

            # 6. 转换为响应对象
            response_objects = [VectorRetrieveResponse(**item) for item in final_list]

            # 日志
            log_lines = [f"✅ [Retrieve] 最终返回结果数: {len(response_objects)}"]
            for i, res in enumerate(response_objects):
                score_str = f"Score={res.score:.4f}"
                if res.original_score is not None and res.score != res.original_score:
                    score_str = f"Original={res.original_score:.4f} -> Final={res.score:.4f}"
                log_lines.append(
                    f"   #{i + 1}: {score_str} | Title: {res.document_title[:40] if res.document_title else 'N/A'}"
                )

            logger.info("\n" + "\n".join(log_lines))

            return response_objects

        except Exception as e:
            logger.error(f"❌ [Retrieve] 检索服务严重异常: {str(e)}", exc_info=True)
            # 根据错误类型提供更具体的提示（可选）
            if "AuthenticationError" in str(e):
                logger.error("🔑 [Retrieve] 可能是 Embedding 或 Reranker 认证失败")
            elif "ConnectionError" in str(e):
                logger.error("🌐 [Retrieve] 无法连接到向量数据库或模型服务")

            # 返回空列表以保证下游系统不崩溃，但在日志中留痕
            return []
