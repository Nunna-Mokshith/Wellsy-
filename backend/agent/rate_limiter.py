"""
Wellsy Rate Limit Manager
Tracks API usage and auto-switches between models to stay free.
"""
import time
import json
from pathlib import Path
from datetime import datetime, timezone


class RateLimitManager:
    """Manages API request budgets across Gemini free tier."""

    def __init__(self, daily_limit: int = 1500, rpm_limit: int = 30, pro_daily_limit: int = 50):
        self.daily_limit = daily_limit
        self.rpm_limit = rpm_limit
        self.pro_daily_limit = pro_daily_limit

        # Tracking state
        self._requests_today = 0
        self._pro_requests_today = 0
        self._minute_requests: list[float] = []
        self._last_reset_date: str = self._today_str()

        # Try to load persisted state
        self._state_file = Path(__file__).parent.parent / "db" / "rate_limits.json"
        self._load_state()

    def _today_str(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _load_state(self):
        """Load persisted rate limit state from disk."""
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text())
                if data.get("date") == self._today_str():
                    self._requests_today = data.get("requests_today", 0)
                    self._pro_requests_today = data.get("pro_requests_today", 0)
                # If it's a new day, counters stay at 0 (fresh budget!)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_state(self):
        """Persist rate limit state to disk."""
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps({
            "date": self._today_str(),
            "requests_today": self._requests_today,
            "pro_requests_today": self._pro_requests_today,
        }))

    def _check_day_reset(self):
        """Reset counters if it's a new day."""
        today = self._today_str()
        if self._last_reset_date != today:
            self._requests_today = 0
            self._pro_requests_today = 0
            self._last_reset_date = today

    def _clean_minute_window(self):
        """Remove requests older than 60 seconds from the RPM window."""
        now = time.time()
        self._minute_requests = [t for t in self._minute_requests if now - t < 60]

    def can_use_flash(self) -> bool:
        """Check if we can make a Gemini Flash request."""
        self._check_day_reset()
        self._clean_minute_window()
        return (
            self._requests_today < self.daily_limit
            and len(self._minute_requests) < self.rpm_limit
        )

    def can_use_pro(self) -> bool:
        """Check if we can make a Gemini Pro request."""
        self._check_day_reset()
        self._clean_minute_window()
        return (
            self._pro_requests_today < self.pro_daily_limit
            and len(self._minute_requests) < self.rpm_limit
        )

    def record_request(self, is_pro: bool = False):
        """Record that a request was made."""
        self._check_day_reset()
        self._requests_today += 1
        if is_pro:
            self._pro_requests_today += 1
        self._minute_requests.append(time.time())
        self._save_state()

    def pick_model(self, complexity: str = "medium") -> str:
        """
        Smart router: pick the best model based on task complexity and budget.
        Returns: 'flash', 'pro', or 'ollama'
        """
        self._check_day_reset()

        if complexity == "simple":
            # Simple tasks → try local first, save API budget
            return "ollama"

        if complexity == "complex" and self.can_use_pro():
            return "pro"

        if self.can_use_flash():
            return "flash"

        # All API budget exhausted → fallback to local
        return "ollama"

    def get_status(self) -> dict:
        """Get current rate limit status for the UI."""
        self._check_day_reset()
        self._clean_minute_window()
        return {
            "daily_used": self._requests_today,
            "daily_limit": self.daily_limit,
            "daily_remaining": max(0, self.daily_limit - self._requests_today),
            "rpm_used": len(self._minute_requests),
            "rpm_limit": self.rpm_limit,
            "pro_used": self._pro_requests_today,
            "pro_limit": self.pro_daily_limit,
            "budget_percent": round((self._requests_today / self.daily_limit) * 100, 1),
            "status": self._get_status_label(),
        }

    def _get_status_label(self) -> str:
        pct = (self._requests_today / self.daily_limit) * 100
        if pct < 50:
            return "healthy"
        elif pct < 75:
            return "moderate"
        elif pct < 90:
            return "warning"
        elif pct < 100:
            return "critical"
        else:
            return "exhausted"
