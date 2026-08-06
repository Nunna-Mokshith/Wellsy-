"""
Wellsy Trust Tier Safety System
Classifies operations into 4 trust levels:
- SAFE: Read-only operations (auto-execute)
- LOW_RISK: Reversible operations (execute + notify)
- HIGH_RISK: Irreversible or external communications (requires confirmation)
- DANGER: Destructive operations (requires explicit typed confirmation)
"""
from typing import Dict, Any, Tuple

# Default risk classification by tool name
TOOL_TRUST_TIERS = {
    # SAFE (Read-Only)
    "read_file": "SAFE",
    "list_files": "SAFE",
    "get_system_stats": "SAFE",
    "query_rag": "SAFE",
    "search_google_images": "SAFE",
    "list_scheduled_tasks": "SAFE",

    # LOW_RISK (Reversible / Local)
    "play_spotify": "LOW_RISK",
    "pause_spotify": "LOW_RISK",
    "set_volume": "LOW_RISK",
    "open_app": "LOW_RISK",
    "search_youtube": "LOW_RISK",

    # HIGH_RISK (External / State Changing)
    "send_whatsapp_message": "HIGH_RISK",
    "send_email": "HIGH_RISK",
    "git_commit": "HIGH_RISK",
    "git_push": "HIGH_RISK",
    "create_file": "HIGH_RISK",
    "schedule_task": "HIGH_RISK",

    # DANGER (Destructive / Mass operations)
    "delete_file": "DANGER",
    "git_push_force": "DANGER",
    "cancel_scheduled_task": "HIGH_RISK",
}

# Hard-coded rules that can NEVER be auto-approved
NEVER_AUTO_APPROVE_KEYWORDS = [
    "delete", "rmdir", "remove", "force", "format", "reset", "clear_memory"
]


class TrustTierEngine:
    def __init__(self):
        self.promotions = {}  # User-granted auto-approval overrides per tool

    def classify_action(self, tool_name: str, args: Dict[str, Any] = None) -> Tuple[str, bool]:
        """
        Classifies a tool action into (tier, requires_confirmation).
        Tiers: 'SAFE', 'LOW_RISK', 'HIGH_RISK', 'DANGER'
        """
        args = args or {}
        base_tier = TOOL_TRUST_TIERS.get(tool_name, "HIGH_RISK")

        # Check for dangerous keywords in arguments
        args_str = str(args).lower()
        if any(kw in args_str for kw in NEVER_AUTO_APPROVE_KEYWORDS):
            return "DANGER", True

        if base_tier == "SAFE":
            return "SAFE", False
        elif base_tier == "LOW_RISK":
            return "LOW_RISK", False
        elif base_tier == "HIGH_RISK":
            # Check if user promoted this tool action
            if self.promotions.get(tool_name) == "AUTO_APPROVE":
                return "HIGH_RISK", False
            return "HIGH_RISK", True
        else:
            return "DANGER", True

    def promote_tool(self, tool_name: str):
        """User explicitly promotes a HIGH_RISK tool to AUTO_APPROVE."""
        if tool_name not in TOOL_TRUST_TIERS or TOOL_TRUST_TIERS[tool_name] != "DANGER":
            self.promotions[tool_name] = "AUTO_APPROVE"

    def format_action_preview(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a human-readable action preview for the user confirmation modal."""
        tier, _ = self.classify_action(tool_name, args)
        
        summary = f"Execute action '{tool_name}'"
        details = []

        if tool_name == "send_whatsapp_message":
            summary = f"Send WhatsApp message to {args.get('contact', 'contact')}"
            details.append(f"Message: \"{args.get('message', '')}\"")
        elif tool_name in ("git_commit", "git_push"):
            summary = f"Git Push / Commit to repository"
            details.append(f"Commit Message: \"{args.get('message', 'Update')}\"")
            details.append(f"Target: {args.get('target', 'current branch')}")
        elif tool_name == "create_file":
            summary = f"Create file '{args.get('filename', 'file')}'"
            details.append(f"Path: {args.get('path', './')}")
        elif tool_name == "delete_file":
            summary = f"⚠️ DELETE File '{args.get('filename', 'file')}'"
            details.append("WARNING: This operation is permanent.")

        for k, v in args.items():
            if k not in ("message", "contact", "filename", "path", "target"):
                details.append(f"{k}: {v}")

        return {
            "tool_name": tool_name,
            "tier": tier,
            "summary": summary,
            "details": details,
            "args": args
        }


trust_engine = TrustTierEngine()
