#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

NODES = {
 '08': 'vy20BglGWOMng5j4IvLne0BLJA7depqY',
 '10': 'YMyQA2dXW7r5AyYBs1x1AEk38zlwrZgb',
 '13': 'ZX6GRezwJly9M4eqc0m0nG6P8dqbropQ',
 '21': 'mExel2BLV5y5A0rBcp0n753pVgk9rpMq',
 '22': 'Qnp9zOoBVBe3A9EBced3RKN5W1DK0g6l',
}
for ch, node in NODES.items():
    try:
        r = gw.call('list_doc_versions', {'nodeId': node})
        items = r.get('versions') or r.get('items') or []
        print(f'ch{ch}: keys={list(r.keys())}')
        for it in items[:3]:
            print('   ', json.dumps(it, ensure_ascii=False)[:200])
    except Exception as e:
        print(f'ch{ch} err: {e}')
