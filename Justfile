# Windows では PowerShell を使用する
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# デフォルト: 利用可能なタスク一覧を表示
default:
    @just --list

# zensical.toml の nav を自動生成
# create-nav:
#     uv run python scripts/zensical_nav_generator.py -overwrite

# docs/tags.md をスキャンして自動生成
generate-tags:
    uv run python scripts/zensical_tags_generator.py

# タグを生成してビルド
build: generate-tags
    uv run zensical build

# タグを生成してローカルサーブ
serve: generate-tags
    uv run zensical serve

# 依存パッケージのインストール
sync:
    uv sync

# 開発用依存パッケージを含めてインストール
sync-dev:
    uv sync --dev

# requirements.txt を再生成（本番用）
export-requirements:
    uv export --no-dev --system-certs -o requirements.txt

# requirements-dev.txt を再生成（開発用）
export-requirements-dev:
    uv export --system-certs -o requirements-dev.txt

# uv.lock を更新
lock:
    uv lock --system-certs

# プリコミットフック実行
pre-commit:
    uv run pre-commit run --all-files

# Testing tasks
# 詳細なテストカバレッジレポートを生成
test-coverage-verbose:
    uv run pytest -s -vv --cov=. --cov-branch --cov-report term-missing --cov-report html

# HTML形式のテストレポートを生成
test-html-report:
    uv run pytest --html=htmlcov/report_page.html

# CI向けXML形式のテスト結果を生成
test-ci-xml:
    uv run python scripts/run_tests.py --report xml

# CI向けターミナル出力形式のテスト結果を生成
test-ci-term:
    uv run python scripts/run_tests.py --report term

# テストカバレッジを計算し、ターミナルとHTMLでレポート
test-coverage:
    uv run pytest --cov=. --cov-branch --cov-report=term-missing --cov-report=html
