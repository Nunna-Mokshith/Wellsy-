"""
Wellsy Multi-Agent System — Specialized Sub-Agents & Prompts
Defines the domain-specific sub-agents, tool groupings, and prompts.
"""
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# Core tools
from tools.files import FILE_TOOLS
from tools.apps import APP_TOOLS
from tools.system import SYSTEM_TOOLS
from tools.clipboard import CLIPBOARD_TOOLS

# Driver tools
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


# === Domain Tool Bindings ===
MEDIA_TOOLS = SPOTIFY_TOOLS + YOUTUBE_TOOLS
COMMS_TOOLS = WHATSAPP_TOOLS + GMAIL_TOOLS + OUTLOOK_TOOLS
OS_TOOLS = FILE_TOOLS + APP_TOOLS + SYSTEM_TOOLS + CLIPBOARD_TOOLS
RESEARCH_TOOLS = GEMINI_CHAT_TOOLS + GOOGLE_IMAGES_TOOLS + OVERLEAF_TOOLS

# === Domain System Prompts ===
SUPERVISOR_PROMPT = """You are the Supervisor of Wellsy (Jarvis-class AI Multi-Agent System).
Your job is to analyze the user request and select the appropriate specialized sub-agent to handle it, or FINISH if no specialized agent is needed.

Available Options:
- MediaAgent: For Spotify playback, YouTube video searches, media controls.
- CommsAgent: For WhatsApp messaging, reading chats, Gmail, Outlook email tasks.
- OSAgent: For file operations (read/create/list/search), launching/closing desktop apps, system stats, volume/brightness, clipboard.
- ResearchAgent: For deep research, Google Images, RAG local knowledge search, Overleaf project management.
- FINISH: Use this when the request is complete, or if it is a general conversational greeting/question that requires no special tools.

Respond with ONLY the exact name of the agent to invoke (MediaAgent, CommsAgent, OSAgent, ResearchAgent, or FINISH). Do not include extra text.
"""

MEDIA_AGENT_PROMPT = """You are Wellsy's Media Sub-Agent 🎵.
You specialize in controlling Spotify playback, searching for music, volume controls, and YouTube video searches.
Keep responses concise, executive, and Jarvis-like. Use your media tools when needed.
"""

COMMS_AGENT_PROMPT = """You are Wellsy's Communications Sub-Agent 💬.
You specialize in messaging via WhatsApp Desktop, reading chats, drafting and checking Gmail/Outlook emails.
Keep responses clear, executive, and Jarvis-like. Execute tasks safely and confirm actions.
"""

OS_AGENT_PROMPT = """You are Wellsy's System & OS Sub-Agent 🖥️.
You specialize in Windows OS management: opening/closing apps, file creation/reading/searching, checking CPU/RAM/Battery, setting brightness/volume, and managing the clipboard.
Keep responses direct, executive, and Jarvis-like.
"""

RESEARCH_AGENT_PROMPT = """You are Wellsy's Research & Data Sub-Agent 🔬.
You specialize in web research, searching local knowledge bases (RAG), fetching Google Images, and managing Overleaf LaTeX projects.
Provide insightful, concise, and structured answers.
"""
