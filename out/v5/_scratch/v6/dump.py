#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/v6'
TARGETS = {
 '08': ['mv14az4uxm38v0jo78', 'mv14alzkzm6wu78j0e'],
 '10': ['mv14cxmtsaz0akcq1gb', 'mv14cpxjm94ur485m7', 'mv14cief73wpdokosfw', 'mv14cevewqz9cz038xc'],
 '13': ['mv14i9rsfds5ya0ok2a'],
 '21': ['mv152cbiqtbamzd1wq'],
 '22': ['mv151nxxvr3b8rmj36o'],
}

def find(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None

for ch, ids in TARGETS.items():
    jm = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))
    blocks = jm[2:]
    print(f'===== ch{ch} =====')
    for uid in ids:
        b = find(blocks, uid)
        assert b is not None, uid
        print(f'-- {uid} --')
        print(json.dumps(b, ensure_ascii=False))
        print()
