"""
Wellsy Phase 2 Verification Test Suite
Tests Encrypted Memory DB, Passive File Scanner, Task Scheduler, and Pre-flight Safety.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from memory.memory_db import memory_db
from memory.file_scanner import file_scanner
from scheduler.scheduler import task_scheduler
from scheduler.preflight import run_preflight_checks


def test_memory_db():
    print("\n--- Testing Encrypted Memory DB ---")
    memory_id = memory_db.store_memory("USER_NOTE", "Test note: AWS certification completed", {"category": "test"})
    assert memory_id > 0, "Memory ID should be > 0"
    print(f"  [+] Stored encrypted memory ID #{memory_id}")

    recalled = memory_db.recall_memories(query="certification", limit=5)
    assert len(recalled) > 0, "Should recall matching memory"
    assert "AWS certification" in recalled[0]["content"]
    print(f"  [+] Recalled memory cleanly: '{recalled[0]['content']}'")

    stats = memory_db.get_stats()
    print(f"  [+] Memory DB stats: {stats}")


def test_file_scanner():
    print("\n--- Testing Passive File Scanner ---")
    new_files, mod_files, del_files = file_scanner.detect_changes()
    print(f"  [+] Scanner snapshot checked: {len(new_files)} new, {len(mod_files)} modified, {len(del_files)} deleted")
    summary = file_scanner.generate_greeting_summary()
    print(f"  [+] Greeting summary: '{summary or 'No file changes detected.'}'")


def test_preflight():
    print("\n--- Testing Pre-flight Safety Checks ---")
    passed, msg = run_preflight_checks("git commit", target="D:\\Wellsy")
    print(f"  [+] Git pre-flight check result: passed={passed}, msg='{msg}'")
    assert passed, "Pre-flight git check on Wellsy repo should pass"


def test_scheduler():
    print("\n--- Testing Task Scheduler ---")
    res = task_scheduler.add_schedule(
        title="Test Daily Backup",
        action="git status",
        trigger_time="23:00",
        schedule_type="DAILY"
    )
    assert res["id"] > 0
    print(f"  [+] Added schedule ID #{res['id']}")

    schedules = task_scheduler.list_schedules()
    assert any(s["id"] == res["id"] for s in schedules)
    print(f"  [+] Verified active schedules: {len(schedules)} tasks active")

    canceled = task_scheduler.remove_schedule(res["id"])
    assert canceled
    print(f"  [+] Canceled test schedule #{res['id']}")


if __name__ == "__main__":
    print("========================================")
    print(" RUNNING WELLSY PHASE 2 TEST SUITE")
    print("========================================")
    test_memory_db()
    test_file_scanner()
    test_preflight()
    test_scheduler()
    print("\n[ALL PHASE 2 TESTS PASSED CLEANLY] [OK]")
