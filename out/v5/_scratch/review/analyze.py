#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, sys, os, json

REV = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/review'
V5 = '/home/ubuntu/projects/work-guide-book/out/v5'
CHS = ['43','13','21','22','23']

def load(path):
    return open(path, encoding='utf-8').read()

ENTRY_RE = re.compile(r'^###\s*(\d+)\\?\.\s*(.*)$')

def headings(txt):
    out = []
    for ln in txt.splitlines():
        m = ENTRY_RE.match(ln)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
    return out

def analyze(ch, txt):
    lines = txt.splitlines()
    heads = headings(txt)
    nums = [n for n,_ in heads]
    print(f'===== CH{ch} =====')
    print('entries:', len(heads), 'nums:', nums)
    # numbering check
    expected = list(range(1, len(heads)+1))
    if nums == expected:
        print('numbering: 1..N 连续 OK')
    else:
        print('numbering: !! 异常 expected', expected, 'got', nums)
        dups = [x for x in set(nums) if nums.count(x)>1]
        missing = [x for x in expected if x not in nums]
        print('  dups:', dups, 'missing:', missing)
    # chapter intro
    intro = None
    for ln in lines[1:6]:
        if ln.startswith('> '):
            intro = ln; break
    print('章首导读:', '有' if intro and len(intro)>10 else '!! 缺失')
    summary = [ln for ln in lines if '本章小结' in ln]
    print('本章小结:', '有' if summary else '!! 缺失')
    # half-width double quotes
    hq = []
    for i,ln in enumerate(lines,1):
        if '"' in ln:
            hq.append((i, ln.strip()[:80]))
    print('半角双引号 \":', len(hq))
    for i,s in hq[:8]:
        print('   L%d %s' % (i,s))
    # 不是...而是
    bu = [(i,ln) for i,ln in enumerate(lines,1) if '不是' in ln and '而是' in ln]
    print('「不是…而是…」:', len(bu))
    for i,ln in bu[:8]:
        print('   L%d %s' % (i, ln.strip()[:90]))
    # consecutive hr
    hr = [i for i,ln in enumerate(lines,1) if ln.strip()=='---']
    consec = []
    for a,b in zip(hr, hr[1:]):
        nblanks = sum(1 for x in lines[a:b-1] if x.strip()=='')
        if b-a<=2:
            consec.append((a,b))
    print('分隔线总数:', len(hr), '连续两 hr:', consec if consec else '无')
    # per-entry blocks
    # split by entry heading positions
    idxs = [i for i,ln in enumerate(lines) if ENTRY_RE.match(ln)]
    idxs.append(len(lines))
    print('--- 四块检查 ---')
    block_labels = ['说人话', '怎么做', '来源', '限制与争议']
    for k in range(len(idxs)-1):
        seg = lines[idxs[k]:idxs[k+1]]
        head = seg[0]
        body = '\n'.join(seg)
        # find label lines (text of a possibly bold label may have spaces)
        got = {}
        for lab in block_labels:
            # match **lab...：** or lab：
            pat = re.compile(r'\*{0,2}' + re.escape(lab) + r'\s*[：:]\*{0,2}')
            m = pat.search(body)
            got[lab] = bool(m)
        # empties: label line with nothing after colon (roughly)
        empties = []
        for i,ln in enumerate(seg):
            s = ln.strip()
            mm = re.match(r'^\*{0,2}(说人话|怎么做|为什么\s*/\s*怎么做|来源|限制与争议)\s*[：:]\*{0,2}\s*$', s)
            if mm:
                empties.append((idxs[k]+i+1, s[:40]))
        flag = ''
        # treat 说人话 + (怎么做 or 为什么/怎么做) + 来源 + 限制与争议
        has4 = got['说人话'] and (got['怎么做']) and got['来源'] and got['限制与争议']
        if not has4:
            flag = ' !! 缺块: ' + ','.join([k2 for k2,v in got.items() if not v])
        print(f'  {head[:46]:46} 四块={"OK" if has4 else "NO"+flag}  空块={empties if empties else "-"}')
    print()

for ch in CHS:
    txt = load(os.path.join(REV, f'live_ch{ch}.md'))
    analyze(ch, txt)
