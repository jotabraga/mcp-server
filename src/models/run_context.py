"""Per-call context passed to tools.

Kept permissive (extra fields accepted) because callers may send arbitrary metadata, but
unlike the original `__dict__.update` version this documents the known fields and gives a
real type to depend on.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RunContext:
    user_id: Optional[str] = None
    tenancy_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "RunContext":
        if not data:
            return cls()
        known = {"user_id", "tenancy_id"}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(
            user_id=data.get("user_id"),
            tenancy_id=data.get("tenancy_id"),
            extra=extra,
        )
