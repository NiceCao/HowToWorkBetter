#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
r = gw.call('list_document_blocks', {'nodeId': IDX['35'][1]})
for blk in r['blocks'][:4]:
    print(json.dumps(blk, ensure_ascii=False))
    print('---')
print('KEYS:', list(r.keys()))
