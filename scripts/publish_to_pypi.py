"""PyPI 公開スクリプト

`uv build` でパッケージをビルドし、`uv publish` で PyPI に公開する。
認証トークンは環境変数 ``UV_PUBLISH_TOKEN`` から読み込む。トークンはローカルで
設定する前提で、リポジトリや CI には保存しない。

semantic-release（.github/workflows/semantic-release.yml）はバージョン更新・
CHANGELOG・タグ・GitHub Release までを担当する。PyPI への公開だけは、トークンを
CI に置かないためにこのスクリプトでローカルから手動実行する。

使用方法:
    # PowerShell
    $env:UV_PUBLISH_TOKEN = "pypi-****"
    uv run python scripts/publish_to_pypi.py

    # bash
    export UV_PUBLISH_TOKEN="pypi-****"
    uv run python scripts/publish_to_pypi.py

オプション:
    --dry-run     ビルドのみ行い公開しない（トークン不要）
    --test        TestPyPI (https://test.pypi.org/legacy/) に公開する
                  （UV_PUBLISH_TOKEN には TestPyPI のトークンを設定すること）
    --skip-build  dist/ を再ビルドせず、既存の成果物をそのまま公開する
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_DIST_DIR = _ROOT / "dist"
_TOKEN_ENV = "UV_PUBLISH_TOKEN"
_TESTPYPI_URL = "https://test.pypi.org/legacy/"


def run(command: list[str]) -> None:
    """コマンドを実行し、失敗したら終了コード付きで中断する。"""
    printable = " ".join(command)
    print(f"[RUN]  {printable}")
    result = subprocess.run(command, cwd=_ROOT)
    if result.returncode != 0:
        print(f"[FAIL] command exited with {result.returncode}: {printable}")
        sys.exit(result.returncode)


def clean_dist() -> None:
    """既存の dist/ を削除して、古い成果物を公開しないようにする。"""
    if _DIST_DIR.exists():
        print(f"[INFO] removing existing build directory: {_DIST_DIR}")
        shutil.rmtree(_DIST_DIR)


def build() -> None:
    """uv build でソース配布物と wheel を生成する。"""
    run(["uv", "build"])


def publish(test: bool) -> None:
    """uv publish で dist/ の成果物を公開する。"""
    command = ["uv", "publish"]
    if test:
        command += ["--publish-url", _TESTPYPI_URL]
    run(command)


def require_token() -> None:
    """公開先トークンが環境変数に設定されているか確認する。"""
    if not os.environ.get(_TOKEN_ENV):
        print(
            f"[FAIL] environment variable {_TOKEN_ENV} is not set.\n"
            "       Set it locally before publishing, e.g.:\n"
            '         PowerShell : $env:UV_PUBLISH_TOKEN = "pypi-****"\n'
            '         bash       : export UV_PUBLISH_TOKEN="pypi-****"'
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and publish zensical-macros-utils to PyPI via uv."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build only; do not publish (no token required).",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Publish to TestPyPI instead of PyPI.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Publish the existing dist/ without rebuilding.",
    )
    args = parser.parse_args()

    if not args.dry_run:
        require_token()

    if args.skip_build:
        if not _DIST_DIR.exists() or not any(_DIST_DIR.iterdir()):
            print(f"[FAIL] --skip-build given but {_DIST_DIR} is empty.")
            sys.exit(1)
        print(f"[INFO] reusing existing build artifacts in {_DIST_DIR}")
    else:
        clean_dist()
        build()

    if args.dry_run:
        print("[INFO] --dry-run: build complete, skipping publish.")
        return

    target = "TestPyPI" if args.test else "PyPI"
    print(f"[INFO] publishing to {target}")
    publish(args.test)
    print(f"[OK]   published to {target}")


if __name__ == "__main__":
    main()
