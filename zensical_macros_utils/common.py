"""
Shared helpers for the zensical macros utils package.

This module centralizes configuration loading and static-asset management so
that ``__init__.py`` can focus on orchestration and the individual macro
modules can focus on rendering.
"""

from __future__ import annotations

import logging
import os
import shutil
from html import escape
from pathlib import Path

logger = logging.getLogger("zensical.macros-utils")

# Relative destination (inside ``docs/``) for the bundled stylesheets.
MACROS_UTILS_DIR = "stylesheets/macros-utils"
# Stylesheets and scripts copied into the docs directory on first use.
MACROS_UTILS_CSS = ["link-card.css", "gist-cb.css", "x-twitter-link-card.css"]
MACROS_UTILS_JS = ["x-twitter-widget.js"]


def escape_html(value: str) -> str:
    """Escape a string for safe interpolation into an HTML attribute or body.

    Args:
        value: Raw string to escape.

    Returns:
        The HTML-escaped string (quotes included).
    """
    return escape(value, quote=True)


def copy_static_files(plugin_dir: Path, docs_dir: Path) -> None:
    """Copy bundled CSS/JS assets into the docs directory.

    A file is only copied when it is missing at the destination or when the
    source is newer than the destination, so repeated builds stay cheap.

    Args:
        plugin_dir: Directory of the installed plugin package.
        docs_dir: Target documentation directory.
    """
    css_dest = docs_dir / MACROS_UTILS_DIR
    css_dest.mkdir(parents=True, exist_ok=True)

    js_dest = docs_dir / "javascripts" / "macros-utils"
    js_dest.mkdir(parents=True, exist_ok=True)

    _copy_if_newer(plugin_dir / "static" / "css", css_dest, MACROS_UTILS_CSS, "CSS")
    _copy_if_newer(plugin_dir / "static" / "js", js_dest, MACROS_UTILS_JS, "JS")


def _copy_if_newer(
    src_dir: Path, dest_dir: Path, filenames: list[str], kind: str
) -> None:
    """Copy each file from ``src_dir`` to ``dest_dir`` when source is newer."""
    for filename in filenames:
        src = src_dir / filename
        dest = dest_dir / filename
        if src.exists() and (
            not dest.exists() or os.path.getmtime(src) > os.path.getmtime(dest)
        ):
            shutil.copy2(src, dest)
            logger.info(f"Copied static {kind} file: {filename}")


def get_docs_dir() -> Path:
    """Return the docs directory path.

    Checks the ``MACROS_UTILS_DOCS_DIR`` env var first, then defaults to
    ``docs`` relative to the current working directory.
    """
    docs_dir_env = os.environ.get("MACROS_UTILS_DOCS_DIR", "docs")
    path = Path(docs_dir_env)
    if not path.is_absolute():
        path = Path(os.getcwd()) / path
    return path


def load_config() -> dict[str, object]:
    """Load full config from ``zensical.toml`` or ``mkdocs.yml`` in CWD.

    Returns an empty dict when neither file exists or parsing fails.
    """
    cwd = Path(os.getcwd())

    # Try zensical.toml first (TOML format, [project] section)
    toml_path = cwd / "zensical.toml"
    if toml_path.exists():
        try:
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib  # type: ignore[no-redef]
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
            project = data.get("project", data)
            return dict(project) if isinstance(project, dict) else {}
        except Exception:
            pass

    # Fall back to mkdocs.yml / mkdocs.yaml (YAML format)
    for config_name in ("mkdocs.yml", "mkdocs.yaml"):
        config_path = cwd / config_name
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    loaded = yaml.safe_load(f)
                return dict(loaded) if isinstance(loaded, dict) else {}
            except Exception:
                pass
    return {}


def load_extra_config() -> dict[str, object]:
    """Load the ``extra`` section from the resolved config (empty if absent)."""
    extra = load_config().get("extra", {})
    return extra if isinstance(extra, dict) else {}
