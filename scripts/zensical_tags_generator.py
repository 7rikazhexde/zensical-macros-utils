"""ビルド前スクリプト: docs/ を全スキャンしてタグ一覧を docs/tags.md に生成する"""
import os
import re
from pathlib import Path


class ZensicalTagsGenerator:
    EXCLUDED_DIRS = {".git", "__pycache__", "assets", "stylesheets", "includes", "gist"}

    def __init__(self, docs_dir: str = "docs") -> None:
        script_dir = Path(__file__).resolve().parent
        self.project_root = script_dir.parent
        self.docs_dir = self.project_root / docs_dir
        self.output_file = self.docs_dir / "tags.md"

    def _slug(self, tag: str) -> str:
        """タグ名からアンカー ID 用スラグを生成する（Jinja2 の lower + replace と一致）"""
        return re.sub(r"\\s+", "-", tag.lower())

    def _read_front_matter(self, file_path: Path) -> dict:
        """Markdown ファイルの YAML front matter を読み込む"""
        try:
            content = file_path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                return {}
            parts = content.split("---", 2)
            if len(parts) < 3:
                return {}
            from ruamel.yaml import YAML
            yaml = YAML()
            return yaml.load(parts[1]) or {}
        except Exception:
            return {}

    def _get_title(self, file_path: Path, front_matter: dict) -> str:
        if "title" in front_matter:
            return str(front_matter["title"])
        return (
            os.path.splitext(file_path.name)[0]
            .replace("-", " ")
            .replace("_", " ")
            .title()
        )

    def _get_page_url(self, file_path: Path) -> str:
        """docs/ からの相対 URL を返す（ディレクトリ型 URL、.md 拡張子なし）"""
        rel = file_path.relative_to(self.docs_dir)
        parts = list(rel.parts)
        if parts[-1] == "index.md":
            parts = parts[:-1]
            return "/".join(parts) + "/" if parts else "./"
        parts[-1] = parts[-1][:-3]
        return "/".join(parts) + "/"

    def collect_tags(self) -> dict[str, list[dict]]:
        """全ドキュメントからタグを収集する（大文字小文字を正規化して重複排除）"""
        # slug → (表示名, ページリスト)
        slug_map: dict[str, tuple[str, list[dict]]] = {}

        for md_file in sorted(self.docs_dir.rglob("*.md")):
            if any(part in self.EXCLUDED_DIRS for part in md_file.parts):
                continue
            if md_file == self.output_file:
                continue

            fm = self._read_front_matter(md_file)
            tags = fm.get("tags")
            if not tags or not isinstance(tags, list):
                continue

            title = self._get_title(md_file, fm)
            url = self._get_page_url(md_file)

            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    continue
                tag = tag.strip()
                slug = self._slug(tag)
                if slug not in slug_map:
                    # 最初に出現した表記を採用
                    slug_map[slug] = (tag, [])
                slug_map[slug][1].append({"title": title, "url": url})

        # slug でソートして返す
        return {display: pages for _, (display, pages) in sorted(slug_map.items())}

    def generate(self) -> None:
        """docs/tags.md を生成する"""
        tag_map = self.collect_tags()

        if not tag_map:
            print("No tags found.")
            return

        lines = [
            "---",
            "title: Tags",
            "description: タグ一覧",
            "#hide:",
            "#  - feedback",
            "---",
            "",
            "# Tags",
            "",
        ]

        for tag, pages in tag_map.items():
            slug = self._slug(tag)
            pages = sorted(pages, key=lambda p: p["title"])
            lines.append(f"## {tag} {{ #{slug} }}")
            lines.append("")
            for page in pages:
                lines.append(f"- [{page['title']}](./{page['url']})")
            lines.append("")

        self.output_file.write_text("\n".join(lines), encoding="utf-8")
        total = sum(len(v) for v in tag_map.values())
        print(f"Generated {self.output_file} ({len(tag_map)} tags, {total} entries)")


def main() -> None:
    generator = ZensicalTagsGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
