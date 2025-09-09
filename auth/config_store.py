from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EnforcerConfig:
    model: str
    policy: str


@dataclass(frozen=True)
class ResolverEntry:
    id: str
    match: Dict[str, Any]
    enforcer: EnforcerConfig


class FileResolverStore:
    """Simple file-backed resolver mapping store (read-only for v1).

    Structure of the JSON file:
    {
      "resolvers": [
        {
          "id": "tenantA",
          "match": { "tenant": "A" },
          "enforcer": { "model": "...", "policy": "..." }
        }
      ]
    }
    """

    def __init__(self, config_path: str | Path):
        self._path = Path(config_path)
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self._path.exists():
            raise FileNotFoundError(f"Resolver config file not found: {self._path}")
        with self._path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "resolvers" not in data:
            raise ValueError("Invalid resolver config: missing 'resolvers' root key")
        return data

    def get_all(self) -> List[ResolverEntry]:
        entries: List[ResolverEntry] = []
        for raw in self._data.get("resolvers", []):
            enforcer = raw.get("enforcer", {})
            entries.append(
                ResolverEntry(
                    id=str(raw.get("id")),
                    match=dict(raw.get("match", {})),
                    enforcer=EnforcerConfig(
                        model=str(enforcer.get("model")),
                        policy=str(enforcer.get("policy")),
                    ),
                )
            )
        return entries

    def find_match(self, context: Dict[str, Any]) -> Optional[ResolverEntry]:
        """Return the first resolver entry whose 'match' dict is entirely contained in context.

        Matching rule (simple v1): for each key in entry.match, context must contain the same key with equal value.
        """
        for entry in self.get_all():
            match_ok = all(context.get(k) == v for k, v in entry.match.items())
            if match_ok:
                return entry
        return None
