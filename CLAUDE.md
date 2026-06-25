# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**zensical-macros-utils** is a [zensical](https://zensical.org/) macros module that provides reusable Jinja2 macros for link cards, GitHub Gist code blocks, and X/Twitter embeds. It is loaded via `zensical.extensions.macros` (the built-in macros extension in zensical v0.0.40+). The module automatically copies its own CSS/JS static assets into the docs directory on first use.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management and Node.js/npm for JavaScript testing.

```sh
uv sync                 # Install Python dependencies (creates .venv)
npm install             # Install JavaScript test dependencies
```

## Commands

### Python Tests

```sh
# Run all tests with coverage
just test-coverage-verbose

# Run a single test file
uv run pytest tests/python/zensical_macros_utils/test_link_card.py -s -vv

# Run tests matching a marker
uv run pytest -m link_card -s -vv

# CI variants
just test-ci-xml    # XML report (for CI)
just test-ci-term   # Terminal report (for CI)
```

Coverage requirement: **100%** for both pytest and Jest, enforced on PRs
(pytest `fail_under = 100`; Jest `coverageThreshold` 100% on all metrics).

### JavaScript Tests

```sh
npm test                # Run Jest tests once
npm run test:watch      # Watch mode
npm run test:coverage   # With coverage
```

### Docs (local preview)

```sh
uv run zensical serve
uv run zensical build
```

### Linting & Type Checking

Pre-commit runs ruff, mypy, and several other checks. To run manually:

```sh
uv run ruff check .             # Lint
uv run ruff format .            # Format
uv run mypy zensical_macros_utils/
pre-commit run --all-files      # Run all hooks
```

mypy is configured with `disallow_untyped_defs = true` — all functions must be fully annotated.

## Release & Commit Conventions

Commits follow **gitmoji** (`:sparkles:` feature, `:bug:` fix, `:boom:` breaking,
`:memo:` docs, ...). The leading `:shortcode:` drives automated releases — see
[CONTRIBUTING.md](CONTRIBUTING.md) for the gitmoji → version-bump table.

Releasing is two steps (the PyPI token never lives in CI):

1. Run the **semantic-release** workflow (`Actions → semantic-release`, manual
   `workflow_dispatch`; set `dry_run` to preview). It computes the next version
   from gitmoji, bumps `pyproject.toml`/`package.json`, re-locks `uv.lock`,
   updates `CHANGELOG.md`, commits to `main`, and creates the `vX.Y.Z` tag +
   GitHub Release. Config: `.releaserc.cjs` + `.github/release-notes-template.hbs`.
2. Publish to PyPI locally: `uv run python scripts/publish_to_pypi.py` (token read
   from the OS keyring via `uv publish --keyring-provider subprocess`; no env var).

Dependabot PRs are gated by `dependency-review.yml`, labelled by
`dependabot-metadata.yml`, and kept current by `dependabot-auto-rebase.yml`;
merging stays manual. All GitHub Actions are pinned to commit SHAs.

## Architecture

### Module Lifecycle (`zensical_macros_utils/__init__.py`)

The module exports `define_env(env: MacroEnv)` called by zensical's macros extension:

- Loads config via `common.load_config()`, which reads `zensical.toml` first and
  falls back to `mkdocs.yml` / `mkdocs.yaml` in the CWD, to get `site_url` and `extra` settings
- Copies CSS/JS static assets into `docs/` via `common.copy_static_files()` (skips if already up-to-date)
- Registers the three macros by calling each sub-module's `define_env`

Framework-agnostic helpers live in `common.py`: `load_config()`,
`load_extra_config()`, `get_docs_dir()` (honours the `MACROS_UTILS_DOCS_DIR` env
var, default `docs/`), `copy_static_files()`, and `escape_html()`. `__init__.py`
re-exports them as `_load_config` / `_load_extra_config` / `_get_docs_dir` and
focuses on orchestration.

### Macro Modules

| Module | Macro | What it does |
| --- | --- | --- |
| `link_card.py` | `link_card(url, ...)` | Fetches SVG icons (from GitHub Gists), renders an HTML link card with image/SVG, domain, and description. Uses `env.variables["_site_url"]` for base URL. |
| `gist_codeblock.py` | `gist_codeblock(gist_url, ...)` | Fetches raw Gist content via GitHub API, auto-detects language via filename extension and Pygments, returns a fenced Markdown code block |
| `x_twitter_card.py` | `x_twitter_card(url)` | Normalizes x.com/twitter.com URLs and renders a Twitter embed widget with dark mode support |
| `debug_logger.py` | (internal) | Per-feature debug logging controlled by `extra.debug.{link_card,gist_codeblock,x_twitter_card}` in `zensical.toml` (or `mkdocs.yml`). Read via `env.variables["extra"]` set by `define_env`. |

### Tests (`tests/python/`)

Tests mirror the source layout under `tests/python/zensical_macros_utils/`. Shared fixtures live in `tests/python/conftest.py`, including:

- `MockMacroEnv` — simulates the zensical `MacroEnv` object (has `variables`, `macros`, `filters`, `macro()`, `filter()`)
- `mock_requests_get()` helper — patches `requests.get` for HTTP calls
- `processor` fixture — pre-built `GistProcessor` instance

`test__init__.py` monkeypatches `_get_docs_dir` and `_load_extra_config` to avoid filesystem/config dependencies in tests.

Custom pytest markers: `gist`, `link_card`, `debug`.

CI matrix: Ubuntu/Windows/macOS × Python 3.10–3.13, timezone Asia/Tokyo.
