#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe ch11 jsonml structure before editing."""
import json, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

jm = wg2.fetch_jm('11')
print('top:', jm[0], jm[1])
blocks = wg2.blocks_of(jm)
print('nblocks =', len(blocks))
for i in [0, 1, 2, 107, 108, 109, 110, 111, 115, 116, 117, 118, 119]:
    b = blocks[i]
    print('---- idx', i, '----')
    print(json.dumps(b, ensure_ascii=False)[:500])
    print('   text=', repr(wg2.text_of(b)))
    print('   uuid=', wg2.uid(b))
