#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取出新增条目（含四块）的 blockId。"""
import sys
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2, gw

TARGETS = {
 '29': ['流水线单调重复', '撑不住的时候别一个人扛'],
 '28': ['组长当众骂人'],
 '24': ['厂区的恋爱和异地分居'],
}
for ch, keys in TARGETS.items():
    node = wg2.node_of(ch)
    res = gw.call('list_document_blocks', {'nodeId': node, 'format': 'element'})
    blks = res['blocks']
    start = len(blks)
    while res.get('hasMore'):
        res = gw.call('list_document_blocks', {'nodeId': node, 'format': 'element', 'startIndex': start})
        blks.extend(res['blocks']); start = len(blks)
    print('== ch%s ==' % ch)
    for b in blks:
        el = b.get('element', {}) or {}
        for kind in ('heading', 'paragraph', 'blockquote'):
            v = el.get(kind)
            if isinstance(v, dict):
                t = v.get('text', '') or ''
                if any(k in t for k in keys):
                    print('  %-9s id=%s | %s' % (b.get('blockType'), el.get('id'), t[:46]))
                break
