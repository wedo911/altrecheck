"""Typed result models for AltRecheck."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ImageReference:
    """A local image reference extracted from a document."""

    document: str
    image_path: str
    alt: str | None
    line: int
    syntax: str


@dataclass(frozen=True, slots=True)
class ImageChange:
    """An image whose bytes differ between two Git revisions."""

    old_path: str
    new_path: str
    status: str


@dataclass(frozen=True, slots=True)
class Finding:
    """A reference that needs a human alt-text review."""

    rule: str
    severity: str
    document: str
    line: int
    image_path: str
    alt: str | None
    message: str


@dataclass(frozen=True, slots=True)
class Report:
    """Complete comparison report."""

    base: str
    head: str
    changes: tuple[ImageChange, ...]
    findings: tuple[Finding, ...]
    base_references: int
    head_references: int

    def to_dict(self) -> dict[str, object]:
        """Return the stable public report schema."""
        return {
            "schema": "altrecheck.report.v1",
            "base": self.base,
            "head": self.head,
            "summary": {
                "changedImages": len(self.changes),
                "findings": len(self.findings),
                "baseReferences": self.base_references,
                "headReferences": self.head_references,
            },
            "changes": [asdict(item) for item in self.changes],
            "findings": [asdict(item) for item in self.findings],
            "disclaimer": (
                "A finding requests human review; it does not prove the alt text is wrong."
            ),
        }

    def to_json(self) -> str:
        """Serialize the report as deterministic, readable JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
