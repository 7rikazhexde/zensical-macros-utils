"""
Zensical macros module for displaying X/Twitter link cards.
"""

from __future__ import annotations

import re
from zensical.extensions.macros import MacroEnv

from .common import escape_html
from .debug_logger import DebugLogger

# Matches a tweet status URL and captures the numeric tweet id.
_TWEET_URL_RE = re.compile(r"https?://(?:mobile\.)?(?:twitter|x)\.com/\w+/status/(\d+)")


def validate_x_twitter_url(url: str, logger: DebugLogger) -> bool:
    """
    Validate X/Twitter tweet page URL

    Args:
        url (str): URL to check
        logger (DebugLogger): Debug logger

    Returns:
        bool: True if URL is valid, False otherwise
    """
    if _TWEET_URL_RE.match(url):
        logger.log(f"Valid X/Twitter URL: {url}")
        return True

    logger.log(f"Invalid X/Twitter URL: {url}")
    return False


def extract_tweet_id(url: str) -> str | None:
    """
    Extract the numeric tweet id from an X/Twitter status URL.

    Args:
        url (str): X/Twitter tweet URL

    Returns:
        str | None: Tweet id, or None when the URL does not contain one.
    """
    match = _TWEET_URL_RE.match(url)
    return match.group(1) if match else None


def standardize_twitter_url(url: str, logger: DebugLogger) -> str:
    """
    Standardize URL to twitter.com format

    Args:
        url (str): Original URL
        logger (DebugLogger): Debug logger

    Returns:
        str: Standardized URL
    """
    # Convert x.com to twitter.com
    standardized_url = url.replace("x.com", "twitter.com")

    logger.log(f"URL standardization: {url} -> {standardized_url}")
    return standardized_url


def create_x_twitter_card(url: str, env: MacroEnv | None = None) -> str:
    """
    Generate embed container HTML from an X/Twitter tweet URL.

    The returned markup is intentionally minimal: a container that the
    ``x-twitter-widget.js`` script turns into a rendered tweet via the
    official ``twttr.widgets.createTweet`` API, plus a ``<noscript>``
    fallback link for environments without JavaScript.

    Args:
        url (str): X tweet URL
        env (MacroEnv | None, optional): zensical macro environment

    Returns:
        str: Embed container HTML
    """
    # Create debug logger
    logger = DebugLogger.create_logger("x_twitter_card", env)

    logger.log("Creating X/Twitter card", {"url": url})

    # URL validation
    if not validate_x_twitter_url(url, logger):
        logger.log("URL validation failed")
        raise ValueError("Invalid X/Twitter URL")

    # Standardize URL and extract the tweet id for client-side rendering.
    url = standardize_twitter_url(url, logger)
    tweet_id = extract_tweet_id(url) or ""

    safe_url = escape_html(url)
    html = f"""
    <div class="x-twitter-embed" data-url="{safe_url}" data-tweet-id="{tweet_id}">
        <noscript><a href="{safe_url}">{safe_url}</a></noscript>
    </div>
    """

    logger.log("X/Twitter card HTML generated successfully")
    return html


def define_env(env: MacroEnv) -> None:
    """
    Define x_twitter_card macro in zensical macro environment

    Args:
        env (MacroEnv): Macro plugin environment
    """

    @env.macro
    def x_twitter_card(url: str) -> str:
        """
        Zensical macro to generate embed container HTML from an X tweet URL.

        Args:
            url (str): X tweet URL

        Returns:
            str: Embed container HTML
        """
        return create_x_twitter_card(url, env)
