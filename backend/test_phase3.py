"""
Wellsy Phase 3 Verification Test Suite
Tests Trust Tier Engine classification, dangerous keyword detection, and Confirmation Gate.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from safety.trust_tiers import trust_engine
from safety.confirmation_gate import confirmation_gate


def test_trust_tier_classification():
    print("\n--- Testing Trust Tier Classification ---")

    # Safe read-only
    tier, req = trust_engine.classify_action("read_file", {"filename": "test.txt"})
    assert tier == "SAFE" and not req, "read_file should be SAFE"
    print(f"  [+] 'read_file': {tier} (confirm={req})")

    # Low risk
    tier, req = trust_engine.classify_action("play_spotify", {"query": "jazz"})
    assert tier == "LOW_RISK" and not req, "play_spotify should be LOW_RISK"
    print(f"  [+] 'play_spotify': {tier} (confirm={req})")

    # High risk
    tier, req = trust_engine.classify_action("git_commit", {"message": "Update"})
    assert tier == "HIGH_RISK" and req, "git_commit should be HIGH_RISK with confirmation"
    print(f"  [+] 'git_commit': {tier} (confirm={req})")

    # Danger
    tier, req = trust_engine.classify_action("delete_file", {"filename": "important.doc"})
    assert tier == "DANGER" and req, "delete_file should be DANGER with confirmation"
    print(f"  [+] 'delete_file': {tier} (confirm={req})")


def test_action_preview():
    print("\n--- Testing Action Preview Formatting ---")
    preview = trust_engine.format_action_preview("send_whatsapp_message", {
        "contact": "Teddy",
        "message": "See you tomorrow at 5pm"
    })
    assert preview["tier"] == "HIGH_RISK"
    assert "Teddy" in preview["summary"]
    print(f"  [+] Action preview: {preview['summary']} | Details: {preview['details']}")


async def test_confirmation_gate():
    print("\n--- Testing Confirmation Gate Async Resolution ---")
    req_id = "req_test_123"

    async def mock_ws_send(msg):
        assert msg["type"] == "confirmation_request"
        # Simulate user clicking approve in frontend
        confirmation_gate.resolve_approval(req_id, approved=True)

    approved = await confirmation_gate.request_approval(
        req_id, "git_push", {"target": "main"}, mock_ws_send
    )
    assert approved, "Gate should resolve as approved"
    print(f"  [+] Async confirmation gate resolved successfully: approved={approved}")


if __name__ == "__main__":
    print("========================================")
    print(" RUNNING WELLSY PHASE 3 TEST SUITE")
    print("========================================")
    test_trust_tier_classification()
    test_action_preview()
    asyncio.run(test_confirmation_gate())
    print("\n[ALL PHASE 3 TESTS PASSED CLEANLY] [OK]")
