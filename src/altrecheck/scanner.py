"""Alt-text review comparison engine."""

from __future__ import annotations

from collections.abc import Iterable

from .gitrepo import GitRepository
from .models import Finding, ImageChange, ImageReference, Report
from .parsers import extract_references


def _rule_for(alt: str | None) -> tuple[str, str]:
    if alt is None:
        return "missing-alt-review", "The changed image still has no alt attribute."
    if alt == "":
        return (
            "decorative-status-review",
            "The changed image is still marked decorative with an empty alt attribute.",
        )
    return "stale-alt-review", "The image changed but its alternative text did not."


def compare_references(
    changes: Iterable[ImageChange],
    base_references: Iterable[ImageReference],
    head_references: Iterable[ImageReference],
) -> list[Finding]:
    """Compare references for changed images and return targeted review findings."""
    old_items = tuple(base_references)
    new_items = tuple(head_references)
    findings: list[Finding] = []
    for change in changes:
        old_by_document: dict[str, set[str | None]] = {}
        for reference in old_items:
            if reference.image_path == change.old_path:
                old_by_document.setdefault(reference.document, set()).add(reference.alt)
        for reference in new_items:
            if reference.image_path != change.new_path:
                continue
            previous_alts = old_by_document.get(reference.document, set())
            if reference.alt not in previous_alts:
                continue
            rule, message = _rule_for(reference.alt)
            findings.append(
                Finding(
                    rule=rule,
                    severity="warning",
                    document=reference.document,
                    line=reference.line,
                    image_path=reference.image_path,
                    alt=reference.alt,
                    message=message,
                )
            )
    return findings


def _references_at(repository: GitRepository, commit: str) -> tuple[ImageReference, ...]:
    references: list[ImageReference] = []
    for document in repository.list_documents(commit):
        source = repository.read_text(commit, document)
        references.extend(extract_references(document, source))
    return tuple(references)


def scan_repository(
    repository: GitRepository, base_revision: str, head_revision: str
) -> Report:
    """Scan a repository across two revisions."""
    base = repository.resolve_revision(base_revision)
    head = repository.resolve_revision(head_revision)
    changes = repository.image_changes(base, head)
    base_references = _references_at(repository, base)
    head_references = _references_at(repository, head)
    findings = compare_references(changes, base_references, head_references)
    return Report(
        base=base,
        head=head,
        changes=changes,
        findings=tuple(findings),
        base_references=len(base_references),
        head_references=len(head_references),
    )
