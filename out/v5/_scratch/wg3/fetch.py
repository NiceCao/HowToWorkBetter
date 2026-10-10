#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'
for ch in ('08','35','39','43'):
    node = IDX[ch][1]
    jm = None
    for _ in range(5):
        r = gw.call('get_document_content', {'nodeId': node, 'format': 'jsonml'})
        if r.get('jsonml'):
            jm = json.loads(r['jsonml']); break
        time.sleep(2)
    assert jm is not None, ch
    json.dump(jm, open(f'{OUT}/jm_ch{ch}.json','w',encoding='utf-8'), ensure_ascii=False)
    print(f'ch{ch} jsonml top len {len(jm)}; blocks {len(jm)-2}')
