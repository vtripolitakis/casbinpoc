from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from .config_store import FileResolverStore
from .enforcer import CasbinEnforcer


class CasbinResolver:
    """Resolve and cache CasbinEnforcer instances based on a context.

    For now, supports only file-based policies as in the current CasbinEnforcer.
    """

    def __init__(self, config_path: str | Path):
        self._store = FileResolverStore(config_path)

    def resolve(self, context: Dict[str, Any]) -> CasbinEnforcer:
        entry = self._store.find_match(context)
        if not entry:
            raise LookupError("No resolver entry matches the provided context")
        return _get_cached_wrapper(entry.enforcer.model, entry.enforcer.policy)


@lru_cache(maxsize=128)
def _get_cached_wrapper(model_path: str, policy_path: str) -> CasbinEnforcer:
    # Cache the CasbinWrapper by its model/policy pair to avoid reloading on every request.
    return CasbinEnforcer(model_path, policy_path)
