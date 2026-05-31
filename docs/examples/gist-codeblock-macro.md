---
title: Zensical Custom Gist Codeblock Macro
tags:
  - Zensical Macros
  - Custom Component
  - Gist
description: Documentation showing macros for generating Gist code blocks using the Zensical Macros Plugin
---

# Gist Codeblock Macro

## Summary

This section describes a macro that displays Gist code in a Zensical code block.

!!! note "This macro is assumed to be used with [Zensical](https://zensical.org/)."

## Usage

Write a macro in markdown with the following parameters to display Gist code in a code block.

Macro：`gist_codeblock`

| Parameters | Required | Default | Description |
|-----------|------|------------|------|
| `gist_url` | required | none | Gist shared link |
| `indent` | optional | 0 | indent level (`0`: none, `1`: 4 spaces, `2`: 8 spaces) |
| `ext` | Optional | Automatic determination from URL | language extension (e.g. `py`, `js`, `sh`, etc.) |

### Examples

#### Basic Usage

??? info "Specify minimal parameters"

    ```markdown
    {% raw %}
    {{ gist_codeblock(
        gist_url="https://gist.github.com/user/id"
    ) }}
    {% endraw %}
    ```

    Example

    ```markdown
    {% raw %}
    {{ gist_codeblock(
        gist_url="https://gist.github.com/7rikazhexde/89036d5fc849411b925e6da7d4986b52"
    ) }}
    {% endraw %}
    ```

{{ gist_codeblock(
    gist_url="https://gist.github.com/7rikazhexde/89036d5fc849411b925e6da7d4986b52"
) }}

#### Specify indentation level

!!! tip

    Must be specified if the code is to be displayed within a block of [admonition](https://zensical.org/docs/authoring/admonitions/).

??? info "Specify indentation level"

    ```markdown
    {% raw %}
    {{ gist_codeblock(
        gist_url="Gist shared link",
        indent=1  # Indentation level (1:4 spaces, 2:8 spaces)
    ) }}
    {% endraw %}
    ```

    Example of displaying code within an admonition block

    ```markdown
    ??? info "Title"
        {% raw %}
        {{ gist_codeblock(
            gist_url="https://gist.github.com/7rikazhexde/89036d5fc849411b925e6da7d4986b52",
            indent=2
        ) }}
        {% endraw %}
    ```

??? info "Indent example (indent=1)"

    {{ gist_codeblock(
        gist_url="https://gist.github.com/7rikazhexde/89036d5fc849411b925e6da7d4986b52",
        indent=1
    ) }}

    ??? info "Indent example (indent=2)"

        {{ gist_codeblock(
            gist_url="https://gist.github.com/7rikazhexde/89036d5fc849411b925e6da7d4986b52",
            indent=2
        ) }}

#### To explicitly specify a language

??? info "Specify language extensions"

    ```markdown
    {% raw %}
    {{ gist_codeblock(
        gist_url="Gist shared link",
        ext="py"  # Specify language extensions
    ) }}
    {% endraw %}
    ```

    Example

    ```markdown
    {% raw %}
    {{ gist_codeblock(
        gist_url="https://gist.github.com/7rikazhexde/6ada2a6ef3ca23938bfa62f32e3fbed8",
        ext="sh"
    ) }}
    {% endraw %}
    ```

{{ gist_codeblock(
    gist_url="https://gist.github.com/7rikazhexde/6ada2a6ef3ca23938bfa62f32e3fbed8",
    ext="sh"
) }}
