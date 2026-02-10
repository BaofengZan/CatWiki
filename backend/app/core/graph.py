
"""LangGraph ReAct Agent
1. ReAct 循环: Agent -> Tools -> Agent ... -> End
2. 支持多轮检索和推理
3. 动态引用提取
"""

import logging
import json
from typing import Literal, List, Annotated

from langchain_core.messages import SystemMessage, BaseMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig

from app.schemas.graph_state import ChatGraphState
from app.services.vector_service import VectorService
from app.schemas.document import VectorRetrieveFilter
from app.core.prompts import SYSTEM_PROMPT, NO_RESULTS_MESSAGE

logger = logging.getLogger(__name__)

# 最大迭代次数限制，防止 Agent 无限循环（从配置读取）
from app.core.config import settings

MAX_ITERATIONS = settings.AGENT_MAX_ITERATIONS


# =============================================================================
# 工具定义
# =============================================================================


@tool
async def search_knowledge_base(query: str, config: RunnableConfig) -> str:
    """在知识库中搜索相关信息。

    当用户的问题需要事实依据、文档支持或你不知道答案时，**必须**使用此工具。
    可以多次调用此工具以查找不同方面的信息。

    Args:
        query: 搜索查询词。应该是针对特定信息的清晰问题。

    Returns:
        JSON 格式的字符串，包含搜索结果列表。
        每个结果包含 'content' (内容摘录) 和 'metadata' (包含 title, document_id 等)。
    """
    # 获取站点上下文
    site_id = config.get("configurable", {}).get("site_id")
    logger.info(f"🔧 [Tool] search_knowledge_base: query='{query}', site_id={site_id}")

    try:
        search_filter = VectorRetrieveFilter(site_id=int(site_id)) if site_id else None

        # 执行检索
        retrieved_docs = await VectorService.retrieve(
            query=query,
            k=5,
            threshold=0.3,
            filter=search_filter,
        )

        if not retrieved_docs:
            return NO_RESULTS_MESSAGE

        # 格式化结果
        results = [
            {
                "content": doc.content,
                "metadata": {
                    "document_id": doc.document_id,
                    "title": doc.document_title,
                    "score": doc.score,
                    **doc.metadata,
                },
            }
            for doc in retrieved_docs
        ]

        return json.dumps(results, ensure_ascii=False)

    except Exception as e:
        logger.error(f"❌ [Tool] Knowledge base search failed: {e}", exc_info=True)
        return f"搜索知识库时出错: {str(e)}"


# 工具列表
tools = [search_knowledge_base]


# =============================================================================
# 辅助函数：引用提取
# =============================================================================


def extract_citations_from_messages(messages: List[BaseMessage], from_last_turn: bool = False) -> List[dict]:
    """从历史消息的 ToolMessage 中提取引用

    Args:
        messages: 消息列表
        from_last_turn: 是否仅提取最后一轮对话的引用 (从最后一条 HumanMessage 开始)
    """
    citations = {}
    target_messages = messages

    if from_last_turn:
        # 找到最后一条 HumanMessage 的索引
        last_human_idx = -1
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_idx = i
                break
        
        if last_human_idx != -1:
            target_messages = messages[last_human_idx:]

    for msg in target_messages:
        if isinstance(msg, ToolMessage) and msg.name == "search_knowledge_base":
            try:
                content = msg.content if isinstance(msg.content, str) else json.dumps(msg.content)
                results = json.loads(content)
                
                if isinstance(results, list):
                    for doc in results:
                        meta = doc.get("metadata", {})
                        doc_id = meta.get("document_id")
                        if doc_id and doc_id not in citations:
                            citations[doc_id] = {
                                "id": str(doc_id),
                                "title": meta.get("title", "Unknown"),
                                "siteId": meta.get("site_id"),
                                "documentId": doc_id,
                                "score": meta.get("score"),
                            }
            except (json.JSONDecodeError, AttributeError):
                continue
            except Exception as e:
                logger.error(f"❌ Error extracting citations: {e}")

    return list(citations.values())


