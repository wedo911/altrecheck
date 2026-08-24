import json
import subprocess
from pathlib import Path

from altrecheck.gitrepo import GitRepository
from altrecheck.scanner import scan_repository


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def make_repo(tmp_path: Path) -> tuple[Path, str]:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.org")
    (tmp_path / "hero.png").write_bytes(b"first image")
    (tmp_path / "index.html").write_text(
        '<img src="hero.png" alt="A sunrise over the sea">', encoding="utf-8"
    )
    return tmp_path, commit(tmp_path, "base")


def test_scans_two_git_revisions(tmp_path: Path) -> None:
    repo_path, base = make_repo(tmp_path)
    (repo_path / "hero.png").write_bytes(b"different image")
    head = commit(repo_path, "replace image")
    report = scan_repository(GitRepository(repo_path), base, head)
    assert report.base == base
    assert report.head == head
    assert len(report.findings) == 1
    assert report.findings[0].document == "index.html"


def test_changed_alt_clears_finding(tmp_path: Path) -> None:
    repo_path, base = make_repo(tmp_path)
    (repo_path / "hero.png").write_bytes(b"different image")
    (repo_path / "index.html").write_text(
        '<img src="hero.png" alt="A forest path">', encoding="utf-8"
    )
    head = commit(repo_path, "replace image and description")
    report = scan_repository(GitRepository(repo_path), base, head)
    assert report.findings == ()


def test_report_is_json_serializable(tmp_path: Path) -> None:
    repo_path, base = make_repo(tmp_path)
    (repo_path / "hero.png").write_bytes(b"different image")
    head = commit(repo_path, "replace image")
    report = scan_repository(GitRepository(repo_path), base, head)
    payload = json.loads(report.to_json())
    assert payload["schema"] == "altrecheck.report.v1"
    assert payload["summary"]["findings"] == 1


def test_content_changing_image_rename_is_scanned(tmp_path: Path) -> None:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.org")
    (tmp_path / "old.png").write_bytes(b"a" * 2_000)
    (tmp_path / "about.md").write_text("![Team portrait](old.png)\n", encoding="utf-8")
    base = commit(tmp_path, "base")

    git(tmp_path, "mv", "old.png", "new.png")
    content = bytearray((tmp_path / "new.png").read_bytes())
    content[:100] = b"b" * 100
    (tmp_path / "new.png").write_bytes(content)
    (tmp_path / "about.md").write_text("![Team portrait](new.png)\n", encoding="utf-8")
    head = commit(tmp_path, "rename and replace image")

    report = scan_repository(GitRepository(tmp_path), base, head)
    assert report.changes[0].status == "renamed-modified"
    assert report.findings[0].image_path == "new.png"
