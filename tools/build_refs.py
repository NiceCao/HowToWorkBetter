#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 docs/引用对照.md —— 《高性价比工作指南》416 条建议的逐条来源对照表。

把每条建议「来源：」里列出的引用摊开（机构/文件名 + 链接），按章分组，
便于人工一眼看出「这条的引用能不能证明这条论点」。

只依赖标准库；可重复运行（幂等，输出完全一致）。
用法：  python3 tools/build_refs.py
"""

import json
import re
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOOK = os.path.join(ROOT, "book")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "引用对照.md")

TITLE_MAX = 30  # 标题截断字数

ENTRY_RE = re.compile(r"^### (\d+)\. (.+?)[ \t]*$", re.M)
# 「来源：」标题行，兼容 **来源：** 与裸 来源：；本行余下内容也算一条内联来源
SRC_RE = re.compile(r"^\*{0,2}来源：\*{0,2}[ \t]*(.*)$")
# 段落小标题（结束来源块的标志）
HEAD_RE = re.compile(
    r"^(?:#|\*{1,2}[^*]|(?:限制与争议|竞业限制|说人话|怎么用|为什么|"
    r"关键提醒|注|第一步|第二步|第三步|规则|每年|两个|四条)[：:])"
)
BULLET_RE = re.compile(r"^[-*][ \t]+(.+)$")
URL_RE = re.compile(r"https?://[^\s)>\]，。、；;\"']+")


def truncate(s, n):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "…"


def clean_name(text):
    """从一条来源文本里取出「机构/文件名」，去掉尾部链接与标点。"""
    name = URL_RE.sub("", text).strip()
    name = name.strip(" \t·.-—")
    return name.strip()


def parse_sources(body):
    """在一个条目正文里抽取「来源：」块，返回 (来源条目列表, 是否有来源块)。

    每条来源 = {"raw": 原文, "name": 名称, "urls": [链接...]}
    """
    lines = body.split("\n")
    start = None
    inline = ""
    for i, ln in enumerate(lines):
        m = SRC_RE.match(ln.strip())
        if m:
            start = i
            inline = m.group(1).strip()
            break
    if start is None:
        return [], False

    raw_entries = []
    if inline:
        raw_entries.append(inline)
    for ln in lines[start + 1:]:
        s = ln.strip()
        if s == "":
            # 空行后若紧跟小标题/正文段，也算块结束；这里保守：跳过空行
            continue
        bm = BULLET_RE.match(s)
        if bm:
            raw_entries.append(bm.group(1).strip())
            continue
        if HEAD_RE.match(s):
            break
        # 其它非项目符号行：视为上一条的续行
        if raw_entries:
            raw_entries[-1] = raw_entries[-1] + " " + s
        else:
            raw_entries.append(s)

    sources = []
    for raw in raw_entries:
        if not raw:
            continue
        urls = URL_RE.findall(raw)
        sources.append({
            "raw": raw,
            "name": clean_name(raw),
            "urls": urls,
        })
    return sources, True


def fmt_source(src):
    urls = src["urls"]
    if urls:
        primary = urls[0]
        label = src["name"] or primary
        out = "[{}]({})".format(label, primary)
        for extra in urls[1:]:
            out += " · <{}>".format(extra)
        return out
    # 无链接
    return "⚠️（无链接）{}".format(src["raw"])


def main():
    chapters = json.load(open(os.path.join(DATA, "chapters.json"), encoding="utf-8"))

    total_items = 0
    with_link = 0
    notfound = 0
    no_src_block = 0
    links_total = 0
    links_uniq = set()
    ge3 = 0

    sections = []
    for ch in chapters:
        path = os.path.join(BOOK, ch["file"])
        text = open(path, encoding="utf-8").read()
        matches = list(ENTRY_RE.finditer(text))

        ch_lines = []
        ch_items = 0
        for i, m in enumerate(matches):
            num = int(m.group(1))
            title = m.group(2).strip()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[m.end():end]

            sources, has_block = parse_sources(body)
            total_items += 1
            ch_items += 1

            n_links = sum(len(s["urls"]) for s in sources)
            for s in sources:
                links_total += len(s["urls"])
                links_uniq.update(s["urls"])
            if has_block and n_links == 0:
                no_src_block += 0
            if not has_block:
                no_src_block += 1
            if n_links >= 1:
                with_link += 1
            block_text = " ".join(s["raw"] for s in sources)
            if "未找到" in block_text:
                notfound += 1
            if len(sources) >= 3:
                ge3 += 1

            ch_lines.append("- **{}** ｜ {} ｜ 来源 {} 条".format(
                num, truncate(title, TITLE_MAX), len(sources)))
            for s in sources:
                ch_lines.append("  - " + fmt_source(s))

        heading = ch.get("h1") or ch["file"]
        sections.append("## {}\n\n{}\n".format(heading, "\n".join(ch_lines)))

    header = []
    header.append("# 引用对照表（416 条建议 · 逐条来源）\n")
    header.append("本文件由 `tools/build_refs.py` 生成，请勿手改；重复运行结果一致（幂等）。")
    header.append("把每条建议「来源：」里列出的引用摊开，便于人工核对"
                  "「这条的引用能不能证明这条论点」。\n")
    header.append("## 统计摘要\n")
    header.append("- 条目总数：{}".format(total_items))
    header.append("- 有官方来源（至少 1 条链接）的条数：{}".format(with_link))
    header.append("- 写「未找到直接相关的官方数据」的条数：{}".format(notfound))
    header.append("- 来源链接总数：{}".format(links_total))
    header.append("- 来源链接去重数：{}".format(len(links_uniq)))
    header.append("- 来源 ≥ 3 条的条目数：{}".format(ge3))
    header.append("- 没有「来源：」块的条目数：{}".format(no_src_block))
    header.append("")
    header.append("口径说明：「来源条数」按条目「来源：」块里列出的引用条目数统计"
                  "（含写在同一行的内联来源）；一条引用含多个链接时链接分别计入总数。"
                  "「未找到」条数指来源块中出现「未找到…官方数据/统计」表述的条目。\n")
    header.append("---\n")

    doc = "\n".join(header) + "\n" + "\n".join(sections).rstrip() + "\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)

    nbytes = os.path.getsize(OUT)
    nlines = doc.count("\n") + 1
    # 表行数 = 条目摘要行数
    table_rows = total_items
    print("OUT", OUT)
    print("lines", nlines, "bytes", nbytes)
    print("table_rows(items)", table_rows)
    print("stats total=%d with_link=%d notfound=%d links=%d uniq=%d ge3=%d no_block=%d"
          % (total_items, with_link, notfound, links_total, len(links_uniq), ge3, no_src_block))


if __name__ == "__main__":
    main()
