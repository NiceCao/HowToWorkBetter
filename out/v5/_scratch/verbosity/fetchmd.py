#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
BASE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/verbosity'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
for ch in ['39','41','42','43']:
    node = IDX[ch][1]
    res = gw.call('get_document_content', {'nodeId': node, 'format': 'markdown'})
    md = res.get('markdown') or res.get('content') or res.get('_text') or json.dumps(res, ensure_ascii=False)
    open(os.path.join(BASE, f'live_ch{ch}.md'), 'w', encoding='utf-8').write(md)
    print(f'ch{ch}: {len(md)} chars saved')
