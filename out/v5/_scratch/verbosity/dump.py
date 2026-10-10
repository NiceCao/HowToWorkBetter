#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
BASE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/verbosity'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))

def leaves(node, out=None):
    if out is None: out = []
    if isinstance(node, list):
        if (len(node) >= 3 and node[0] == 'span' and isinstance(node[1], dict)
                and node[1].get('data-type') == 'leaf' and isinstance(node[-1], str)):
            out.append(node); return out
        for c in node[1:]:
            leaves(c, out)
    return out

def full_text(block):
    return ''.join(lf[-1] for lf in leaves(block))

for ch in ['39','41','42','43']:
    node = IDX[ch][1]
    res = gw.call('list_document_blocks', {'nodeId': node, 'startIndex': 0, 'endIndex': 1000, 'format': 'jsonml'})
    json.dump(res, open(os.path.join(BASE, f'blocks_ch{ch}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    blocks = res.get('blocks', [])
    print(f'=== ch{ch} node={node} blocks={len(blocks)} ===')
    for b in blocks:
        try:
            jm = json.loads(b['jsonml']) if isinstance(b.get('jsonml'), str) else b.get('jsonml')
        except Exception:
            jm = b.get('jsonml')
        t = full_text(jm) if jm else ''
        if '说人话' in t:
            print(f"  idx={b['index']} blockId={b['blockId']} type={b.get('blockType')} len={len(t)}")
print('DONE')
