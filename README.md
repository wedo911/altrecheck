# AltRecheck

AltRecheck asks for an accessibility review when image bytes change but the associated alternative text does not. It is a deterministic, local CLI and GitHub Action: no vision model, uploads, API key, or network service.

```text
AltRecheck: 1 alt-text review finding(s)
index.html:24: warning [stale-alt-review] The image changed but its alternative text did not. image='media/hero.png' alt='A sunrise over the sea'
```

An unchanged description can still be correct. A finding means “a person should review this,” not “the text is wrong.”

## Why this catches a different regression

Most accessibility linters check whether `alt` exists or follows quality heuristics. Those checks can pass after a developer replaces the image and forgets to reconsider a plausible existing description. AltRecheck compares two Git revisions and uses the image change itself as the review trigger.

The product decision and landscape search are documented in [docs/RESEARCH.md](docs/RESEARCH.md). Behavior and limits are locked in [docs/SPEC.md](docs/SPEC.md).

## GitHub Action

```yaml
name: Alt text review

on:
  pull_request:

permissions:
  contents: read

jobs:
  altrecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: wedo911/altrecheck@v0
        with:
          base: ${{ github.event.pull_request.base.sha }}
          head: ${{ github.event.pull_request.head.sha }}
```

The action emits file-and-line workflow annotations and fails when review findings exist. Set `fail-on-findings: "false"` to make it advisory.

## CLI

AltRecheck needs Python 3.10 or later and Git. It has no runtime Python dependencies.

```sh
python -m pip install "altrecheck @ git+https://github.com/wedo911/altrecheck.git@v0"
altrecheck --base origin/main --head HEAD
```

Run directly from a source checkout:

```sh
PYTHONPATH=src python -m altrecheck --base HEAD^ --head HEAD
```

Useful options:

```text
--format text|json|github
--repo PATH
--no-fail
```

Exit codes are `0` for clear, `1` for review findings, and `2` for an operational error.

## Supported references

- HTML `<img src="..." alt="...">` in `.html` and `.htm`
- Inline and reference-style Markdown images in `.md` and `.markdown`
- Both supported forms in `.mdx`
- PNG, JPEG, GIF, WebP, SVG, and AVIF repository files
- Modified images and renamed images whose content also changed

Dynamic component props, CSS backgrounds, remote URLs, data URLs, and pixel interpretation are intentionally outside v0.1.

## Development

```sh
python -m pip install -e ".[test]"
pytest
ruff check .
```

## Security and privacy

AltRecheck performs read-only Git operations and never uploads images. Git commands use argument arrays rather than a shell. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
