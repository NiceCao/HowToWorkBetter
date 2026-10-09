#!/usr/bin/env python3
"""生成 sitemap.xml：按站点里实际存在的 HTML 页面来列。

覆盖范围：
  - 根目录的 index.html（首页，网址就是站点根）
  - ch/*.html（50 个章节页）

规则：
  - loc 前缀固定为 GitHub Pages 站点地址；
  - lastmod 取该文件在磁盘上的最后修改日期（UTC，精确到天）；
  - 只用 Python 3 标准库，无第三方依赖。

用法：
    python3 tools/build_sitemap.py
"""

import datetime
import os
from urllib.parse import quote
from xml.sax.saxutils import escape

SITE = "https://nicecao.github.io/HowToWorkBetter/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sitemap.xml")


def collect_pages():
    """返回 [(相对路径, 磁盘路径), ...]，首页的相对路径为空串。"""
    pages = []

    index = os.path.join(ROOT, "index.html")
    if os.path.isfile(index):
        pages.append(("", index))

    ch_dir = os.path.join(ROOT, "ch")
    if os.path.isdir(ch_dir):
        for name in sorted(os.listdir(ch_dir)):
            if name.lower().endswith(".html"):
                pages.append(("ch/" + name, os.path.join(ch_dir, name)))

    return pages


def lastmod(path):
    ts = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")


def main():
    pages = collect_pages()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for rel, path in pages:
        # 中文文件名按 RFC 3986 做百分号编码，再交给 XML 转义（尖括号、& 等）。
        loc = SITE + quote(rel, safe="/")
        lines.append("  <url>")
        lines.append("    <loc>%s</loc>" % escape(loc))
        lines.append("    <lastmod>%s</lastmod>" % lastmod(path))
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>%s</priority>" % ("1.0" if rel == "" else "0.8"))
        lines.append("  </url>")
    lines.append("</urlset>")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    chapters = len(pages) - (1 if pages and pages[0][0] == "" else 0)
    print("已生成 %s" % OUT)
    print("共 %d 条：首页 1 条 + 章节页 %d 条" % (len(pages), chapters))


if __name__ == "__main__":
    main()
