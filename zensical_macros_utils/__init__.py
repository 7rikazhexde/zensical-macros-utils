"""
Zensical macros module for enhanced documentation components.
"""

from __future__ import annotations

import logging
from pathlib import Path

from zensical.extensions.macros import MacroEnv

from . import gist_codeblock
from . import link_card
from . import x_twitter_card
from .common import (
    MACROS_UTILS_CSS,
    MACROS_UTILS_DIR,
    MACROS_UTILS_JS,
    copy_static_files,
)
from .common import get_docs_dir as _get_docs_dir
from .common import load_config as _load_config
from .common import load_extra_config as _load_extra_config

logger = logging.getLogger("zensical.macros-utils")

__all__ = [
    "MACROS_UTILS_CSS",
    "MACROS_UTILS_DIR",
    "MACROS_UTILS_JS",
    "copy_static_files",
    "define_env",
    "_get_docs_dir",
    "_load_config",
    "_load_extra_config",
]


def define_env(env: MacroEnv) -> None:
    """
    Zensicalマクロモジュールの環境を定義する
    """
    plugin_dir = Path(__file__).parent

    try:
        docs_dir = _get_docs_dir()

        # Make config values available to sub-modules via env.variables
        config = _load_config()
        raw_extra = config.get("extra", {})
        extra = raw_extra if isinstance(raw_extra, dict) else {}
        if extra:
            env.variables["extra"] = extra
        site_url = str(config.get("site_url", ""))
        if site_url:
            env.variables["_site_url"] = site_url

        copy_static_files(plugin_dir, docs_dir)

        link_card.define_env(env)
        gist_codeblock.define_env(env)
        x_twitter_card.define_env(env)

        logger.info("Zensical macros utils initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize zensical macros utils: {e}")
