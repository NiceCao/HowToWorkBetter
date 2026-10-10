#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 book/*.md 生成 data/entries.json（检索页用的别章条目索引）。

为什么要这个脚本：entries.json 以前是手工生成的一次性快照，正文增删条目后不会自动更新，
检索页会显示过期条数（章节条数、全书条数）。现在纳入构建链：
    python3 tools/build_entries.py && python3 build_items.py && python3 build_index.py && python3 build_site.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / 'book'
OUT = ROOT / 'data' / 'entries.json'

rows = []
for f in sorted(BOOK.glob('*.md')):
    n = int(f.name[:2])
    stem = f.stem
    text = f.read_text(encoding='utf-8')
    for m in re.finditer(r'^### +(\d+)\.\s*(.+?)\s*$', text, re.M):
        no, title = int(m.group(1)), m.group(2).strip()
        seg = text[m.end():m.end() + 500]
        lv = re.search(r'性价比\s*[:：]\s*(极高|高|一般)', seg)
        level = f'{lv.group(1)}性价比' if lv else ''
        rows.append({'chapter': n, 'chapter_title': stem, 'level': level,
                     'entry': no, 'title': title})

OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'entries.json 已生成：{len(rows)} 条 / {len({r["chapter"] for r in rows})} 章')
