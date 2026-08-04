"""
Wellsy Brain — Multi-Agent Architecture
Supervisor-Worker pattern orchestrating domain-specific sub-agents:
- MediaAgent (Spotify, YouTube)
- CommsAgent (WhatsApp, Gmail, Outlook)
- OSAgent (Files, Desktop Apps, System Settings, Clipboard)
- ResearchAgent (RAG, Google Images, Gemini Chat, Overleaf)
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_FLASH_MODEL,
    GEMINI_PRO_MODEL,
    WELLSY_SYSTEM_PROMPT,
)
from agent.rate_limiter import RateLimitManager
from agent.agents import (
    MEDIA_TOOLS,
    COMMS_TOOLS,
    OS_TOOLS,
    RESEARCH_TOOLS,
    SUPERVISOR_PROMPT,
    MEDIA_AGENT_PROMPT,
    COMMS_AGENT_PROMPT,
    OS_AGENT_PROMPT,
    RESEARCH_AGENT_PROMPT,
)

# === State Definition ===
class WellsyState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str


# === Rate Limit Manager ===
rate_limiter = RateLimitManager()


def get_base_llm(model_type: str = "flash"):
    model_name = GEMINI_PRO_MODEL if model_type == "pro" else GEMINI_FLASH_MODEL
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY,
        temperature=0.7,
        convert_system_message_to_human=False,
    )


def get_agent_llm(tools: list, complexity: str = "medium"):
    model_choice = rate_limiter.pick_model(complexity)
    llm = get_base_llm("pro" if model_choice == "pro" else "flash")
    if tools:
        return llm.bind_tools(tools), model_choice
    return llm, model_choice


# === Supervisor Node ===
def supervisor_node(state: WellsyState):
    """Supervisor router node — decides which specialized subagent handles the request."""
    messages = state["messages"]
    
    # If the last message is already a final AIMessage from a subagent (without tool calls), we FINISH
    last_msg = messages[-1] if messages else None
    if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
        return {"next_agent": "FINISH"}

    prompt = SystemMessage(content=SUPERVISOR_PROMPT)
    llm = get_base_llm("flash")
    
    rate_limiter.record_request(is_pro=False)
    response = llm.invoke([prompt] + messages)
    
    choice = response.content.strip()
    valid_agents = ["MediaAgent", "CommsAgent", "OSAgent", "ResearchAgent", "FINISH"]
    
    selected_agent = "FINISH"
    for agent in valid_agents:
        if agent.lower() in choice.lower():
            selected_agent = agent
            break
            
    print(f"[Supervisor] Routing task to: {selected_agent}")
    return {"next_agent": selected_agent}


def route_supervisor(state: WellsyState) -> str:
    """Route from supervisor node to sub-agents or END."""
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "MediaAgent":
        return "media_agent"
    elif next_agent == "CommsAgent":
        return "comms_agent"
    elif next_agent == "OSAgent":
        return "os_agent"
    elif next_agent == "ResearchAgent":
        return "research_agent"
    return END


# === Domain Sub-Agent Nodes ===
def make_agent_node(agent_name: str, system_prompt: str, tools: list):
    """Factory to create a domain sub-agent node."""
    def agent_node(state: WellsyState):
        messages = state["messages"]
        
        domain_sys_msg = SystemMessage(content=system_prompt)
        full_messages = [domain_sys_msg] + [m for m in messages if not isinstance(m, SystemMessage)]
        
        llm, model_used = get_agent_llm(tools, complexity="medium")
        rate_limiter.record_request(is_pro=(model_used == "pro"))
        
        response = llm.invoke(full_messages)
        print(f"[{agent_name}] Responded (Tool calls: {bool(response.tool_calls)})")
        return {"messages": [response]}
        
    return agent_node


def should_continue_tools(state: WellsyState, tools_node_name: str) -> str:
    """Check if the last message in state contains tool calls."""
    messages = state["messages"]
    last_msg = messages[-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return tools_node_name
    return "supervisor"


# Create node functions
media_agent_node = make_agent_node("MediaAgent", MEDIA_AGENT_PROMPT, MEDIA_TOOLS)
comms_agent_node = make_agent_node("CommsAgent", COMMS_AGENT_PROMPT, COMMS_TOOLS)
os_agent_node = make_agent_node("OSAgent", OS_AGENT_PROMPT, OS_TOOLS)
research_agent_node = make_agent_node("ResearchAgent", RESEARCH_AGENT_PROMPT, RESEARCH_TOOLS)


# === Build the Multi-Agent Graph ===
def create_wellsy_multi_agent():
    """Create and compile the Wellsy Multi-Agent graph."""
    graph = StateGraph(WellsyState)
    
    # 1. Add Supervisor
    graph.add_node("supervisor", supervisor_node)
    
    # 2. Add Domain Agents
    graph.add_node("media_agent", media_agent_node)
    graph.add_node("comms_agent", comms_agent_node)
    graph.add_node("os_agent", os_agent_node)
    graph.add_node("research_agent", research_agent_node)
    
    # 3. Add Domain Tools Nodes
    if MEDIA_TOOLS:
        graph.add_node("media_tools", ToolNode(MEDIA_TOOLS))
    if COMMS_TOOLS:
        graph.add_node("comms_tools", ToolNode(COMMS_TOOLS))
    if OS_TOOLS:
        graph.add_node("os_tools", ToolNode(OS_TOOLS))
    if RESEARCH_TOOLS:
        graph.add_node("research_tools", ToolNode(RESEARCH_TOOLS))
        
    # Set Entry Point
    graph.set_entry_point("supervisor")
    
    # Conditional Edges from Supervisor
    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "media_agent": "media_agent",
            "comms_agent": "comms_agent",
            "os_agent": "os_agent",
            "research_agent": "research_agent",
            END: END,
        }
    )
    
    # Conditional Edges from Sub-Agents to Tools or back to Supervisor
    graph.add_conditional_edges(
        "media_agent",
        lambda state: should_continue_tools(state, "media_tools" if MEDIA_TOOLS else "supervisor"),
        {"media_tools": "media_tools" if MEDIA_TOOLS else "supervisor", "supervisor": "supervisor"}
    )
    if MEDIA_TOOLS:
        graph.add_edge("media_tools", "media_agent")
        
    graph.add_conditional_edges(
        "comms_agent",
        lambda state: should_continue_tools(state, "comms_tools" if COMMS_TOOLS else "supervisor"),
        {"comms_tools": "comms_tools" if COMMS_TOOLS else "supervisor", "supervisor": "supervisor"}
    )
    if COMMS_TOOLS:
        graph.add_edge("comms_tools", "comms_agent")
        
    graph.add_conditional_edges(
        "os_agent",
        lambda state: should_continue_tools(state, "os_tools" if OS_TOOLS else "supervisor"),
        {"os_tools": "os_tools" if OS_TOOLS else "supervisor", "supervisor": "supervisor"}
    )
    if OS_TOOLS:
        graph.add_edge("os_tools", "os_agent")
        
    graph.add_conditional_edges(
        "research_agent",
        lambda state: should_continue_tools(state, "research_tools" if RESEARCH_TOOLS else "supervisor"),
        {"research_tools": "research_tools" if RESEARCH_TOOLS else "supervisor", "supervisor": "supervisor"}
    )
    if RESEARCH_TOOLS:
        graph.add_edge("research_tools", "research_agent")

    return graph.compile()


# Compile agent
wellsy_agent = create_wellsy_multi_agent()


async def chat(user_message: str, history: list = None) -> tuple[str, dict]:
    """
    Send a message to Wellsy Multi-Agent system and get a response.
    Returns: (response_text, rate_limit_status)
    """
    if history is None:
        history = []

    # Build message list
    messages = [SystemMessage(content=WELLSY_SYSTEM_PROMPT)]
    messages.extend(history)
    messages.append(HumanMessage(content=user_message))

    # Run the multi-agent graph
    result = wellsy_agent.invoke({"messages": messages}, config={"recursion_limit": 15})

    # Extract the final AI response
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content and not m.tool_calls]

    if ai_messages:
        raw_content = ai_messages[-1].content
        if isinstance(raw_content, list):
            text_parts = []
            for part in raw_content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            response_text = "\n".join(text_parts)
        else:
            response_text = str(raw_content)
    else:
        response_text = "All requested actions have been completed, Moksh."

    status = rate_limiter.get_status()
    return response_text, status
