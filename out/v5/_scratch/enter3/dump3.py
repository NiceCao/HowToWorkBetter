#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

jm = wg2.fetch_jm('24')
blocks = wg2.blocks_of(jm)
for i in range(52, 56):
    print(i, json.dumps(blocks[i], ensure_ascii=False)[:260])
