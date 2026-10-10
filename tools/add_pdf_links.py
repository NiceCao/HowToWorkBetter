# -*- coding: utf-8 -*-
"""给 dist/HowToWorkBetter.pdf 补上「能点的」链接：书签（大纲）+ 目录页跳转 + 封面网址。

背景：google-chrome --print-to-pdf 会把正文里的外链（来源网址）写成 /URI 注释，
但目录里的站内锚点（#ch01）不会变成可点击的内部跳转，封面上的网址也不是链接，
整本 PDF 也没有书签树 —— 读者在阅读器里点目录点不动。

本脚本做三件事（后处理，不改内容）：
1. 按 51 章建 PDF 书签（大纲）：阅读器侧边栏/目录树可直接跳章；
2. 目录页每一行加内部跳转链接：点「第N章 …」直接翻到该章；
3. 封面上的网址加外链。

    python3 tools/add_pdf_links.py [dist/HowToWorkBetter.pdf]
"""
import os
import re
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, NameObject, NumberObject,
                          RectangleObject, TextStringObject)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PDF = os.path.join(ROOT, 'dist', 'HowToWorkBetter.pdf')
CH_RE = re.compile(r'第\s*(\d{1,2})\s*章')
URL_RE = re.compile(r'https?://[^\s)]+')


def page_chunks(page):
    """返回该页的文本块 [(x, y, text, size)]，坐标已换算成 PDF 页面坐标（左下角为原点）。

    注意：pypdf 的 visitor 给的 tm 是文本空间坐标，必须和当前的 cm（CTM）相乘，
    否则拿到的 y 会是 2000 多这种超出页高（841.9pt）的值 —— 链接矩形会跑到页面外，点不到。
    """
    out = []

    def visitor(text, cm, tm, font_dict, font_size):
        if not (text and text.strip()):
            return
        a, b, c, d, e, f = [float(v) for v in cm]
        x = float(tm[4]) * a + float(tm[5]) * c + e
        y = float(tm[4]) * b + float(tm[5]) * d + f
        scale = abs(a * d - b * c) ** 0.5 or 1.0
        out.append((x, y, text, (font_size or 10.5) * scale))

    page.extract_text(visitor_text=visitor)
    return out


def lines_of(chunks, tol=3.5):
    """把文本块按 y 归并成行，返回 [(y, x_min, x_max, text, size)]。"""
    rows = []
    for x, y, text, size in sorted(chunks, key=lambda c: (-c[1], c[0])):
        for r in rows:
            if abs(r[0] - y) <= tol:
                r[1] = min(r[1], x)
                r[2] = max(r[2], x + len(text) * size * 0.62)
                r[3] += text
                break
        else:
            rows.append([y, x, x + len(text) * size * 0.62, text, size])
    return [(r[0], r[1], r[2], r[3], r[4]) for r in rows]


def find_toc_and_chapters(reader):
    """返回 (目录页码范围, {章号: 起始页下标}, 章标题)。"""
    n_pages = len(reader.pages)
    per_page_lines = [lines_of(page_chunks(p)) for p in reader.pages]
    toc_pages = []
    for i in range(min(8, n_pages)):
        hits = sum(1 for ln in per_page_lines[i] if CH_RE.search(ln[3]))
        if hits >= 5:
            toc_pages.append(i)
    if not toc_pages:
        raise SystemExit('[links] 没找到目录页')
    last_toc = max(toc_pages)
    start = {}
    titles = {}
    # 每章都从新页开始，所以「章名在页面最开头」才是章首页；
    # 只按「页面里出现第N章」会被正文里的交叉引用（如「见第28章」）带偏。
    for i in range(last_toc + 1, n_pages):
        text = (reader.pages[i].extract_text() or '').lstrip()
        m = re.match(r'第\s*(\d{1,2})\s*章', text)
        if not m:
            continue
        num = int(m.group(1))
        if num in start:
            continue
        start[num] = i
        first_line = text.split('\n', 1)[0].strip()
        titles[num] = first_line
    return toc_pages, start, titles


def goto_dest(writer, target_page_index):
    ref = writer.pages[target_page_index].indirect_reference
    dest = ArrayObject([ref, NameObject('/Fit')])
    return DictionaryObject({
        NameObject('/S'): NameObject('/GoTo'),
        NameObject('/D'): dest,
    })


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    reader = PdfReader(path)
    toc_pages, start, titles = find_toc_and_chapters(reader)
    print('[links] 目录页(0基): %s ｜ 定位到章节: %d 章' % (toc_pages, len(start)))

    writer = PdfWriter()
    writer.append(reader)

    # 1) 书签
    writer.add_outline_item('目录', toc_pages[0])
    for num in sorted(start):
        name = re.sub(r'^第\s*\d{1,2}\s*章\s*', '', titles[num]).strip()
        writer.add_outline_item('第%d章 %s' % (num, name), start[num])

    # 2) 目录页内部跳转 + 3) 封面网址
    n_toc_links = 0
    n_cover = 0
    width = float(writer.pages[toc_pages[0]].mediabox.width)
    for i in range(len(writer.pages)):
        page = reader.pages[i]
        add = []
        if i in toc_pages:
            for y, x0, x1, text, size in lines_of(page_chunks(page)):
                m = CH_RE.search(text)
                if not m:
                    continue
                num = int(m.group(1))
                if num not in start:
                    continue
                rect = RectangleObject([max(4.0, x0 - 6), y - 3.5, width - 34, y + size * 0.9])
                add.append(DictionaryObject({
                    NameObject('/Type'): NameObject('/Annot'),
                    NameObject('/Subtype'): NameObject('/Link'),
                    NameObject('/Rect'): rect,
                    NameObject('/Border'): ArrayObject([NumberObject(0)] * 3),
                    NameObject('/A'): goto_dest(writer, start[num]),
                }))
                n_toc_links += 1
        elif i == 0:
            have = set()
            for a in (page.get('/Annots') or []):
                o = a.get_object()
                act = o.get('/A')
                if act is not None and '/URI' in act.get_object():
                    have.add(str(act.get_object()['/URI']))
            for y, x0, x1, text, size in lines_of(page_chunks(page)):
                for u in URL_RE.findall(text):
                    if u in have:
                        continue
                    i2 = text.find(u)
                    x_start = x0 + i2 * size * 0.5
                    rect = RectangleObject([x_start, y - 3.5, x_start + len(u) * size * 0.5, y + size * 0.9])
                    add.append(DictionaryObject({
                        NameObject('/Type'): NameObject('/Annot'),
                        NameObject('/Subtype'): NameObject('/Link'),
                        NameObject('/Rect'): rect,
                        NameObject('/Border'): ArrayObject([NumberObject(0)] * 3),
                        NameObject('/A'): DictionaryObject({
                            NameObject('/S'): NameObject('/URI'),
                            NameObject('/URI'): TextStringObject(u),
                        }),
                    }))
                    n_cover += 1
        if add:
            writer.add_annotation(i, add[0])
            for a in add[1:]:
                writer.add_annotation(i, a)

    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        writer.write(f)
    os.replace(tmp, path)
    print('[links] 已写入 %s ｜ 目录跳转=%d ｜ 封面外链=%d ｜ 书签=%d'
          % (path, n_toc_links, n_cover, 1 + len(start)))
    return path


if __name__ == '__main__':
    main()
