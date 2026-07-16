# Contributing

Thanks for contributing to `django-feature-flags`.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

## Local checks

Run the same checks used in CI:

```bash
pytest
ruff check .
ruff format --check feature_flags tests
mypy feature_flags
```

You can also run the default tox environments:

```bash
tox -e py311,lint,mypy
```

## Pull requests

1. Add or update tests for behavior changes.
2. Keep documentation in sync with the API.
3. Prefer backwards-compatible defaults unless a breaking change is intentional and documented.

## Release process

1. Update the version in `pyproject.toml` and `feature_flags/__init__.py`.
2. Create a tagged release.
3. Publish through the GitHub Actions workflow configured for PyPI trusted publishing.
