from altrecheck.parsers import extract_references, resolve_image_path


def test_extracts_html_images_with_lines() -> None:
    source = '<h1>News</h1>\n<img src="images/chart.png" alt="Quarterly revenue">'
    references = extract_references("pages/report.html", source)
    assert [(item.image_path, item.alt, item.line) for item in references] == [
        ("pages/images/chart.png", "Quarterly revenue", 2),
    ]


def test_extracts_inline_and_reference_markdown() -> None:
    source = (
        "![A solar array](media/solar.png)\n"
        "![System diagram][architecture]\n\n"
        '[architecture]: ./media/system.svg "Diagram"\n'
    )
    references = extract_references("docs/readme.md", source)
    assert [(item.image_path, item.alt) for item in references] == [
        ("docs/media/solar.png", "A solar array"),
        ("docs/media/system.svg", "System diagram"),
    ]


def test_ignores_images_inside_fenced_markdown_code() -> None:
    source = "```md\n![Example](assets/example.png)\n```\n"
    assert extract_references("README.md", source) == []


def test_ignores_remote_data_and_escaping_paths() -> None:
    assert resolve_image_path("docs/page.md", "https://example.org/a.png") is None
    assert resolve_image_path("docs/page.md", "data:image/png;base64,abc") is None
    assert resolve_image_path("page.md", "../../outside.png") is None


def test_decodes_local_url_paths_and_strips_query() -> None:
    assert resolve_image_path("docs/page.md", "../media/a%20b.png?v=2#x") == "media/a b.png"
