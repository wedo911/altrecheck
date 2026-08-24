"""Conservative local image-reference extraction."""

from __future__ import annotations

import posixpath
import re
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

from .models import ImageReference

_MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdx"}
_HTML_EXTENSIONS = {".html", ".htm", ".mdx"}
_INLINE_IMAGE = re.compile(
    r"!\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
_REFERENCE_IMAGE = re.compile(r"!\[([^\]]*)\]\[([^\]]*)\]")
_REFERENCE_DEFINITION = re.compile(
    r"^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|([^\s]+))", re.MULTILINE
)


def resolve_image_path(document: str, source: str) -> str | None:
    """Resolve a web reference to a safe repository-relative POSIX path."""
    if not source or any(character in source for character in "{}\\\0"):
        return None
    parsed = urlsplit(source.strip())
    if parsed.scheme or parsed.netloc or source.startswith("//"):
        return None
    decoded = unquote(parsed.path)
    if not decoded:
        return None
    if decoded.startswith("/"):
        candidate = posixpath.normpath(decoded.lstrip("/"))
    else:
        parent = str(PurePosixPath(document).parent)
        candidate = posixpath.normpath(posixpath.join(parent, decoded))
    if candidate in {"", ".", ".."} or candidate.startswith("../"):
        return None
    return candidate


class _ImageHTMLParser(HTMLParser):
    def __init__(self, document: str) -> None:
        super().__init__(convert_charrefs=True)
        self.document = document
        self.references: list[ImageReference] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "img":
            return
        attributes = {name.casefold(): value for name, value in attrs}
        source = attributes.get("src")
        if source is None:
            return
        path = resolve_image_path(self.document, source)
        if path is None:
            return
        self.references.append(
            ImageReference(
                document=self.document,
                image_path=path,
                alt=attributes.get("alt"),
                line=self.getpos()[0],
                syntax="html",
            )
        )


def _active_markdown_lines(source: str) -> list[tuple[int, str]]:
    active: list[tuple[int, str]] = []
    fence: str | None = None
    for line_number, line in enumerate(source.splitlines(), start=1):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is None:
            active.append((line_number, line))
    return active


def _extract_markdown(document: str, source: str) -> list[ImageReference]:
    active_lines = _active_markdown_lines(source)
    active_source = "\n".join(line for _, line in active_lines)
    definitions: dict[str, str] = {}
    for match in _REFERENCE_DEFINITION.finditer(active_source):
        definitions[match.group(1).strip().casefold()] = match.group(2) or match.group(3)

    references: list[ImageReference] = []
    for line_number, line in active_lines:
        for match in _INLINE_IMAGE.finditer(line):
            path = resolve_image_path(document, match.group(2) or match.group(3))
            if path is not None:
                references.append(
                    ImageReference(document, path, match.group(1), line_number, "markdown")
                )
        for match in _REFERENCE_IMAGE.finditer(line):
            label = (match.group(2) or match.group(1)).strip().casefold()
            source_path = definitions.get(label)
            path = resolve_image_path(document, source_path) if source_path else None
            if path is not None:
                references.append(
                    ImageReference(document, path, match.group(1), line_number, "markdown")
                )
    return references


def extract_references(document: str, source: str) -> list[ImageReference]:
    """Extract supported local image references from one repository document."""
    suffix = PurePosixPath(document).suffix.casefold()
    references: list[ImageReference] = []
    if suffix in _HTML_EXTENSIONS:
        parser = _ImageHTMLParser(document)
        parser.feed(source)
        references.extend(parser.references)
    if suffix in _MARKDOWN_EXTENSIONS:
        references.extend(_extract_markdown(document, source))
    return references
