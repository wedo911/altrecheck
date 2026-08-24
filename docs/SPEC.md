# AltRecheck v0.1 specification

Status: accepted for implementation on 2026-08-25.

## Goal

Ask for a focused human review when an image's bytes change but the alternative
text associated with that image does not.

## Supported first slice

- Git repositories and any two resolvable revisions.
- Modified images and renamed images whose content also changed.
- PNG, JPEG, GIF, WebP, SVG, and AVIF files.
- HTML `<img src alt>` references.
- Inline and reference-style Markdown images in `.md` and `.mdx` files.
- Text, JSON, and GitHub workflow annotation output.
- Exit `1` when review findings exist, `0` when clear, and `2` for an
  operational error.

## Explicit limits

- A finding means “review this,” not “this alt text is incorrect.”
- The tool does not interpret pixels or generate descriptions.
- Dynamic component props, CSS background images, remote URLs, data URLs, and
  images outside the repository are outside v0.1.
- Parsing is deliberately conservative. Unsupported syntax is skipped rather
  than guessed.

## Privacy and security

- No network access or image upload.
- Git is invoked with argument arrays, never a shell command string.
- Repository paths that normalize outside the root are rejected.
- Output escapes GitHub workflow command delimiters.
