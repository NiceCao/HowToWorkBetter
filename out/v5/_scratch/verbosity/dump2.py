#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
BASE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/verbosity'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))

TARGETS = {
 '39': [17],
 '41': [92],
 '42': [6, 35, 74],
 '43': [6, 21],
}

for ch, idxs in TARGETS.items():
    node = IDX[ch][1]
    res = json.load(open(os.path.join(BASE, f'blocks_ch{ch}.json'), encoding='utf-8'))
    blocks = {b['index']: b for b in res['blocks']}
    for i in idxs:
        b = blocks[i]
        print(f'\n##### ch{ch} idx={i} blockId={b["blockId"]} #####')
        print(b['jsonml'])
