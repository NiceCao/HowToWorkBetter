#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe ch24/28/29 jsonml structure before editing."""
import json, sys, re
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

for CH in ['24', '28', '29']:
    jm = wg2.fetch_jm(CH)
    blocks = wg2.blocks_of(jm)
    print('\n===== ch%s  nblocks=%d  node=%s =====' % (CH, len(blocks), wg2.node_of(CH)))
    for i, b in enumerate(blocks):
        tag = b[0]
        u = wg2.uid(b)
        t = wg2.text_of(b)
        attrs = {k: v for k, v in b[1].items() if k in ('blockquote',)}
        # heading level
        lv = ''
        if tag == 'h1': lv = 'H1'
        elif tag == 'h2': lv = 'H2'
        elif tag == 'h3': lv = 'H3'
        print('%3d %-4s %-6s u=%-22s | %s' % (i, tag, lv, str(u), t[:70]))
