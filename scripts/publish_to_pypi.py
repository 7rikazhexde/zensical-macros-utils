"""PyPI 公開スクリプト (uv + keyring)

`uv build` でビルドし、`uv publish` で PyPI に公開する。認証トークンは OS の
キーリング（Windows 資格情報マネージャー / macOS Keychain / Secret Service 等）に
保存し、環境変数やリポジトリ・CI には置かない。

事前設定（1 回だけ）:
    # keyring CLI を導入（uv のツールとして PATH に入る）
    uv tool install keyring

    # PyPI トークンを保存（プロンプトにトークンを貼り付け。画面にも履歴にも残らない）
    keyring set https://upload.pypi.org/legacy/ __token__

    # TestPyPI も使う場合
    keyring set https://test.pypi.org/legacy/ __token__

使用方法:
    uv run python scripts/publish_to_pypi.py            # ビルドして PyPI に公開
    uv run python scripts/publish_to_pypi.py --dry-run  # ビルドのみ
    uv run python scripts/publish_to_pypi.py --test     # TestPyPI に公開

オプション:
    --dry-run     ビルドのみ行い公開しない（keyring 不要）
    --test        TestPyPI (https://test.pypi.org/legacy/) に公開する
    --skip-build  dist/ を再ビルドせず、既存の成果物をそのまま公開する
    --username    keyring 参照に使うユーザー名（既定: __token__）
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_DIST_DIR = _ROOT / "dist"
_PYPI_URL = "https://upload.pypi.org/legacy/"
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


def publish(test: bool, username: str) -> None:
    """uv publish + keyring で dist/ の成果物を公開する。

    --publish-url は keyring に登録したサービス名（URL）と一致させる必要がある。
    """
    url = _TESTPYPI_URL if test else _PYPI_URL
    run(
        [
            "uv",
            "publish",
            "--publish-url",
            url,
            "--keyring-provider",
            "subprocess",
            "--username",
            username,
        ]
    )


def require_keyring() -> None:
    """keyring CLI が PATH 上に存在するか確認する。"""
    if shutil.which("keyring") is None:
        print(
            "[FAIL] 'keyring' CLI not found on PATH.\n"
            "       Install it once:  uv tool install keyring\n"
            "       Store your token: keyring set https://upload.pypi.org/legacy/ __token__"
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and publish zensical-macros-utils to PyPI via uv + keyring."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build only; do not publish (keyring not required).",
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
    parser.add_argument(
        "--username",
        default="__token__",
        help="Username used for the keyring lookup (default: __token__).",
    )
    args = parser.parse_args()

    if not args.dry_run:
        require_keyring()

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
    print(f"[INFO] publishing to {target} (credentials from keyring)")
    publish(args.test, args.username)
    print(f"[OK]   published to {target}")


if __name__ == "__main__":
    main()
