# Contributing to zensical-macros-utils

Thanks for your interest in contributing!

## Development environment

This project uses [uv](https://docs.astral.sh/uv/) for Python and npm for the
JavaScript (Jest) tests.

```sh
uv sync          # Python dependencies (creates .venv)
npm install      # JavaScript test dependencies
```

- **Code style**: ruff (lint + format) and mypy (`disallow_untyped_defs = true`),
  enforced via pre-commit. Run `pre-commit run --all-files` before pushing.
- **Tests**: pytest and Jest, both kept at **100% coverage**.
  - Python: `uv run python scripts/run_tests.py --report term`
  - JavaScript: `npm test -- --coverage`
- **Branching**: use a `type/short-description` branch name, e.g.
  `fix/twitter-card-duplicate`, `docs/add-config-examples`, `ci/semantic-release`.
- **Pull requests**: keep one focused change per PR.

## Commit messages — gitmoji

Commits follow [gitmoji](https://gitmoji.dev/) conventions (same as
[json2vars-setter](https://github.com/7rikazhexde/json2vars-setter)). Use the
`:shortcode:` form at the start of the subject so the release tooling can read it:

```
:sparkles: feat(link-card): add SVG fallback for missing icons
:bug: fix(js): prevent duplicate Twitter card render on reload
:memo: docs: document mkdocs.yml configuration
```

### How gitmoji drives releases

Releases are automated with **semantic-release** (`.releaserc.cjs`,
`.github/workflows/semantic-release.yml`). The gitmoji in commits since the last
tag decide the next version:

| Bump  | gitmoji |
| ----- | ------- |
| Major | `:boom:` |
| Minor | `:sparkles:` |
| Patch | `:bug:` `:ambulance:` `:lock:` `:zap:` `:rocket:` `:wrench:` `:recycle:` `:fire:` `:arrow_up:` `:arrow_down:` `:pushpin:` `:pencil2:` `:globe_with_meridians:` `:alien:` `:card_file_box:` |

A commit whose gitmoji is **not** in the table above (e.g. `:memo:`, `:white_check_mark:`,
`:art:`) does not trigger a release and is omitted from the generated release
notes — use those freely for docs/test/chore work, but make sure each user-facing
change carries a release-triggering gitmoji.

## Release process

Releasing is two steps; the PyPI token is never stored in CI.

1. **Version, changelog, tag, GitHub Release** — run the **semantic-release**
   workflow manually (`Actions → semantic-release → Run workflow`). Use the
   `dry_run` input first to preview the next version and notes. It bumps
   `pyproject.toml` / `package.json`, refreshes `uv.lock`, updates
   `CHANGELOG.md`, commits to `main`, and creates the `vX.Y.Z` tag + Release.

2. **Publish to PyPI** — locally, with your token in the environment:

   ```sh
   # PowerShell
   $env:UV_PUBLISH_TOKEN = "pypi-****"
   uv run python scripts/publish_to_pypi.py

   # Preview the build first, or publish to TestPyPI:
   uv run python scripts/publish_to_pypi.py --dry-run
   uv run python scripts/publish_to_pypi.py --test
   ```

## Dependency updates & security

Dependabot opens grouped update PRs (`.github/dependabot.yml`) with a `cooldown`
so freshly published versions are not pulled instantly. Each PR is checked by
`dependency-review.yml` (fails on a newly introduced vulnerability) and labelled
by bump type (`dependabot-metadata.yml`); `dependabot-auto-rebase.yml` keeps open
PRs mergeable. **Merging is always manual.**
