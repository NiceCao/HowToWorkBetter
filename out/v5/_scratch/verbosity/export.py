#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

OUT = '/home/ubuntu/projects/work-guide-book/out/v5'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))

for ch in ['39', '41', '42', '43']:
    node = IDX[ch][1]
    res = gw.call('get_document_content', {'nodeId': node, 'format': 'markdown'})
    md = res.get('markdown')
    if md is None:
        md = res.get('content') or res.get('_text') or json.dumps(res, ensure_ascii=False)
    dst = os.path.join(OUT, f'ch{ch}.md')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(md if md.endswith('\n') else md + '\n')
    print(f'ch{ch}: wrote {dst}  ({len(md)} chars)')
