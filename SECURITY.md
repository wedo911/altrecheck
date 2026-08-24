# Security policy

## Supported version

Security fixes are applied to the latest version on `main`.

## Boundaries

AltRecheck treats repository paths and document content as untrusted.

- It performs read-only Git operations.
- Git is invoked with argument arrays and `shell=False`.
- User revisions are resolved to full commit hashes before file access.
- NULs, option-like revisions, escaping paths, dynamic references, and remote
  image URLs are rejected or skipped.
- Documents are decoded as text and never executed.
- The tool makes no network requests and does not upload image content.
- GitHub workflow command values are escaped before annotations are emitted.

The tool does not determine whether an image or description is safe, accurate,
lawful, or conformant. It requests a focused human review.

## Report a vulnerability

Do not disclose repository secrets or private images in a public issue. Use
GitHub's private vulnerability reporting and provide a sanitized proof of
concept, affected version, and expected impact.
