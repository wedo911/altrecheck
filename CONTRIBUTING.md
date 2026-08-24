# Contributing

Contributions that improve parser coverage, Git edge cases, accessibility
workflow output, documentation, or tests are welcome.

1. Open an issue that describes the regression or supported syntax.
2. Add a failing test before the implementation.
3. Keep runtime code within the Python standard library.
4. Run `pytest` and `ruff check .`.
5. Update `docs/SPEC.md` when public behavior changes.

Do not commit real private images, secrets, or customer repositories. Small
synthetic byte fixtures are sufficient for integration tests.
