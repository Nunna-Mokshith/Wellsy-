"""
Wellsy Confirmation Gate Middleware
Intercepts high-risk tool actions, registers pending confirmations, and waits for user response.
"""
import asyncio
from typing import Dict, Any, Optional

from safety.trust_tiers import trust_engine


class ConfirmationGate:
    def __init__(self):
        self.pending_requests: Dict[str, asyncio.Event] = {}
        self.user_decisions: Dict[str, bool] = {}

    async def request_approval(self, request_id: str, tool_name: str, args: Dict[str, Any], send_ws_func) -> bool:
        """
        Sends an approval request to the frontend and waits for response.
        Returns True if approved, False if rejected or timed out.
        """
        preview = trust_engine.format_action_preview(tool_name, args)
        preview["request_id"] = request_id

        # Register event listener
        event = asyncio.Event()
        self.pending_requests[request_id] = event

        # Notify frontend
        await send_ws_func({
            "type": "confirmation_request",
            "preview": preview
        })

        try:
            # Wait up to 60 seconds for user decision
            await asyncio.wait_for(event.wait(), timeout=60.0)
            approved = self.user_decisions.get(request_id, False)
            return approved
        except asyncio.TimeoutError:
            print(f"[!] Confirmation request #{request_id} timed out.")
            return False
        finally:
            self.pending_requests.pop(request_id, None)
            self.user_decisions.pop(request_id, None)

    def resolve_approval(self, request_id: str, approved: bool):
        """Called when WebSocket receives confirmation_response from frontend."""
        if request_id in self.pending_requests:
            self.user_decisions[request_id] = approved
            self.pending_requests[request_id].set()


confirmation_gate = ConfirmationGate()
