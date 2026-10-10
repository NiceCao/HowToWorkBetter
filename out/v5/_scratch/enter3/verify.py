#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回读验证 ch24/28/29 并导出 markdown 到 out/v5/chNN.md。"""
import json, re, sys, os
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2, gw

OUTDIR = '/home/ubuntu/projects/work-guide-book/out/v5'
EXPECT_N = {'29': 10, '28': 9, '24': 9}

for ch in ['29', '28', '24']:
    node = wg2.node_of(ch)
    res = gw.call('list_document_blocks', {'nodeId': node, 'format': 'element'})
    blks = res['blocks']
    start = len(blks)
    while res.get('hasMore'):
        res = gw.call('list_document_blocks', {'nodeId': node, 'format': 'element', 'startIndex': start})
        blks.extend(res['blocks'])
        start = len(blks)
    print('\n===== ch%s  blocks=%d =====' % (ch, len(blks)))

    nums = []
    for b in blks:
        el = b.get('element', {})
        if b.get('blockType') == 'heading':
            h = el.get('heading', {})
            if h.get('level') == 3:
                t = h.get('text', '')
                m = re.match(r'^(\d+)\.\s', t)
                if m:
                    nums.append((int(m.group(1)), t[:34]))
    print('条目编号:', [n for n, _ in nums])
    ok = [n for n, _ in nums] == list(range(1, EXPECT_N[ch] + 1))
    print('编号 1..%d 连续: %s' % (EXPECT_N[ch], ok))
    for n, t in nums:
        print('   %2d  %s' % (n, t))

    md = gw.call('get_document_content', {'nodeId': node, 'format': 'markdown'}).get('markdown', '')
    outp = os.path.join(OUTDIR, 'ch%s.md' % ch)
    open(outp, 'w', encoding='utf-8').write(md)
    print('导出 %s  %d bytes' % (outp, len(md.encode())))
    print('四块计数: 说人话=%d 来源=%d 限制与争议=%d 为什么=%d 加粗说人话=%d 加粗来源=%d' % (
        md.count('说人话：'), md.count('来源：'), md.count('限制与争议：'), md.count('为什么'),
        md.count('**说人话：**'), md.count('**来源：**')))
