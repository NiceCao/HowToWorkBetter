#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore bold on the 说人话 / 限制与争议 labels of 14 blocks in ch13 & ch43."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

NODE = {'13': 'ZX6GRezwJly9M4eqc0m0nG6P8dqbropQ', '43': 'o14dA3GK8gze4AlxSEbEDbAGJ9ekBD76'}
REV = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/review'

# blockId(uuid) -> label
TARGETS = {
 '13': [
   ('mv14jdm2vtpepxbc83', '说人话：'),
   ('mv14jdm9nxyqnd2aqjo', '限制与争议：'),
   ('mv14ifmvmjg4aabffr', '说人话：'),
   ('mv14ifmyjvcvn6agluo', '限制与争议：'),
   ('mv14i9rsfds5ya0ok2a', '说人话：'),
   ('mv14i9rvzu1k7rs3wsf', '限制与争议：'),
 ],
 '43': [
   ('mv165ooczsp4adbdn7q', '说人话：'),
   ('mv165oodj61zc02nsw', '限制与争议：'),
   ('mv165djj2x16zqf9fy7', '说人话：'),
   ('mv165djkowjqf36p1j', '限制与争议：'),
   ('mv164pxgur302agenho', '说人话：'),
   ('mv164pxlzbwnu9enug', '限制与争议：'),
   ('mv163wanqn2622vrf5n', '说人话：'),
   ('mv163war3klzevuyk3d', '限制与争议：'),
 ],
}

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

def find_block(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None

MODE = sys.argv[1] if len(sys.argv) > 1 else 'dry'

for ch, items in TARGETS.items():
    jm = json.load(open(f'{REV}/jm_ch{ch}.json', encoding='utf-8'))
    blocks = jm[2:]
    if MODE == 'apply':
        r = gw.call('save_doc_version', {'nodeId': NODE[ch]})
        print(f'ch{ch} save_doc_version ->', r.get('success'), r.get('versionId') or r.get('docVersion') or '')
    for uid, label in items:
        b = find_block(blocks, uid)
        assert b is not None, f'{ch} {uid} not found'
        full = text_of(b)
        assert full.startswith(label), f'{ch} {uid} does not start with {label}: {full[:20]}'
        rest = full[len(label):]
        # sanity: block must currently be a single non-bold leaf
        heavy = json.dumps(b, ensure_ascii=False)
        assert '"bold": true' not in heavy, f'{ch} {uid} already has bold?!'
        if MODE == 'dry':
            print(f'ch{ch} {uid}')
            print(f'   label={label!r} rest={rest[:70]!r}  (rest len {len(rest)})')
        else:
            newb = ['p', {'uuid': uid}, ['span', {'data-type': 'text'},
                    ['span', {'bold': True, 'data-type': 'leaf'}, label],
                    ['span', {'data-type': 'leaf'}, rest]]]
            r = gw.call('update_document_block', {'nodeId': NODE[ch], 'blockId': uid,
                                                  'format': 'jsonml', 'jsonml': json.dumps(newb, ensure_ascii=False)})
            print(f'ch{ch} update {uid} ->', r.get('success'), r.get('logId', ''))
            time.sleep(0.4)
