"""Safe, read-only Git repository access."""

from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath

from .models import ImageChange

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
DOCUMENT_EXTENSIONS = {".html", ".htm", ".md", ".markdown", ".mdx"}


class GitRepositoryError(RuntimeError):
    """Raised when a required read-only Git operation fails."""


class GitRepository:
    """Read files and changes from a local Git repository."""

    def __init__(self, root: Path | str = ".") -> None:
        self.root = Path(root).resolve()

    def _run(self, *args: str) -> bytes:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.root,
                check=True,
                capture_output=True,
            )
        except FileNotFoundError as error:
            raise GitRepositoryError("Git is not installed or is not on PATH") from error
        except subprocess.CalledProcessError as error:
            detail = error.stderr.decode("utf-8", errors="replace").strip()
            raise GitRepositoryError(detail or f"git {' '.join(args)} failed") from error
        return result.stdout

    def resolve_revision(self, revision: str) -> str:
        """Resolve a user revision to a full commit hash before further use."""
        if not revision or revision.startswith("-") or "\0" in revision:
            raise GitRepositoryError(f"Invalid Git revision: {revision!r}")
        output = self._run("rev-parse", "--verify", f"{revision}^{{commit}}")
        return output.decode("ascii").strip()

    def list_documents(self, commit: str) -> tuple[str, ...]:
        """List supported documents in a commit."""
        output = self._run("ls-tree", "-r", "-z", "--name-only", commit)
        paths = output.decode("utf-8", errors="surrogateescape").split("\0")
        return tuple(
            path
            for path in paths
            if path and PurePosixPath(path).suffix.casefold() in DOCUMENT_EXTENSIONS
        )

    def read_text(self, commit: str, path: str) -> str:
        """Read a repository file without checking out a revision."""
        if "\0" in path or path.startswith("../"):
            raise GitRepositoryError(f"Unsafe repository path: {path!r}")
        return self._run("cat-file", "blob", f"{commit}:{path}").decode(
            "utf-8", errors="replace"
        )

    def _blob_id(self, commit: str, path: str) -> str:
        return self._run("rev-parse", f"{commit}:{path}").decode("ascii").strip()

    def image_changes(self, base: str, head: str) -> tuple[ImageChange, ...]:
        """Return modified images and renamed images whose bytes changed."""
        output = self._run("diff", "--name-status", "-z", "--find-renames", base, head, "--")
        fields = output.decode("utf-8", errors="surrogateescape").split("\0")
        changes: list[ImageChange] = []
        index = 0
        while index < len(fields) and fields[index]:
            status = fields[index]
            index += 1
            if status.startswith(("R", "C")):
                old_path, new_path = fields[index], fields[index + 1]
                index += 2
                if (
                    status.startswith("R")
                    and _is_image(new_path)
                    and self._blob_id(base, old_path) != self._blob_id(head, new_path)
                ):
                    changes.append(ImageChange(old_path, new_path, "renamed-modified"))
                continue
            path = fields[index]
            index += 1
            if status[0] in {"M", "T"} and _is_image(path):
                changes.append(ImageChange(path, path, "modified"))
        return tuple(changes)


def _is_image(path: str) -> bool:
    return PurePosixPath(path).suffix.casefold() in IMAGE_EXTENSIONS
