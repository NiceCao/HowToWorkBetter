#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, json

REV = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/review'
CHS = ['43','13','21','22','23']
ENTRY = re.compile(r'^###\s*(\d+)\\?\.\s*(.*)$')
LABEL = re.compile(r'^\*{0,2}(说人话|限制与争议|来源|本章小结)\s*[：:]\*{0,2}', )

def analyze(ch):
    lines = open(f'{REV}/live_ch{ch}.md', encoding='utf-8').read().splitlines()
    idx = [i for i, l in enumerate(lines) if ENTRY.match(l)] + [len(lines)]
    heads = [ENTRY.match(lines[i]).group(1) for i in idx[:-1]]
    nums = [int(h) for h in heads]
    print(f'===== CH{ch} : {len(nums)} 条 =====')
    print(f'  编号: {nums}  {"连续OK" if nums==list(range(1,len(nums)+1)) else "!!异常"}')
    # intro (first blockquote after title) & summary
    intro = next((l for l in lines[1:6] if l.startswith('>')), '')
    summ = [l for l in lines if l.startswith('>') and '本章小结' in l]
    print(f'  章首导读: {"有" if intro else "无"}   本章小结: {"有" if summ else "无"}')
    # half-width quote / 不是…而是
    hq = sum(1 for l in lines if '"' in l)
    bu = sum(1 for l in lines if '不是' in l and '而是' in l)
    print(f'  半角双引号={hq}  「不是…而是…」={bu}')
    # consecutive hr
    hr = [i for i, l in enumerate(lines) if l.strip() == '---']
    cons = [(a+1,b+1) for a, b in zip(hr, hr[1:]) if b-a <= 2]
    print(f'  分隔线={len(hr)}  连续hr={cons if cons else "无"}')
    # per-entry blocks
    for k in range(len(idx)-1):
        seg = lines[idx[k]:idx[k+1]]
        labels = [(i, LABEL.match(l).group(1) if LABEL.match(l) else None) for i, l in enumerate(seg)]
        # force second block detection: any bold label not in {说人话,来源,限制与争议,本章小结}
        found = {'说人话': False, '第二块': False, '来源': False, '限制与争议': False}
        content_ok = {'说人话': False, '第二块': False, '来源': False, '限制与争议': False}
        labs = []
        for i, l in enumerate(seg):
            m = re.match(r'^\*{0,2}([^：:]{1,12})\s*[：:]\*{0,2}', l)
            if m and (l.startswith('**') or re.match(r'^(说人话|限制与争议|标签|来源|怎么|为什么|可以)', l) or '：' in l[:16]):
                labs.append((i, m.group(1).strip()))
        for j, (i, lab) in enumerate(labs):
            nxt = labs[j+1][0] if j+1 < len(labs) else len(seg)
            body = ('\n'.join(seg[i:nxt])).split('：', 1)
            rest = body[1] if len(body) > 1 else ''
            rest = re.sub(r'\*{1,2}', '', rest)
            rest_lines = [x for x in rest.split('\n') if x.strip() and x.strip() != '-']
            nonempty = bool(rest_lines)
            if lab == '说人话': key = '说人话'
            elif lab == '来源': key = '来源'
            elif lab == '限制与争议': key = '限制与争议'
            elif lab == '本章小结': continue
            else: key = '第二块'
            found[key] = True; content_ok[key] = content_ok[key] or nonempty
        miss = [k2 for k2 in ['说人话','第二块','来源','限制与争议'] if not found[k2]]
        emptyblk = [k2 for k2 in found if found[k2] and not content_ok[k2]]
        body_lines = sum(1 for l in seg[1:] if l.strip())
        flag = ''
        if miss: flag += f' 缺块={miss}'
        if emptyblk: flag += f' 空块={emptyblk}'
        if body_lines == 0: flag += ' 只剩标题'
        if flag:
            print(f'  {heads[k]:>3}. {seg[0][:40]:40}{flag}')
    print()

for ch in CHS:
    analyze(ch)
