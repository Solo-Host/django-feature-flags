# Contributing

Thanks for contributing to `django-feature-flags`.

## Development setup

```bash
uv sync --extra dev
```

## Local checks

Run the same checks used in CI:

```bash
uv run tox
```

You can also run the default tox environments:

```bash
uv run tox -e py313
uv run tox -e lint
uv run tox -e mypy
uv run tox -e security
```

## Pull requests

1. Add or update tests for behavior changes.
2. Keep documentation in sync with the API.
3. Prefer backwards-compatible defaults unless a breaking change is intentional and documented.

## Release process

1. Do not bump the version during normal feature work.
2. Use `.github/workflows/release.yml` to create the release bump PR from `main`.
   The workflow updates `pyproject.toml`, `feature_flags/__init__.py`, and
   `uv.lock` together.
3. The workflow enables squash auto-merge with branch deletion for the release
   PR after checks register.
4. Let the workflow create the tag and GitHub Release after the release PR merges.
