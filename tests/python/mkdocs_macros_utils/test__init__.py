"""
Tests for MkDocs Macros Utils initialization module.
This module tests the functionality of the package's __init__.py,
including static file copying and environment setup.
"""

import os
import sys
import logging
from pathlib import Path
import pytest
from _pytest.logging import LogCaptureFixture
from pytest import MonkeyPatch
from mkdocs_macros_utils import (
    copy_static_files,
    define_env,
    MACROS_UTILS_DIR,
    MACROS_UTILS_CSS,
    MACROS_UTILS_JS,
    _get_docs_dir,
    _load_config,
    _load_extra_config,
)
from tests.python import MockMacroEnv


@pytest.fixture(autouse=True)
def setup_logging(caplog: LogCaptureFixture) -> None:
    """Setup logging for tests"""
    caplog.set_level(logging.INFO)


# -- Static File Tests ------------------------------
def test_copy_static_files(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    """Test copying of static files"""
    # Create mock plugin directory structure
    plugin_dir = tmp_path / "plugin"
    docs_dir = tmp_path / "docs"

    # Create necessary directories
    (plugin_dir / "static" / "css").mkdir(parents=True)
    (plugin_dir / "static" / "js").mkdir(parents=True)

    # Create mock static files
    for css_file in MACROS_UTILS_CSS:
        css_path = plugin_dir / "static" / "css" / css_file
        css_path.write_text("/* CSS content */")

    for js_file in MACROS_UTILS_JS:
        js_path = plugin_dir / "static" / "js" / js_file
        js_path.write_text("// JS content")

    # Test copying
    with caplog.at_level(logging.INFO):
        copy_static_files(plugin_dir, docs_dir)

    # Verify CSS files were copied
    css_dest = docs_dir / MACROS_UTILS_DIR
    for css_file in MACROS_UTILS_CSS:
        assert (css_dest / css_file).exists()

    # Verify JS files were copied
    js_dest = docs_dir / "javascripts" / "macros-utils"
    for js_file in MACROS_UTILS_JS:
        assert (js_dest / js_file).exists()

    # Test log messages
    assert any("Copied static CSS file" in record.message for record in caplog.records)
    assert any("Copied static JS file" in record.message for record in caplog.records)


def test_copy_static_files_update_only_newer(
    tmp_path: Path, caplog: LogCaptureFixture
) -> None:
    """Test that files are only copied when source is newer"""
    plugin_dir = tmp_path / "plugin"
    docs_dir = tmp_path / "docs"

    # Create necessary directories and initial files
    (plugin_dir / "static" / "css").mkdir(parents=True)
    css_dest = docs_dir / MACROS_UTILS_DIR
    css_dest.mkdir(parents=True)

    # Create a test CSS file
    test_css = "link-card.css"
    src_path = plugin_dir / "static" / "css" / test_css
    dest_path = css_dest / test_css

    # Create initial files
    src_path.write_text("/* CSS content */")
    dest_path.write_text("/* Old CSS content */")

    # Set destination file to be newer
    os.utime(dest_path, (2000000000, 2000000000))

    # Copy files
    with caplog.at_level(logging.INFO):
        copy_static_files(plugin_dir, docs_dir)

    # Verify file wasn't copied (no log message)
    assert not any(
        "Copied static CSS file" in record.message for record in caplog.records
    )


# -- Environment Setup Tests ------------------------------
def test_define_env_success(
    tmp_path: Path, caplog: LogCaptureFixture, monkeypatch: MonkeyPatch
) -> None:
    """Test successful environment setup"""
    mock_env = MockMacroEnv()

    # Create necessary plugin directory structure
    plugin_dir = tmp_path / "plugin"
    (plugin_dir / "static" / "css").mkdir(parents=True)
    (plugin_dir / "static" / "js").mkdir(parents=True)

    # Create mock static files
    for css_file in MACROS_UTILS_CSS:
        (plugin_dir / "static" / "css" / css_file).write_text("/* CSS */")
    for js_file in MACROS_UTILS_JS:
        (plugin_dir / "static" / "js" / js_file).write_text("/* JS */")

    # Monkeypatch plugin directory and docs directory
    monkeypatch.setattr("mkdocs_macros_utils.__file__", str(plugin_dir / "__init__.py"))
    monkeypatch.setattr("mkdocs_macros_utils._get_docs_dir", lambda: tmp_path / "docs")
    monkeypatch.setattr("mkdocs_macros_utils._load_extra_config", lambda: {})

    with caplog.at_level(logging.INFO):
        define_env(mock_env)

    assert any("successfully" in record.message for record in caplog.records)
    assert hasattr(mock_env, "link_card")
    assert hasattr(mock_env, "gist_codeblock")
    assert hasattr(mock_env, "x_twitter_card")


def test_define_env_failure(
    caplog: LogCaptureFixture, monkeypatch: MonkeyPatch
) -> None:
    """Test environment setup failure handling"""
    mock_env = MockMacroEnv()

    # Make copy_static_files raise to trigger the error path
    monkeypatch.setattr(
        "mkdocs_macros_utils._get_docs_dir", lambda: Path("/nonexistent/readonly")
    )
    monkeypatch.setattr("mkdocs_macros_utils._load_extra_config", lambda: {})
    monkeypatch.setattr(
        "mkdocs_macros_utils.copy_static_files",
        lambda *args: (_ for _ in ()).throw(RuntimeError("Simulated failure")),
    )

    with caplog.at_level(logging.ERROR):
        define_env(mock_env)

    assert any("Failed to initialize" in record.message for record in caplog.records)


# -- _get_docs_dir Tests ------------------------------
def test_get_docs_dir_default(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _get_docs_dir returns CWD/docs when env var is not set."""
    monkeypatch.delenv("MACROS_UTILS_DOCS_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    assert _get_docs_dir() == tmp_path / "docs"


def test_get_docs_dir_relative_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _get_docs_dir with a relative path in MACROS_UTILS_DOCS_DIR."""
    monkeypatch.setenv("MACROS_UTILS_DOCS_DIR", "custom_docs")
    monkeypatch.chdir(tmp_path)
    assert _get_docs_dir() == tmp_path / "custom_docs"


def test_get_docs_dir_absolute_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _get_docs_dir with an absolute path in MACROS_UTILS_DOCS_DIR."""
    monkeypatch.setenv("MACROS_UTILS_DOCS_DIR", str(tmp_path))
    assert _get_docs_dir() == tmp_path


# -- _load_config Tests ------------------------------
def test_load_config_yaml_fallback(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _load_config reads mkdocs.yml when no zensical.toml exists."""
    (tmp_path / "mkdocs.yml").write_text("site_name: Test\nextra:\n  debug: true\n")
    monkeypatch.chdir(tmp_path)
    config = _load_config()
    assert config["site_name"] == "Test"
    assert config["extra"]["debug"] is True


def test_load_config_no_files(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _load_config returns empty dict when no config files exist."""
    monkeypatch.chdir(tmp_path)
    assert _load_config() == {}


def test_load_config_invalid_toml_fallback(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Test _load_config falls back to mkdocs.yml on invalid TOML."""
    (tmp_path / "zensical.toml").write_bytes(b"invalid toml [[[")
    (tmp_path / "mkdocs.yml").write_text("site_name: Fallback\n")
    monkeypatch.chdir(tmp_path)
    config = _load_config()
    assert config.get("site_name") == "Fallback"


def test_load_config_tomli_fallback(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _load_config uses tomli when tomllib stdlib is not available."""
    (tmp_path / "zensical.toml").write_bytes(b'[project]\nsite_name = "TomliTest"\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(sys.modules, "tomllib", None)
    config = _load_config()
    assert config.get("site_name") == "TomliTest"


# -- _load_extra_config Tests ------------------------------
def test_load_extra_config(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _load_extra_config returns the extra section from config."""
    (tmp_path / "mkdocs.yml").write_text("extra:\n  key: value\n")
    monkeypatch.chdir(tmp_path)
    assert _load_extra_config() == {"key": "value"}


def test_load_extra_config_empty(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test _load_extra_config returns empty dict when no extra section exists."""
    monkeypatch.chdir(tmp_path)
    assert _load_extra_config() == {}
