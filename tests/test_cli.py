from pathlib import Path

from altrecheck import cli
from altrecheck.gitrepo import GitRepositoryError
from altrecheck.models import Finding, ImageChange, Report


def report(*, finding: bool) -> Report:
    findings = (
        Finding(
            rule="stale-alt-review",
            severity="warning",
            document="docs/a,b:guide.md",
            line=4,
            image_path="media/hero.png",
            alt="Old view",
            message="The image changed but its alternative text did not.",
        ),
    ) if finding else ()
    return Report(
        base="a" * 40,
        head="b" * 40,
        changes=(ImageChange("media/hero.png", "media/hero.png", "modified"),),
        findings=findings,
        base_references=1,
        head_references=1,
    )


def test_cli_returns_one_and_prints_text_finding(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "scan_repository", lambda *_: report(finding=True))
    assert cli.main(["--repo", ".", "--base", "a", "--head", "b"]) == 1
    output = capsys.readouterr().out
    assert "stale-alt-review" in output
    assert "docs/a,b:guide.md:4" in output


def test_cli_no_fail_returns_zero(monkeypatch) -> None:
    monkeypatch.setattr(cli, "scan_repository", lambda *_: report(finding=True))
    assert cli.main(["--base", "a", "--head", "b", "--no-fail"]) == 0


def test_cli_emits_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "scan_repository", lambda *_: report(finding=False))
    assert cli.main(["--base", "a", "--head", "b", "--format", "json"]) == 0
    assert '"schema": "altrecheck.report.v1"' in capsys.readouterr().out


def test_github_output_escapes_command_properties(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "scan_repository", lambda *_: report(finding=True))
    assert cli.main(["--base", "a", "--head", "b", "--format", "github"]) == 1
    output = capsys.readouterr().out
    assert "file=docs/a%2Cb%3Aguide.md" in output
    assert "title=AltRecheck%3A stale-alt-review" in output


def test_cli_returns_two_for_git_error(monkeypatch, capsys, tmp_path: Path) -> None:
    def fail(*_args):
        raise GitRepositoryError("not a repository")

    monkeypatch.setattr(cli, "scan_repository", fail)
    assert cli.main(["--repo", str(tmp_path)]) == 2
    assert "not a repository" in capsys.readouterr().err
