#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify ch11 after merge + export markdown to out/v5/ch11.md."""
import json, sys, re
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2, gw

CH = '11'
NODE = wg2.node_of(CH)

# ---- blocks ----
res = gw.call('list_document_blocks', {'nodeId': NODE, 'format': 'element'})
blocks = res['blocks']
print('totalCount =', res.get('totalCount'), 'len =', len(blocks))

# rebuild full list (paged?) — if hasMore, page through
start = len(blocks)
while res.get('hasMore'):
    res = gw.call('list_document_blocks', {'nodeId': NODE, 'format': 'element', 'startIndex': start})
    blocks.extend(res['blocks'])
    start = len(blocks)
print('blocks after paging =', len(blocks))

headings = [b for b in blocks if b.get('blockType') == 'heading']
print('\n--- headings ---')
nums = []
for b in headings:
    el = b['element']
    h = el.get('heading', {})
    lvl = h.get('level'); txt = h.get('text', '')
    print('  idx=%s %s | %s | id=%s' % (b.get('index'), lvl, txt[:60], el.get('id')))
    m = re.match(r'^(\d+)\.\s', txt)
    if m:
        nums.append(int(m.group(1)))

print('\nentry numbers found =', nums)
print('continuous 1..11 ? ', nums == list(range(1, 12)))

# ---- empty blocks ----
empty = []
for b in blocks:
    el = b['element']
    bt = b.get('blockType')
    txt = ''
    if 'paragraph' in el: txt = el['paragraph'].get('text', '')
    elif 'blockquote' in el: txt = el['blockquote'].get('text', '')
    elif 'heading' in el: txt = el['heading'].get('text', '')
    if bt == 'paragraph' and (txt is None or txt.strip() == ''):
        empty.append(b.get('index'))
print('empty paragraph blocks =', empty)

# ---- four blocks per entry (via markdown) ----
md = gw.call('get_document_content', {'nodeId': NODE, 'format': 'markdown'}).get('markdown', '')
print('\nmarkdown chars =', len(md))
for key in ['说人话：', '来源：', '限制与争议：']:
    print('  count %s = %d' % (key, md.count(key)))
print('  count 为什么 =', md.count('为什么'))

import os
outp = '/home/ubuntu/projects/work-guide-book/out/v5/ch11.md'
open(outp, 'w', encoding='utf-8').write(md)
print('wrote', outp, os.path.getsize(outp), 'bytes')
print('\n--- markdown tail ---')
print(md[-600:])
