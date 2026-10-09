#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把钉钉文档导出的线上正文（out/v2/chNN.md）应用到仓库的 book/NN-章名.md。

用法：python3 tools/apply_live.py            # 只处理 out/v2 里存在的章
      python3 tools/apply_live.py 01 02 03   # 只处理指定章

做的事：
1. 去掉钉钉 markdown 导出的转义（\. \_ \+ \- \* \| 等）
2. 按 data/chapters.json 的映射写到 book/NN-章名.md
3. 打印每章：条目数、正文字数（去空白）、改前 vs 改后
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_DIR = '/home/ubuntu/projects/work-guide-50/out/v2'   # 钉钉导出目录（书稿工程目录，不进本仓库）
os.chdir(ROOT)

CH = {c['n']: c for c in json.load(open('data/chapters.json', encoding='utf-8'))}
ESC = [(r'\.', '.'), (r'\_', '_'), (r'\+', '+'), (r'\-', '-'), (r'\*', '*'), (r'\|', '|'),
       (r'\#', '#'), (r'\(', '('), (r'\)', ')'), (r'\[', '['), (r'\]', ']')]


def clean(text):
    for pat, rep in ESC:
        text = text.replace(pat, rep)
    return text


def entries(md):
    return [b for b in re.split(r'\n(?=### )', md) if b.startswith('### ')]


def body_chars(md):
    """整章正文字数（去掉标题行、元信息行与空白）"""
    t = re.sub(r'^>.*$', '', md, flags=re.M)
    t = re.sub(r'^#.*$', '', t, flags=re.M)
    return len(re.sub(r'\s+', '', t))


want = [a.zfill(2) for a in sys.argv[1:]]
srcs = sorted(glob.glob(os.path.join(LIVE_DIR, 'ch[0-9][0-9].md')))
rows = []
for src in srcs:
    num = int(os.path.basename(src)[2:4])
    if want and f'{num:02d}' not in want:
        continue
    if num not in CH:
        print(f'· 跳过 {src}（不在章节表里）')
        continue
    dst = os.path.join('book', CH[num]['file'])
    old = open(dst, encoding='utf-8').read() if os.path.exists(dst) else ''
    md = clean(open(src, encoding='utf-8').read()).rstrip() + '\n'
    open(dst, 'w', encoding='utf-8').write(md)
    rows.append((num, CH[num]['file'], len(entries(md)), len(entries(old)),
                 body_chars(old), body_chars(md)))

print(f'{"章":>3}  {"文件":32} 条目(旧→新)   正文字数(改前→改后)')
for num, f, e_new, e_old, c_old, c_new in sorted(rows):
    flag = '' if e_new == e_old else '  ⚠ 条目数变了'
    print(f'{num:03d}  {f:32} {e_old:>3}→{e_new:<3}   {c_old:>6}→{c_new:<6}{flag}')
print(f'\n共应用 {len(rows)} 章。接着跑：python3 build_items.py && python3 build_index.py && python3 build_site.py')
