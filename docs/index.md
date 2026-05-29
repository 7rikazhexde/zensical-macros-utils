# mkdocs-macros-utils

!!! warning "Deprecated"

    This package is no longer maintained. Please migrate to **[zensical-macros-utils](https://pypi.org/project/zensical-macros-utils/)**.

[mkdocs-macros-utils](https://pypi.org/project/mkdocs-macros-utils/) is a [zensical](https://zensical.org/)-based project that provides macros to extend cards, code blocks, etc, in MkDocs documents.

## Features

- **Link Card**: Create link cards with images and descriptions, etc
- **Gist Code Block**: Embed and syntax-highlight code from GitHub Gists
- **X/Twitter Card**: Embed tweets with proper styling and dark mode support

## Usage

### Install [mkdocs-macros-utils](https://pypi.org/project/mkdocs-macros-utils/)

!!! info "For pip"

    ```bash
    pip install mkdocs-macros-utils
    ```

!!! info "For uv"

    ```bash
    uv add mkdocs-macros-utils
    ```

### Config settings

1. Add the extension to your `zensical.toml`

    ```toml
    extra_css = [
        "stylesheets/macros-utils/link-card.css",
        "stylesheets/macros-utils/gist-cb.css",
        "stylesheets/macros-utils/x-twitter-link-card.css",
    ]

    extra_javascript = [
        "javascripts/macros-utils/x-twitter-widget.js",
    ]

    [project.plugins.macros]
    modules = ["mkdocs_macros_utils"]

    [project.extra.debug]
    link_card = false
    gist_codeblock = false
    x_twitter_card = false
    ```

1. Start the development server

    ```bash
    uv run zensical serve
    ```

The plugin will automatically create the required directories and copy CSS/JS files during the build process.

## [Examples](./examples/index.md)
