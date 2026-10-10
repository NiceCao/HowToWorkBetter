#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys

OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/v6'

def leaves(node, out):
    if isinstance(node, list):
        if len(node) >= 2 and isinstance(node[1], dict) and node[1].get('data-type') == 'leaf':
            out.append(node[2] if len(node) >= 3 and isinstance(node[2], str) else '')
            return out
        for c in node[1:]:
            leaves(c, out)
    return out

def text_of(b):
    return ''.join(leaves(b, []))

ch = sys.argv[1]
jm = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))
blocks = jm[2:]
for i, b in enumerate(blocks):
    if not isinstance(b, list) or len(b) < 2 or not isinstance(b[1], dict):
        continue
    t = text_of(b)
    typ = b[0]
    uid = b[1].get('uuid')
    isbold = 'bold' in json.dumps(b, ensure_ascii=False)
    print(f'{i:3d} {typ:5s} bold={int(isbold)} {uid} | {t[:70]}')
