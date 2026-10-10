#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

NODES = {
 '08': 'vy20BglGWOMng5j4IvLne0BLJA7depqY',
 '10': 'YMyQA2dXW7r5AyYBs1x1AEk38zlwrZgb',
 '13': 'ZX6GRezwJly9M4eqc0m0nG6P8dqbropQ',
 '21': 'mExel2BLV5y5A0rBcp0n753pVgk9rpMq',
 '22': 'Qnp9zOoBVBe3A9EBced3RKN5W1DK0g6l',
}

OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/v6'

for ch, node in NODES.items():
    jm = None
    for _ in range(5):
        r = gw.call('get_document_content', {'nodeId': node, 'format': 'jsonml'})
        if r.get('jsonml'):
            jm = json.loads(r['jsonml'])
            break
        time.sleep(2)
    if jm is None:
        print(f'ch{ch} FAILED', r)
        continue
    json.dump(jm, open(f'{OUT}/jm_ch{ch}.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'ch{ch} saved, top-level len={len(jm)}')
