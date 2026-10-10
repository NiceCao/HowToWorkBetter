#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

for CH, idxs in {'24':[6,7,8,9], '28':list(range(4,15)), '29':[11,12,47,48,85,86,96,97]}.items():
    jm = wg2.fetch_jm(CH)
    blocks = wg2.blocks_of(jm)
    print('\n##### ch%s #####' % CH)
    for i in idxs:
        print('--%d--' % i, json.dumps(blocks[i], ensure_ascii=False))
