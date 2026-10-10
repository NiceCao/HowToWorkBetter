#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
OUT='/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'
ch=sys.argv[1]
lo=int(sys.argv[2]); hi=int(sys.argv[3])
jm=json.load(open(f'{OUT}/jm_ch{ch}.json',encoding='utf-8'))
for i,b in enumerate(jm[2:]):
    if lo<=i<=hi:
        print(i, json.dumps(b,ensure_ascii=False))
