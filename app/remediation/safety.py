import os
import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SafetyController:
    """Enforces high-level safety caps and cooldowns for remediation actions."""

    def __init__(self, max_actions_per_hour: int = None, cooldown_minutes: int = None):
        self.max_actions_per_hour: int = max_actions_per_hour or int(os.getenv("MAX_ACTIONS_PER_HOUR", "3"))
        self.cooldown_seconds: int = 60 * (cooldown_minutes or int(os.getenv("COOLDOWN_MINUTES", "10")))
        self.action_timestamps: Dict[str, list] = {}
        self.resource_last_action: Dict[str, float] = {}

    def _prune_old(self, action_key: str, now: float) -> None:
        one_hour_ago = now - 3600
        self.action_timestamps.setdefault(action_key, [])
        self.action_timestamps[action_key] = [t for t in self.action_timestamps[action_key] if t >= one_hour_ago]

    def allow(self, action_key: str, resource_id: str) -> Tuple[bool, str]:
        now = time.time()
        self._prune_old(action_key, now)

        # Global cap per action type
        if len(self.action_timestamps.get(action_key, [])) >= self.max_actions_per_hour:
            return False, f"Action cap reached for '{action_key}' in the last hour"

        # Resource cooldown
        last = self.resource_last_action.get(resource_id, 0)
        if now - last < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - (now - last))
            return False, f"Cooldown active for resource '{resource_id}' ({remaining}s remaining)"

        return True, "allowed"

    def record(self, action_key: str, resource_id: str) -> None:
        now = time.time()
        self.action_timestamps.setdefault(action_key, []).append(now)
        self.resource_last_action[resource_id] = now
