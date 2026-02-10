import sys
import os
import asyncio
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


# Mock State
class MockState(TypedDict):
    iteration_count: int
    messages: list


async def test_state_persistence_reset():
    print("Testing state persistence reset...")

    # 1. Define a simple graph that increments iteration_count
    def node_a(state):
        print(f"  [Node A] Received iteration_count: {state.get('iteration_count')}")
        return {"iteration_count": state.get("iteration_count", 0) + 1}

    builder = StateGraph(MockState)
    builder.add_node("a", node_a)
    builder.add_edge(START, "a")
    builder.add_edge("a", END)

    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "test_thread"}}

    # 2. Simulate Turn 1: Standard run
    print("\n--- Turn 1 ---")
    # Initial input: count=0
    await graph.ainvoke({"iteration_count": 0, "messages": []}, config)
    # State should be 1
    state = await graph.aget_state(config)
    print(f"  [Turn 1 End] State iteration_count: {state.values['iteration_count']}")
    assert state.values["iteration_count"] == 1

    # 3. Simulate Turn 2: Without reset (Problem Case)
    print("\n--- Turn 2 (Simulating Problem: No Reset) ---")
    # If we DON'T pass iteration_count in input, it should persist
    await graph.ainvoke({"messages": []}, config)
    state = await graph.aget_state(config)
    print(f"  [Turn 2 End] State iteration_count: {state.values['iteration_count']}")
    assert state.values["iteration_count"] == 2  # Persisted and incremented

    # 4. Simulate Turn 3: With Reset (Fix Case)
    print("\n--- Turn 3 (Simulating Fix: With Reset) ---")
    # Pass iteration_count=0 in input
    await graph.ainvoke({"iteration_count": 0, "messages": []}, config)
    state = await graph.aget_state(config)
    print(f"  [Turn 3 End] State iteration_count: {state.values['iteration_count']}")
    # Should be 1 (0 + 1), NOT 3
    assert state.values["iteration_count"] == 1

    print("\n✅ Verification Successful: Input keys overwrite state (reset works).")


if __name__ == "__main__":
    asyncio.run(test_state_persistence_reset())
