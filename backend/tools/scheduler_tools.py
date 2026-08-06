"""
Wellsy Scheduler Tools
LangChain structured tools for creating, listing, and canceling scheduled tasks.
"""
from typing import Optional
from langchain_core.tools import tool
from scheduler.scheduler import task_scheduler


@tool
def schedule_task(title: str, action: str, trigger_time: str, schedule_type: str = "ONCE", target: Optional[str] = None) -> str:
    """Schedule a new automated background task or reminder.
    
    Args:
        title: Short descriptive name for the task (e.g. 'Daily Git Push')
        action: The command/action to execute (e.g. 'git push', 'send_whatsapp')
        trigger_time: 'HH:MM' for daily (e.g. '23:00') or ISO timestamp for one-shot
        schedule_type: 'DAILY' or 'ONCE'
        target: Optional target path, repo, or contact name
    """
    try:
        res = task_scheduler.add_schedule(
            title=title,
            action=action,
            trigger_time=trigger_time,
            schedule_type=schedule_type.upper(),
            target=target
        )
        return f"Task '{title}' scheduled successfully for {trigger_time} ({schedule_type}). ID: {res['id']}"
    except Exception as e:
        return f"Failed to schedule task: {e}"


@tool
def list_scheduled_tasks() -> str:
    """List all currently active scheduled tasks and reminders."""
    try:
        tasks = task_scheduler.list_schedules()
        if not tasks:
            return "No scheduled tasks active."
        lines = []
        for t in tasks:
            lines.append(f"• ID {t['id']}: [{t['schedule_type']}] {t['title']} at {t['trigger_time']} (Action: {t['action']})")
        return "Scheduled Tasks:\n" + "\n".join(lines)
    except Exception as e:
        return f"Failed to list scheduled tasks: {e}"


@tool
def cancel_scheduled_task(task_id: int) -> str:
    """Cancel and remove a scheduled task by ID."""
    try:
        success = task_scheduler.remove_schedule(task_id)
        if success:
            return f"Scheduled task #{task_id} canceled successfully."
        return f"Task #{task_id} not found."
    except Exception as e:
        return f"Failed to cancel task: {e}"


SCHEDULER_TOOLS = [schedule_task, list_scheduled_tasks, cancel_scheduled_task]
