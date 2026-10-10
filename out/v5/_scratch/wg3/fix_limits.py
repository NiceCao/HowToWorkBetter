#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair the 6 inserted entries' 限制与争议 blocks: strip the trailing '---'
(and the 合并说明 blockquote) that the draft parser wrongly captured."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
HERE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
DRAFT = json.load(open(f'{HERE}/draft.json', encoding='utf-8'))

def clean_limit(s):
    # real limit is everything up to the first blank-line '---' separator
    return s.split('\n\n---')[0].strip()

def bold_para(label, text):
    return ["p", {}, ["span", {"data-type": "text"},
            ["span", {"bold": True, "data-type": "leaf"}, label],
            ["span", {"data-type": "leaf"}, text]]]

def fetch(ch):
    for _ in range(6):
        r = gw.call('get_document_content', {'nodeId': IDX[ch][1], 'format': 'jsonml'})
        if r.get('jsonml'): return json.loads(r['jsonml'])
        time.sleep(2)
    raise SystemExit('fetch fail')

def leaves(n, o):
    if isinstance(n, list):
        if len(n) >= 2 and isinstance(n[1], dict) and n[1].get('data-type') == 'leaf':
            o.append(n[2]); return o
        for c in n[1:]: leaves(c, o)
    return o
def T(b): return ''.join(leaves(b, []))

JOBS = {'35': [5, 6], '39': [8, 7], '43': [4], '08': [10]}
for ch, dns in JOBS.items():
    for dn in dns:
        real = clean_limit(DRAFT[str(dn)]['limit'])
        frag = real[:24]
        jm = fetch(ch)
        hits = [b[1]['uuid'] for b in jm[2:] if b[0] == 'p' and T(b).startswith('限制与争议：') and frag in T(b)]
        assert len(hits) == 1, f'ch{ch} draft{dn} -> {hits}'
        new = bold_para('限制与争议：', ' ' + real)
        for _ in range(3):
            r = gw.call('update_document_block', {'nodeId': IDX[ch][1], 'blockId': hits[0],
                                                  'format': 'jsonml', 'jsonml': json.dumps(new, ensure_ascii=False)})
            if r.get('success'):
                print(f'ch{ch} draft{dn} 限制 fixed ({hits[0]}) len={len(real)}'); break
            print('  retry', r.get('errorMsg', r)); time.sleep(2)
        else:
            raise SystemExit(f'FAILED ch{ch} draft{dn}')
print('done')
