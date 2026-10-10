#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump raw jsonml for anchors + sample entries of ch24/28/29."""
import json, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

WANT = {
 '24': [1, 4,5,6,7,8,9, 47,48,49,56,57,58,63,64],
 '28': [1, 52,53,54,55,56,57,58, 77,78, 87,88,89,100,101],
 '29': [1, 4,5,6,7,8,9,10,11,12,13, 38,39, 48,49, 85,86, 96,97],
}

for CH, idxs in WANT.items():
    jm = wg2.fetch_jm(CH)
    blocks = wg2.blocks_of(jm)
    print('\n################## ch%s ##################' % CH)
    for i in idxs:
        b = blocks[i]
        print('---- idx %d ----' % i)
        print(json.dumps(b, ensure_ascii=False))
    # full text of intro + summary
    print('--- INTRO full:', repr(wg2.text_of(blocks[1])))
    print('--- SUMMARY full:', repr(wg2.text_of(blocks[-1])))
