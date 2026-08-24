from altrecheck.models import ImageChange, ImageReference
from altrecheck.scanner import compare_references


def ref(image: str, alt: str | None, document: str = "index.html", line: int = 1) -> ImageReference:
    return ImageReference(document=document, image_path=image, alt=alt, line=line, syntax="html")


def test_flags_unchanged_alt_after_image_change() -> None:
    change = ImageChange(old_path="hero.png", new_path="hero.png", status="modified")
    findings = compare_references(
        [change], [ref("hero.png", "A city skyline")], [ref("hero.png", "A city skyline")]
    )
    assert len(findings) == 1
    assert findings[0].rule == "stale-alt-review"


def test_accepts_alt_that_changed_with_image() -> None:
    change = ImageChange(old_path="hero.png", new_path="hero.png", status="modified")
    findings = compare_references(
        [change], [ref("hero.png", "A city skyline")], [ref("hero.png", "A forest")]
    )
    assert findings == []


def test_flags_unchanged_empty_alt_for_decorative_status_review() -> None:
    change = ImageChange(old_path="shape.svg", new_path="shape.svg", status="modified")
    findings = compare_references([change], [ref("shape.svg", "")], [ref("shape.svg", "")])
    assert findings[0].rule == "decorative-status-review"


def test_flags_missing_alt_after_image_change() -> None:
    change = ImageChange(old_path="map.png", new_path="map.png", status="modified")
    findings = compare_references([change], [ref("map.png", None)], [ref("map.png", None)])
    assert findings[0].rule == "missing-alt-review"


def test_handles_content_changing_rename() -> None:
    change = ImageChange(old_path="old.png", new_path="new.png", status="renamed-modified")
    findings = compare_references(
        [change],
        [ref("old.png", "Team portrait", "about.md")],
        [ref("new.png", "Team portrait", "about.md")],
    )
    assert len(findings) == 1
    assert findings[0].image_path == "new.png"


def test_does_not_compare_unrelated_documents() -> None:
    change = ImageChange(old_path="hero.png", new_path="hero.png", status="modified")
    findings = compare_references(
        [change],
        [ref("hero.png", "Old", "old.html")],
        [ref("hero.png", "Old", "new.html")],
    )
    assert findings == []
