#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the 9 rewrites + 9 appends, then export markdown to out/v5/chNN.md."""
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

SAY_IDS = {
 '08': ['mv14az4uxm38v0jo78', 'mv14alzkzm6wu78j0e'],
 '10': ['mv14cxmtsaz0akcq1gb', 'mv14cpxjm94ur485m7', 'mv14cief73wpdokosfw', 'mv14cevewqz9cz038xc'],
 '13': ['mv14i9rsfds5ya0ok2a'],
 '21': ['mv152cbiqtbamzd1wq'],
 '22': ['mv151nxxvr3b8rmj36o'],
}
APPEND_IDS = {
 '08': ['mv14az4wlqfjk1swmtr', 'mv14alzlnuyp4vzt6he'],
 '10': ['mv14cxmvuqofnnq51v', 'mv14cpxlgk9odu6gj7', 'mv14ciehtvsyi0yk9rj', 'mv14cevgpuuhccjdthi'],
 '13': ['mv14i9rt0tnmc82qwql'],
 '21': ['mv152cbjq7unlgnq9em'],
 '22': ['mv1mx3yzw46qltycqva'],
}

def leaves_nodes(b, out):
    if isinstance(b, list):
        if len(b) >= 2 and isinstance(b[1], dict) and b[1].get('data-type') == 'leaf':
            out.append(b)
            return out
        for c in b[1:]:
            leaves_nodes(c, out)
    return out

def text_of(b):
    return ''.join((n[2] if len(n) >= 3 and isinstance(n[2], str) else '') for n in leaves_nodes(b, []))

def nz(s):
    return len(''.join(s.split()))

def find(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None

ok = True
new_jm = {}
for ch, node in NODES.items():
    jm = None
    for _ in range(5):
        r = gw.call('get_document_content', {'nodeId': node, 'format': 'jsonml'})
        if r.get('jsonml'):
            jm = json.loads(r['jsonml']); break
        time.sleep(2)
    assert jm, ch
    new_jm[ch] = jm
    json.dump(jm, open(f'{OUT}/jm_new_ch{ch}.json', 'w', encoding='utf-8'), ensure_ascii=False)
    blocks = jm[2:]
    old = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))[2:]
    print(f'===== ch{ch} blocks {len(old)} -> {len(blocks)} =====')
    assert len(old) == len(blocks), 'block count changed!'
    for uid in SAY_IDS[ch]:
        b = find(blocks, uid)
        assert b, uid
        ln = leaves_nodes(b, [])
        bold = [n for n in ln if n[1].get('bold')]
        body = [n for n in ln if not n[1].get('bold')]
        assert len(bold) == 1 and text_of(bold[0]) == '说人话：', f'{uid} bold label lost: {[text_of(n) for n in ln]}'
        t = text_of(body[0]).strip()
        c = nz(t)
        stat = 'OK' if c <= 120 else 'FAIL'
        if c > 120:
            ok = False
        print(f'  SAY {uid} bold=√ len={c} {stat}')
    for uid in APPEND_IDS[ch]:
        b = find(blocks, uid)
        assert b, uid
        t = text_of(b)
        print(f'  APP {uid} ok text tail: ...{t[-34:]}')

print('\nALL <=120 AND BOLD OK:', ok)
raise SystemExit(0 if ok else 1)
