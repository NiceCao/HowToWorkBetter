#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os

OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/v6'

def leaves(node, out):
    if isinstance(node, list):
        if len(node) >= 2 and isinstance(node[1], dict) and node[1].get('data-type') == 'leaf':
            out.append(node[2] if len(node) >= 3 and isinstance(node[2], str) else '')
            return out
        for c in node[1:]:
            leaves(c, out)
    return out

def text_of(b):
    return ''.join(leaves(b, []))

for ch in ['08', '10', '13', '21', '22']:
    jm = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))
    blocks = jm[2:]
    print(f'===== ch{ch} =====')
    head = ''
    for b in blocks:
        if not isinstance(b, list) or not isinstance(b[1], dict):
            continue
        if b[0] == 'h3':
            head = text_of(b)
        if b[0] == 'p' and text_of(b).startswith('说人话：'):
            t = text_of(b)
            body = t[len('说人话：'):].strip()
            nospace = ''.join(body.split())
            uid = b[1].get('uuid')
            print(f'  [{head[:24]}] id={uid} len={len(body)} nospace={len(nospace)}')
            print(f'      {body}')
