#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys

OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/v6'

def find(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None

ch = sys.argv[1]
ids = sys.argv[2:]
jm = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))
blocks = jm[2:]
for uid in ids:
    b = find(blocks, uid)
    if b is None:
        print(f'!! {uid} NOT FOUND')
        continue
    print(f'-- {uid} --')
    print(json.dumps(b, ensure_ascii=False))
    print()
