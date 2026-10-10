#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
NODES = {ch: IDX[ch][1] for ch in ('08','35','39','43')}
OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'

for ch, node in NODES.items():
    # list_document_blocks
    for _ in range(4):
        r = gw.call('list_document_blocks', {'nodeId': node})
        if r.get('success'):
            break
        time.sleep(2)
    else:
        print(f'ch{ch} list FAILED', r)
        continue
    blocks = r['blocks']
    lines = []
    for i, blk in enumerate(blocks):
        el = blk.get('element', {})
        bid = el.get('id')
        typ = None
        txt = ''
        for k in ('paragraph','heading','blockquote','unorderedList','orderedList','code','hr','divider'):
            if k in el:
                typ = k
                v = el[k]
                if isinstance(v, dict):
                    txt = v.get('text','')
                break
        if typ is None:
            typ = '?' + ','.join(el.keys())
        lines.append(f'{i:3d} | {bid} | {typ:16s} | {txt[:90]}')
    open(f'{OUT}/blocks_ch{ch}.txt','w',encoding='utf-8').write('\n'.join(lines))
    print(f'ch{ch}: {len(blocks)} blocks -> blocks_ch{ch}.txt')
