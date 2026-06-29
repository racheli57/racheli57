#!/usr/bin/env python3
"""校验推广文档生成脚本的文章数量、标题长度、正文长度与 docx 输出。"""
from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

import generate_policy_docx as generator


def chinese_len(text: str) -> int:
    return len(text.replace(" ", ""))


def validate_articles() -> list[str]:
    errors: list[str] = []
    articles = generator.build_ip_rights_article()
    if len(articles) != 10:
        errors.append(f"文章数量应为10，实际为{len(articles)}")
    titles = {a.title for a in articles}
    if len(titles) != len(articles):
        errors.append("标题存在重复")
    for article in articles:
        title_len = chinese_len(article.title)
        body_len = chinese_len(article.body)
        if not 15 <= title_len <= 30:
            errors.append(f"标题长度不合规：{article.title}（{title_len}）")
        if not 850 <= body_len <= 1450:
            errors.append(f"正文长度偏离1000字：{article.title}（{body_len}）")
        for keyword in ("200万元", "3000万元", "337", "深圳", "海外"):
            if keyword not in article.body:
                errors.append(f"正文缺少关键词 {keyword}：{article.title}")
    return errors


def validate_outputs() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out = root / "docs"
        summary = root / "generated_documents.md"
        paths = generator.generate(out, summary)
        if len(paths) != 10:
            errors.append(f"输出docx数量应为10，实际为{len(paths)}")
        if not summary.exists() or "推广文档汇总" not in summary.read_text(encoding="utf-8"):
            errors.append("Markdown汇总文件未正确生成")
        for path in paths:
            if not path.exists():
                errors.append(f"文件不存在：{path}")
                continue
            try:
                with zipfile.ZipFile(path) as zf:
                    names = set(zf.namelist())
                    if "word/document.xml" not in names:
                        errors.append(f"docx缺少 word/document.xml：{path}")
            except zipfile.BadZipFile:
                errors.append(f"docx不是有效zip包：{path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验批量政策推广文档生成结果")
    parser.add_argument("--skip-output", action="store_true", help="仅校验文章参数，不生成临时文件")
    args = parser.parse_args()
    errors = validate_articles()
    if not args.skip_output:
        errors.extend(validate_outputs())
    if errors:
        print("校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("校验通过：10篇文章、标题长度、正文长度、docx与Markdown输出均符合预期")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
