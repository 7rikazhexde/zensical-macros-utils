"""設定ファイル読み込み確認スクリプト

カレントディレクトリにある設定ファイル（zensical.toml / mkdocs.yml / mkdocs.yaml）を
検出し、load_config() で正しく読み込めるかを確認する。

使用方法:
    uv run python scripts/verify_config_loading.py
    uv run python scripts/verify_config_loading.py --dir path/to/project
"""

import argparse
import os
import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加して zensical_macros_utils をインポートできるようにする
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from zensical_macros_utils.common import (  # noqa: E402  # sys.path 調整後にインポートする必要がある
    load_config,
    load_extra_config,
)

CONFIG_CANDIDATES = ["zensical.toml", "mkdocs.yml", "mkdocs.yaml"]


def check_directory(target_dir: Path) -> int:
    """指定ディレクトリの設定ファイルを検出してロード結果を表示する。

    Returns:
        0 on success, 1 on failure.
    """
    original_cwd = Path(os.getcwd())
    os.chdir(target_dir)

    try:
        found = [name for name in CONFIG_CANDIDATES if (target_dir / name).exists()]

        if not found:
            print(f"[SKIP] 設定ファイルが見つかりません: {target_dir}")
            print(f"       対象ファイル: {', '.join(CONFIG_CANDIDATES)}")
            return 0

        print(f"[INFO] 検出した設定ファイル: {', '.join(found)}")
        config = load_config()

        if not config:
            print("[FAIL] load_config() が空の dict を返しました")
            return 1

        extra = load_extra_config()

        site_name = config.get("site_name", "(未設定)")
        site_url = config.get("site_url", "(未設定)")
        print(f"[OK]   site_name : {site_name}")
        print(f"[OK]   site_url  : {site_url}")
        print(f"[OK]   extra     : {extra if extra else '(なし)'}")
        print("[PASS] 設定ファイルの読み込みに成功しました")
        return 0

    except Exception as exc:
        print(f"[FAIL] 例外が発生しました: {exc}")
        return 1

    finally:
        os.chdir(original_cwd)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="設定ファイル（zensical.toml / mkdocs.yml / mkdocs.yaml）の読み込みを確認する"
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="確認するディレクトリ（デフォルト: カレントディレクトリ）",
    )
    args = parser.parse_args()

    target = Path(args.dir).resolve()
    if not target.is_dir():
        print(f"[FAIL] ディレクトリが存在しません: {target}")
        sys.exit(1)

    sys.exit(check_directory(target))


if __name__ == "__main__":
    main()
