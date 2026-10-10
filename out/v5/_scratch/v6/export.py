#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confirm only the intended blocks changed, then export live markdown to out/v5/chNN.md."""
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
DST = '/home/ubuntu/projects/work-guide-book/out/v5'

CHANGED = {
 '08': {'mv14az4uxm38v0jo78', 'mv14alzkzm6wu78j0e', 'mv14az4wlqfjk1swmtr', 'mv14alzlnuyp4vzt6he'},
 '10': {'mv14cxmtsaz0akcq1gb', 'mv14cpxjm94ur485m7', 'mv14cief73wpdokosfw', 'mv14cevewqz9cz038xc',
        'mv14cxmvuqofnnq51v', 'mv14cpxlgk9odu6gj7', 'mv14ciehtvsyi0yk9rj', 'mv14cevgpuuhccjdthi'},
 '13': {'mv14i9rsfds5ya0ok2a', 'mv14i9rt0tnmc82qwql'},
 '21': {'mv152cbiqtbamzd1wq', 'mv152cbjq7unlgnq9em'},
 '22': {'mv151nxxvr3b8rmj36o', 'mv1mx3yzw46qltycqva'},
}

def uid_of(b):
    if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict):
        return b[1].get('uuid')
    return None

allok = True
for ch, node in NODES.items():
    old = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))[2:]
    new = json.load(open(f'{OUT}/jm_new_ch{ch}.json', encoding='utf-8'))[2:]
    assert len(old) == len(new), ch
    diff = []
    for o, n in zip(old, new):
        if json.dumps(o, ensure_ascii=False) != json.dumps(n, ensure_ascii=False):
            diff.append(uid_of(o))
    same = set(diff) == CHANGED[ch]
    allok = allok and same
    print(f'ch{ch} changed blocks: {diff}  expected {sorted(CHANGED[ch])}  {"OK" if same else "MISMATCH"}')

print('\nEXACT-DIFF OK:', allok)

# export live markdown
for ch, node in NODES.items():
    md = None
    for _ in range(5):
        r = gw.call('get_document_content', {'nodeId': node, 'format': 'markdown'})
        if r.get('markdown'):
            md = r['markdown']; break
        time.sleep(2)
    assert md is not None, ch
    p = f'{DST}/ch{ch}.md'
    with open(p, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f'exported ch{ch} -> {p} ({len(md)} chars)')

raise SystemExit(0 if allok else 1)
