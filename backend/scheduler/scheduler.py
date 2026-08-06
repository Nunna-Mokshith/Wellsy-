"""
Wellsy Persistent Task Scheduler Engine
Manages scheduled background tasks, cron-like reminders, and automated pre-flight checks.
"""
import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from memory.config import DB_DIR
from scheduler.preflight import run_preflight_checks

SCHEDULES_DB_FILE = DB_DIR / "schedules.db"


class TaskScheduler:
    def __init__(self, db_path: Path = SCHEDULES_DB_FILE):
        self.db_path = db_path
        self._init_db()
        self.is_running = False
        self._loop_task = None

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Create schedules database table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target TEXT,
                    schedule_type TEXT NOT NULL, -- 'ONCE', 'DAILY', 'INTERVAL'
                    trigger_time TEXT NOT NULL,  -- ISO format or 'HH:MM'
                    interval_minutes INTEGER DEFAULT 0,
                    trust_tier TEXT DEFAULT 'HIGH_RISK',
                    enabled INTEGER DEFAULT 1,
                    last_run TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_schedule(
        self,
        title: str,
        action: str,
        trigger_time: str,
        schedule_type: str = "ONCE",
        target: Optional[str] = None,
        interval_minutes: int = 0,
        trust_tier: str = "HIGH_RISK"
    ) -> Dict[str, Any]:
        """Add a new scheduled task."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO schedules 
                   (title, action, target, schedule_type, trigger_time, interval_minutes, trust_tier, enabled, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)""",
                (title, action, target, schedule_type, trigger_time, interval_minutes, trust_tier, now)
            )
            conn.commit()
            new_id = cursor.lastrowid

        return {
            "id": new_id,
            "title": title,
            "action": action,
            "trigger_time": trigger_time,
            "schedule_type": schedule_type,
            "status": "Scheduled"
        }

    def list_schedules(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """List all registered scheduled tasks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_disabled:
                cursor.execute("SELECT id, title, action, target, schedule_type, trigger_time, interval_minutes, trust_tier, enabled, last_run, created_at FROM schedules")
            else:
                cursor.execute("SELECT id, title, action, target, schedule_type, trigger_time, interval_minutes, trust_tier, enabled, last_run, created_at FROM schedules WHERE enabled = 1")
            rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "title": r[1],
                "action": r[2],
                "target": r[3],
                "schedule_type": r[4],
                "trigger_time": r[5],
                "interval_minutes": r[6],
                "trust_tier": r[7],
                "enabled": bool(r[8]),
                "last_run": r[9],
                "created_at": r[10]
            })
        return results

    def remove_schedule(self, schedule_id: int) -> bool:
        """Cancel and delete a scheduled task."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
            conn.commit()
            return cursor.rowcount > 0

    async def execute_task(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """Run pre-flight check and execute scheduled action."""
        # 1. Pre-flight check
        passed, msg = run_preflight_checks(task["action"], task.get("target"))
        if not passed:
            return False, f"Pre-flight safety failed: {msg}"

        # 2. Execution logic
        # Updates last_run timestamp
        now_str = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE schedules SET last_run = ? WHERE id = ?", (now_str, task["id"]))
            conn.commit()

        # If ONCE, disable task
        if task["schedule_type"] == "ONCE":
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE schedules SET enabled = 0 WHERE id = ?", (task["id"],))
                conn.commit()

        return True, f"Successfully executed scheduled task '{task['title']}'."

    async def start_scheduler_loop(self, on_trigger_callback=None):
        """Background loop to check and execute due tasks every 30 seconds."""
        self.is_running = True
        print("  [+] Wellsy Task Scheduler loop started.")
        while self.is_running:
            try:
                tasks = self.list_schedules()
                now = datetime.now()
                now_time_str = now.strftime("%H:%M")

                for t in tasks:
                    due = False
                    stype = t["schedule_type"]
                    ttime = t["trigger_time"]

                    if stype == "DAILY" and ttime == now_time_str:
                        # Check if already ran in the last 60 seconds
                        last_run = t.get("last_run")
                        if not last_run or (now - datetime.fromisoformat(last_run)).total_seconds() > 120:
                            due = True
                    elif stype == "ONCE":
                        try:
                            t_dt = datetime.fromisoformat(ttime)
                            if now >= t_dt:
                                due = True
                        except Exception:
                            if ttime == now_time_str:
                                due = True

                    if due:
                        success, result_msg = await self.execute_task(t)
                        if on_trigger_callback:
                            await on_trigger_callback(t, success, result_msg)
            except Exception as e:
                print(f"[!] TaskScheduler error in loop: {e}")

            await asyncio.sleep(30)


task_scheduler = TaskScheduler()
