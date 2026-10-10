#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

BASE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/verbosity'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))

EXPECT = {
 ('39', 'mv15wtrcgk0b6jjd0ep'): 93,
 ('41', 'mv167cb123gjfcmo1f8'): 90,
 ('42', 'mv163hnzlwygumy0339'): 72,
 ('42', 'mv162m648k2e5swnk5m'): 108,
 ('42', 'mv1628645ylbaaq2v55'): 111,
 ('43', 'mv165ooczsp4adbdn7q'): 107,
 ('43', 'mv165djj2x16zqf9fy7'): 110,
}

def find_leaves(node, out=None):
    if out is None: out = []
    if isinstance(node, list):
        if (len(node) >= 3 and node[0] == 'span' and isinstance(node[1], dict)
                and node[1].get('data-type') == 'leaf' and isinstance(node[-1], str)):
            out.append(node); return out
        for c in node[1:]:
            find_leaves(c, out)
    return out

ok = True
for ch in ['39', '41', '42', '43']:
    node = IDX[ch][1]
    res = gw.call('list_document_blocks', {'nodeId': node, 'startIndex': 0, 'endIndex': 1000, 'format': 'jsonml'})
    byid = {b['blockId']: b for b in res['blocks']}
    print(f'===== ch{ch}: {len(res["blocks"])} blocks =====')
    for (c, bid), exp in EXPECT.items():
        if c != ch: continue
        b = byid[bid]
        jm = json.loads(b['jsonml'])
        lvs = find_leaves(jm)
        bold = [l for l in lvs if l[1].get('bold')]
        nonbold = [l for l in lvs if not l[1].get('bold')]
        label_ok = len(bold) == 1 and bold[0][-1] == '说人话：'
        text = nonbold[0][-1]
        n = len(text) - (1 if text.startswith(' ') else 0)
        good = label_ok and n == exp and n <= 120
        ok = ok and good
        print(f'  {bid}: bold标签={"保留" if label_ok else "丢失!"} 正文={n}字 (期望{exp}) {"OK" if good else "FAIL"}')
    # ch42 为什么校验
    if ch == '42':
        wb = byid['mv162865zeko41fcvrs']
        wt = ''.join(l[-1] for l in find_leaves(json.loads(wb['jsonml'])) if not l[1].get('bold'))
        has = '都列为不得贿赂的对象' in wt
        print(f'  ch42 为什么(idx75): 已含第八条对象清单 = {has}')
        ok = ok and has

print('\nVERIFY', 'PASS' if ok else 'FAIL')
