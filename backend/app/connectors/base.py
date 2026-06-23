"""Shared connector base: on-disk JSON cache so the pipeline is re-runnable
and the demo is deterministic (free API tiers are rate-limited)."""
import hashlib
import json
import os
from typing import Optional

from app.core.config import settings


class CachedConnector:
    name = "base"

    def _cache_path(self, key: str) -> str:
        cache_dir = os.path.join(settings.data_dir, "cache", self.name)
        os.makedirs(cache_dir, exist_ok=True)
        digest = hashlib.sha1(key.encode()).hexdigest()
        return os.path.join(cache_dir, f"{digest}.json")

    def cache_get(self, key: str) -> Optional[dict]:
        path = self._cache_path(key)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    def cache_put(self, key: str, value: dict) -> None:
        with open(self._cache_path(key), "w") as f:
            json.dump(value, f)
