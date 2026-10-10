#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json
src = open('staging/59-进厂打工真实内容.md', encoding='utf-8').read()
# split on entry headers "### N. title"
parts = re.split(r'\n### (\d+)\. ', src)
# parts[0] = preamble; then pairs (num, body)
entries = {}
for i in range(1, len(parts), 2):
    num = int(parts[i]); body = parts[i+1]
    # title = first line
    lines = body.split('\n')
    title = lines[0].strip()
    # label lines: find "> 性价比："
    m = re.search(r'> 性价比：(.+?)\n> 成本：(.+?)\n> 口径：(.+?)\n> 证据等级：(\S+)', body)
    labels = None
    if m:
        labels = {'性价比': m.group(1).strip(), '成本': m.group(2).strip(),
                  '口径': m.group(3).strip(), '证据等级': m.group(4).strip()}
    def block(name, nxt):
        pat = r'\*\*'+re.escape(name)+r'：\*\* (.*?)(?=\n\n\*\*'+re.escape(nxt)+r'|\Z)'
        mm = re.search(pat, body, re.S)
        return mm.group(1).strip() if mm else None
    say = block('说人话', '为什么 / 怎么做')
    why = block('为什么 / 怎么做', '来源')
    lim = block('限制与争议', '\Z')
    # sources: between **来源：** and **限制与争议：**
    ms = re.search(r'\*\*来源：\*\*\n(.*?)(?=\n\*\*限制与争议：\*\*)', body, re.S)
    srcs = []
    if ms:
        for ln in ms.group(1).split('\n'):
            ln = ln.strip()
            if ln.startswith('- '):
                srcs.append(ln[2:].strip())
    entries[num] = {'title': title, 'labels': labels, 'say': say, 'why': why,
                    'sources': srcs, 'limit': lim}
json.dump(entries, open('out/v5/_scratch/wg3/draft.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k in sorted(entries):
    e = entries[k]
    print('='*70)
    print(f"ENTRY {k}: {e['title']}")
    print('LABELS:', e['labels'])
    print('SAY:', (e['say'] or '')[:60], '... len', len(e['say'] or ''))
    print('WHY:', (e['why'] or '')[:60], '... len', len(e['why'] or ''))
    print('SOURCES:', len(e['sources']))
    for s in e['sources']: print('   -', s[:70])
    print('LIMIT:', (e['limit'] or '')[:60], '... len', len(e['limit'] or ''))
