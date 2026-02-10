
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.core.graph import create_agent_graph
from app.core.config import settings
from unittest.mock import MagicMock, AsyncMock

async def test_summarization_trigger():
    print(f"🔧 Testing Summarization Trigger...")
    print(f"⚙️ Config: AGENT_SUMMARY_TRIGGER_MSG_COUNT={settings.AGENT_SUMMARY_TRIGGER_MSG_COUNT}")

    # 1. Create a mock model
    mock_model = AsyncMock()
    # Mock bind_tools to return the model itself (synchronously)
    mock_model.bind_tools = MagicMock(return_value=mock_model)
    
    # Mock ainvoke to return a summary when prompted
    async def mock_ainvoke(messages, **kwargs):
        # Helper to extract text content
        content_buffer = []
        for m in messages:
            if isinstance(m.content, str):
                content_buffer.append(m.content)
            elif isinstance(m.content, list):
                 for block in m.content:
                     if isinstance(block, dict) and 'text' in block:
                         content_buffer.append(block['text'])
        
        full_text = " ".join(content_buffer)

        # Check for summary prompt
        if "请逐步概括目前的对话内容" in full_text:
            print("✨ [MockModel] Summarization Prompt Detected!")
            return AIMessage(content="[MOCKED SUMMARY] This is a summary of the conversation.")
        
        print("🤖 [MockModel] Generating normal response...")
        return AIMessage(content="[MOCKED RESPONSE] I am a mock response.")
        
    mock_model.ainvoke = mock_ainvoke

    # 2. Create the graph
    graph = create_agent_graph(model=mock_model)

    # 3. Create a state with MANY messages to trigger threshold
    # Trigger is > 10 non-system messages
    # Let's create 12 messages
    messages = [SystemMessage(content="System")]
    for i in range(6):
        messages.append(HumanMessage(content=f"Question {i}"))
        messages.append(AIMessage(content=f"Answer {i}"))
    
    initial_count = len([m for m in messages if not isinstance(m, SystemMessage)])
    print(f"📊 Initial non-system message count: {initial_count}")
    
    # 4. Run the graph
    # We invoke with a new user message
    new_message = HumanMessage(content="Trigger Question")
    # Note: create_agent_graph execution usually starts with existing state + new input
    # If we pass all messages in input, they are the state.
    
    messages.append(new_message)
    input_state = {"messages": messages}
    
    print("🚀 Running graph...")
    
    # Use ainvoke
    final_state = await graph.ainvoke(input_state)
    
    # 5. Verify Results
    print("\n🏁 Validation Results:")
    
    # A. Check Summary
    summary = final_state.get("summary")
    if summary == "[MOCKED SUMMARY] This is a summary of the conversation.":
        print("✅ SUCCESS: Summary was generated and stored.")
    else:
        print(f"❌ FAILURE: Summary mismatch. Got: '{summary}'")

    # B. Check Message Pruning
    # The summarization node should have removed messages
    # It keeps last 6 non-system messages + system message + potentially new ones?
    # Logic in graph.py:
    # conversation_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
    # delete_messages = [RemoveMessage(id=m.id) for m in conversation_messages[:-6]]
    
    # Checking final state messages list might be complex because RemoveMessage logic 
    # happens in the state update. LangGraph applies edits. 
    # So final_state["messages"] should contain fewer messages.
    
    final_msgs = final_state["messages"]
    final_non_sys = [m for m in final_msgs if not isinstance(m, SystemMessage)]
    print(f"📊 Final non-system message count: {len(final_non_sys)}")
    
    # We expect roughly 6 (kept) + 1 (new Answer from agent) = 7? or just 6 range.
    if len(final_non_sys) < initial_count:
        print(f"✅ SUCCESS: Messages were pruned (Count {initial_count} -> {len(final_non_sys)}).")
    else:
        print(f"❌ FAILURE: Messages were NOT pruned. Count remains {len(final_non_sys)}.")

if __name__ == "__main__":
    asyncio.run(test_summarization_trigger())
