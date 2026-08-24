# AltRecheck research note

Research date: 2026-08-25.

## Problem

Alternative text is contextual: it must describe the information or function
represented by the current image. A pull request can replace an image while
leaving a plausible, non-empty `alt` attribute untouched. Presence-based
linters continue to pass even though the description now deserves review.

## Landscape search

The scoped search found tools that detect missing, empty, generic, or
filename-derived alt text; accessibility regression scanners; and optional
vision-model checks of current image/description quality. It did not find a
small deterministic Git/CI tool whose trigger is specifically:

> image bytes changed + the associated alternative text did not change

AltRecheck does not claim the unchanged text is wrong. It creates a targeted
manual-review gate, with no image upload, model, API key, or content inference.
This search supports a useful niche but cannot prove that no similar project
exists.

## Product decision

The first release is a dependency-free Python CLI and composite GitHub Action.
It compares two Git revisions, finds modified or content-changing renamed image
files, resolves their references from HTML and Markdown, and reports references
whose alt text remained byte-for-byte identical.

## Sources

- W3C WAI, *Images Tutorial*: https://www.w3.org/WAI/tutorials/images/
- WCAG 2.2, Success Criterion 1.1.1: https://www.w3.org/TR/WCAG22/#non-text-content
- Git documentation, *git diff*: https://git-scm.com/docs/git-diff
- GitHub, accessibility alt-text bot:
  https://github.com/github/accessibility-alt-text-bot
- GitHub accessibility scanner alt-text plugin:
  https://github.com/github/accessibility-scanner-alt-text-plugin
- `eslint-plugin-jsx-a11y` alt-text rule:
  https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/main/docs/rules/alt-text.md
