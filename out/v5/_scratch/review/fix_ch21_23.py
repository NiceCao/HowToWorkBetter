#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch21: remove 7 redundant hr blocks; ch21 & ch23: restore bold 本章小结： label."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

NODE = {'21': 'mExel2BLV5y5A0rBcp0n753pVgk9rpMq', '23': 'gwva2dxOW4y567RecYGMLqglVbkz3BRL'}
REV = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/review'

# ch21 redundant hr blockIds (second of each adjacent pair)
CH21_EXTRA_HR = ['mv0pspmrp5iiaclaner', 'mv0pspnbloj6k7pz56', 'mv0pspo2og9d87odfcr',
                 'mv0psqcd3j5ft3rqmt3', 'mv0psqej8dipnfghy5k', 'mv0psqh2v6x3kkzulj',
                 'mv0psqjnibodk0j0jg']
# summary block uuids
SUMMARY = {'21': 'mv0uc9q34q4liw39mns', '23': 'mv0uh4c9erpglbkt8i4'}

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

def find(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None

MODE = sys.argv[1] if len(sys.argv) > 1 else 'dry'

for ch in ['21', '23']:
    jm = json.load(open(f'{REV}/jm_after_ch{ch}.json', encoding='utf-8'))
    blocks = jm[2:]
    if MODE == 'apply':
        r = gw.call('save_doc_version', {'nodeId': NODE[ch]})
        print(f'ch{ch} save_doc_version ->', r.get('success'))
    # ---- summary label restore ----
    uid = SUMMARY[ch]
    b = find(blocks, uid)
    assert b is not None, f'{ch} summary {uid} not found'
    assert b[0] == 'p' and b[1].get('blockquote') is True, f'{ch} summary not blockquote: {json.dumps(b)[:120]}'
    full = text_of(b)
    assert not full.startswith('本章小结'), f'{ch} already has label'
    assert json.dumps(b, ensure_ascii=False).count('leaf') == 1, f'{ch} summary not single leaf: {full[:30]}'
    if MODE == 'dry':
        print(f'ch{ch} SUMMARY {uid} rest={full[:40]!r} len={len(full)}')
    else:
        newb = ['p', {'blockquote': True, 'uuid': uid}, ['span', {'data-type': 'text'},
                ['span', {'bold': True, 'data-type': 'leaf'}, '本章小结：'],
                ['span', {'data-type': 'leaf'}, ' ' + full]]]
        r = gw.call('update_document_block', {'nodeId': NODE[ch], 'blockId': uid,
                                              'format': 'jsonml', 'jsonml': json.dumps(newb, ensure_ascii=False)})
        print(f'ch{ch} summary update {uid} ->', r.get('success'))
        time.sleep(0.4)
    # ---- ch21 hr cleanup ----
    if ch == '21':
        # verify all extras are hr and are second-of-pair
        hr_idx = {b[1]['uuid']: i for i, b in enumerate(blocks) if isinstance(b, list) and b[0] == 'hr' and isinstance(b[1], dict) and b[1].get('uuid')}
        for u in CH21_EXTRA_HR:
            assert u in hr_idx, f'{ch} {u} not an hr block'
            assert (hr_idx[u] - 1) in [v for v in hr_idx.values()], f'{ch} {u} not second of pair'
        if MODE == 'dry':
            print(f'ch{ch} would delete {len(CH21_EXTRA_HR)} hr blocks; total hr before={len(hr_idx)}')
        else:
            r = gw.call('delete_document_block', {'nodeId': NODE[ch], 'blockId': ','.join(CH21_EXTRA_HR)})
            print(f'ch{ch} delete {len(CH21_EXTRA_HR)} hr ->', r.get('success'), r.get('notFoundBlockIds'))
            time.sleep(0.4)
