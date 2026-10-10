#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用项目自带 check_book 的解析逻辑校验导出的三章（不改仓库）。"""
import importlib.util, os, re

ROOT = '/home/ubuntu/projects/work-guide-book'
spec = importlib.util.spec_from_file_location('cb', os.path.join(ROOT, 'tools/check_book.py'))
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

ESC = [(r'\.', '.'), (r'\_', '_'), (r'\+', '+'), (r'\-', '-'), (r'\*', '*'),
       (r'\|', '|'), (r'\#', '#'), (r'\(', '('), (r'\)', ')'), (r'\[', '['), (r'\]', ']')]


def clean(t):
    for a, b in ESC:
        t = t.replace(a, b)
    return t


for num in ['24', '28', '29']:
    path = os.path.join(ROOT, 'out/v5/ch%s.md' % num)
    txt = clean(open(path, encoding='utf-8').read())
    tmp = os.path.join(ROOT, 'out/v5/_scratch/enter3', 'clean_ch%s.md' % num)
    open(tmp, 'w', encoding='utf-8').write(txt)
    h1, entries = cb.parse_chapter(tmp)
    nums = [e['num'] for e in entries]
    print('\n== ch%s  (%s) 条数=%d ==' % (num, h1[:26], len(entries)))
    print('   编号:', nums, ' 连续:', nums == list(range(1, len(nums) + 1)))
    print('   章级编号问题:', cb.check_numbering(entries) or '无')
    bad = 0
    for e in entries:
        cats = [i[0] for i in e['issues']]
        if cats:
            bad += 1
            print('   第%d条 问题: %s | %s' % (e['num'], cats, e['title'][:30]))
    print('   有问题条目:', bad)
    print('   说人话块:', sum(1 for e in entries if e['plain_len'] is not None),
          ' 有来源链接:', sum(1 for e in entries if e['src_links']),
          ' 说人话超120字:', sum(1 for e in entries if (e['plain_len'] or 0) > 120))
