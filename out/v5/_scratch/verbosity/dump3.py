#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
BASE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/verbosity'
res = json.load(open(os.path.join(BASE, 'blocks_ch42.json'), encoding='utf-8'))
blocks = {b['index']: b for b in res['blocks']}
for i in [73, 74, 75, 76]:
    b = blocks.get(i)
    if not b: 
        print(f'idx {i}: MISSING'); continue
    print(f'\n##### ch42 idx={i} blockId={b["blockId"]} type={b.get("blockType")} #####')
    print(json.dumps(b.get('jsonml'), ensure_ascii=False)[:2500])
