#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐字比对：live 新条目正文 == staging/59 草稿正文。"""
import re, os

ROOT = '/home/ubuntu/projects/work-guide-book'
st = open(os.path.join(ROOT, 'staging/59-进厂打工真实内容.md'), encoding='utf-8').read()


def parse_staging(txt):
    out = {}
    for chunk in re.split(r'\n(?=### )', txt):
        m = re.match(r'### (\d+)\.\s*(.+)', chunk)
        if not m:
            continue
        n = int(m.group(1))
        body = chunk
        def grab(label):
            mm = re.search(r'\*\*%s：\*\*\s*(.*?)(?=\n\n|\Z)' % re.escape(label), body, re.S)
            return mm.group(1).strip() if mm else None
        # 来源块（含列表项）
        sm = re.search(r'\*\*来源：\*\*\s*\n((?:- .*\n?)+)', body)
        srcs = re.findall(r'^- (.*)$', sm.group(1), re.M) if sm else []
        out[n] = dict(title=m.group(2).strip(),
                      say=grab('说人话'),
                      wei=grab('为什么 / 怎么做'),
                      xian=grab('限制与争议'),
                      src=[s.strip() for s in srcs])
    return out


ST = parse_staging(st)


def grab_live(path, title_key):
    txt = open(path, encoding='utf-8').read()
    # 去转义
    for a, b in [(r'\.', '.'), (r'\_', '_'), (r'\*', '*')]:
        txt = txt.replace(a, b)
    chunks = re.split(r'\n(?=### )', txt)
    for c in chunks:
        if not c.startswith('### '):
            continue
        if title_key in c:
            def grab(label):
                mm = re.search(r'\*\*%s：\*\*\s*(.*?)(?=\n\n|\Z)' % re.escape(label), c, re.S)
                return mm.group(1).strip() if mm else None
            sm = re.search(r'\*\*来源：\*\*\s*\n((?:- .*\n?)+)', c)
            srcs = re.findall(r'^- (.*)$', sm.group(1), re.M) if sm else []
            return dict(say=grab('说人话'), wei=grab('为什么 / 怎么做'),
                        xian=grab('限制与争议'), src=[s.strip() for s in srcs])
    return None


MAP = [('29', 1, '流水线单调重复'), ('29', 2, '撑不住的时候别一个人扛'),
       ('28', 3, '组长当众骂人'), ('24', 9, '厂区的恋爱和异地分居')]
allok = True
for ch, n, key in MAP:
    live = grab_live(os.path.join(ROOT, 'out/v5/ch%s.md' % ch), key)
    s = ST[n]
    print('\nch%s 草稿第%d条 (%s)' % (ch, n, key))
    for f in ('say', 'wei', 'xian'):
        same = live[f] == s[f]
        allok = allok and same
        print('   %-5s 一致=%s' % (f, same))
        if not same:
            print('     live:', repr(live[f]))
            print('     stg :', repr(s[f]))
    same = live['src'] == s['src']
    allok = allok and same
    print('   来源 一致=%s (%d 条)' % (same, len(s['src'])))
    if not same:
        for a, b in zip(live['src'], s['src']):
            if a != b:
                print('     live:', repr(a))
                print('     stg :', repr(b))
print('\n全部逐字一致:', allok)
