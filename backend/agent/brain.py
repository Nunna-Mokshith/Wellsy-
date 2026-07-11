"""
Wellsy Brain — The LangGraph Agent
This is the core intelligence. It receives commands, reasons about them,
picks tools, executes actions, and responds in Wellsy's personality.
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

# Core tools
from tools.files import FILE_TOOLS
from tools.apps import APP_TOOLS
from tools.system import SYSTEM_TOOLS
from tools.clipboard import CLIPBOARD_TOOLS

# App drivers
try:
    from tools.spotify import SPOTIFY_TOOLS
except ImportError:
    SPOTIFY_TOOLS = []
try:
    from tools.youtube import YOUTUBE_TOOLS
except ImportError:
    YOUTUBE_TOOLS = []
try:
    from tools.whatsapp import WHATSAPP_TOOLS
except ImportError:
    WHATSAPP_TOOLS = []
try:
    from tools.gmail import GMAIL_TOOLS
except ImportError:
    GMAIL_TOOLS = []
try:
    from tools.outlook import OUTLOOK_TOOLS
except ImportError:
    OUTLOOK_TOOLS = []
try:
    from tools.gemini_chat import GEMINI_CHAT_TOOLS
except ImportError:
    GEMINI_CHAT_TOOLS = []
try:
    from tools.google_images import GOOGLE_IMAGES_TOOLS
except ImportError:
    GOOGLE_IMAGES_TOOLS = []
try:
    from tools.overleaf import OVERLEAF_TOOLS
except ImportError:
    OVERLEAF_TOOLS = []


# === State Definition ===
class WellsyState(TypedDict):
    messages: Annotated[list, add_messages]


# === All Available Tools ===
ALL_TOOLS = (
    FILE_TOOLS + APP_TOOLS + SYSTEM_TOOLS + CLIPBOARD_TOOLS +
    SPOTIFY_TOOLS + YOUTUBE_TOOLS + WHATSAPP_TOOLS + GMAIL_TOOLS +
    OUTLOOK_TOOLS + GEMINI_CHAT_TOOLS + GOOGLE_IMAGES_TOOLS + OVERLEAF_TOOLS
)


# === Rate Limit Manager ===
rate_limiter = RateLimitManager()


def get_llm(complexity: str = "medium"):
    """Get the appropriate LLM based on task complexity and budget."""
    model_choice = rate_limiter.pick_model(complexity)

    if model_choice == "pro":
        model_name = GEMINI_PRO_MODEL
    else:
        model_name = GEMINI_FLASH_MODEL

    # For 'ollama' fallback, we still use Flash for now
    # (Ollama integration comes in Phase 2)
    # TODO: Add Ollama local model support

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY,
        temperature=0.7,
        convert_system_message_to_human=False,
    )
    return llm.bind_tools(ALL_TOOLS), model_choice


# === Agent Nodes ===
def wellsy_think(state: WellsyState):
    """Wellsy's thinking node — processes input and decides what to do."""
    messages = state["messages"]

    # Add system prompt if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=WELLSY_SYSTEM_PROMPT)] + messages

    # Classify complexity based on message content
    last_msg = messages[-1].content if messages else ""
    complexity = classify_complexity(last_msg)

    # Get appropriate LLM
    llm, model_used = get_llm(complexity)

    # Record the API request
    rate_limiter.record_request(is_pro=(model_used == "pro"))

    # Generate response
    response = llm.invoke(messages)

    return {"messages": [response]}


def classify_complexity(text: str) -> str:
    """Quick heuristic to classify task complexity."""
    text_lower = text.lower()

    # Simple tasks — can be handled locally
    simple_keywords = ["open", "close", "launch", "volume", "brightness", "time", "battery"]
    if any(kw in text_lower for kw in simple_keywords) and len(text_lower.split()) < 8:
        return "simple"

    # Complex tasks — need deeper reasoning
    complex_keywords = [
        "analyze", "compare", "explain", "research", "summarize",
        "plan", "design", "debug", "review", "create a", "write a",
        "help me with", "figure out",
    ]
    if any(kw in text_lower for kw in complex_keywords):
        return "complex"

    # Default to medium
    return "medium"


def should_continue(state: WellsyState) -> Literal["tools", "__end__"]:
    """Decide if we should call tools or end the conversation turn."""
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    return "__end__"


# === Build the Graph ===
def create_wellsy_agent():
    """Create and compile the Wellsy agent graph."""
    graph = StateGraph(WellsyState)

    # Add nodes
    graph.add_node("think", wellsy_think)
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    # Set entry point
    graph.set_entry_point("think")

    # Add edges
    graph.add_conditional_edges("think", should_continue)
    graph.add_edge("tools", "think")  # After using tools, think again

    # Compile
    return graph.compile()


# === Create the agent instance ===
wellsy_agent = create_wellsy_agent()


async def chat(user_message: str, history: list = None) -> tuple[str, dict]:
    """
    Send a message to Wellsy and get a response.
    Returns: (response_text, rate_limit_status)
    """
    if history is None:
        history = []

    # Build message list
    messages = [SystemMessage(content=WELLSY_SYSTEM_PROMPT)]
    messages.extend(history)
    messages.append(HumanMessage(content=user_message))

    # Run the agent
    result = wellsy_agent.invoke({"messages": messages})

    # Extract the final AI response
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content and not m.tool_calls]

    if ai_messages:
        raw_content = ai_messages[-1].content
        # Gemini sometimes returns content as a list of dicts
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
        response_text = "Hmm, something went sideways. Try again?"

    # Get rate limit status
    status = rate_limiter.get_status()

    return response_text, status