# =============================================================================
# Agent 图构建
# =============================================================================


def create_agent_graph(checkpointer=None, model: ChatOpenAI = None):
    """创建 ReAct Agent 图

    Args:
        checkpointer: 可选的 Checkpointer 实例
        model: 配置好的 LLM 实例 (必须支持 bind_tools)

    Returns:
        编译后的 StateGraph
    """
    if model is None:
        raise ValueError("Model must be provided to create_agent_graph")

    # 1. 绑定工具到模型
    model_with_tools = model.bind_tools(tools)

    # 2. 定义节点
    async def agent_node(state: ChatGraphState) -> dict:
        """Agent 决策节点"""
        logger.debug("🤖 [Agent] Thinking...")
        messages = state["messages"]

        # 确保 SystemPrompt 存在


        # 注入 System Prompt
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # 3. 构建图
    graph_builder = StateGraph(ChatGraphState)

    # 工具节点包装器：递增迭代计数 + 检测空结果
    tool_node = ToolNode(tools)

    # 连续空结果终止阈值（从配置读取）
    MAX_CONSECUTIVE_EMPTY = settings.AGENT_MAX_CONSECUTIVE_EMPTY

    async def tools_wrapper_node(state: ChatGraphState) -> dict:
        """工具节点包装器，执行工具并追踪迭代计数和空结果"""
        # 调用原始工具节点
        result = await tool_node.ainvoke(state)

        # 递增迭代计数
        current_count = state.get("iteration_count", 0)
        result["iteration_count"] = current_count + 1

        # 检测工具返回是否为空结果
        consecutive_empty = state.get("consecutive_empty_count", 0)
        is_empty_result = False

        # 检查最后一条工具消息是否为空结果
        if result.get("messages"):
            last_tool_msg = result["messages"][-1] if result["messages"] else None
            if last_tool_msg:
                content = getattr(last_tool_msg, "content", "")
                # 检测空结果标志
                if content == NO_RESULTS_MESSAGE or "未找到相关文档" in content or content == "[]":
                    is_empty_result = True

        if is_empty_result:
            result["consecutive_empty_count"] = consecutive_empty + 1
            logger.debug(
                f"🔄 [Graph] Empty result, consecutive count: {result['consecutive_empty_count']}/{MAX_CONSECUTIVE_EMPTY}"
            )
        else:
            result["consecutive_empty_count"] = 0  # 重置

        logger.debug(f"🔄 [Graph] Iteration count: {result['iteration_count']}/{MAX_ITERATIONS}")
        return result

    # 条件路由函数：检查迭代次数限制 + 连续空结果
    def route_after_agent(state: ChatGraphState) -> Literal["tools", "__end__"]:
        """Agent 后的路由决策，包含迭代次数和连续空结果检查"""
        messages = state["messages"]
        last_message = messages[-1] if messages else None

        # 检查是否需要调用工具
        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # 检查迭代次数
            current_count = state.get("iteration_count", 0)
            if current_count >= MAX_ITERATIONS:
                logger.warning(f"⚠️ [Graph] Max iterations ({MAX_ITERATIONS}) reached, forcing end")
                return "__end__"

            # 检查连续空结果
            consecutive_empty = state.get("consecutive_empty_count", 0)
            if consecutive_empty >= MAX_CONSECUTIVE_EMPTY:
                logger.warning(
                    f"⚠️ [Graph] {MAX_CONSECUTIVE_EMPTY} consecutive empty results, stopping early"
                )
                return "__end__"

            return "tools"

        return "__end__"

    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", tools_wrapper_node)

    # 4. 定义边
    graph_builder.add_edge(START, "agent")

    # 条件边: Agent -> (Tools | END)，包含迭代次数检查
    graph_builder.add_conditional_edges(
        "agent",
        route_after_agent,
    )

    # 循环边: Tools -> Agent
    graph_builder.add_edge("tools", "agent")

    return graph_builder.compile(checkpointer=checkpointer)


# =============================================================================
# 辅助函数
# =============================================================================



