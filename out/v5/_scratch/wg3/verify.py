#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify ch08/35/39/43 after merge + export live markdown to out/v5/chNN.md."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
HERE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'
DST = '/home/ubuntu/projects/work-guide-book/out/v5'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
DRAFT = json.load(open(f'{HERE}/draft.json', encoding='utf-8'))
NODES = {'08': IDX['08'][1], '35': IDX['35'][1], '39': IDX['39'][1], '43': IDX['43'][1]}
# new item -> (chapter, item number, draft number)
NEW = {'35': [(6, 5), (10, 6)], '39': [(6, 8), (10, 7)], '43': [(5, 4)], '08': [(5, 10)]}
IMPORT = {'35': {'draft5': ('想跟老师傅学到东西', 6), 'draft6': ('想换好岗位', 10)},
          '39': {'draft8': ('久站久坐', 6), 'draft7': ('上夜班', 10)},
          '43': {'draft4': ('乱罚款', 5)}, '08': {'draft10': ('老乡、工头拉你', 5)}}

def fetch(ch, fmt):
    for _ in range(6):
        r = gw.call('get_document_content', {'nodeId': NODES[ch], 'format': fmt})
        if r.get(fmt): return r[fmt]
        time.sleep(2)
    raise SystemExit(f'{ch} {fmt} fail')

def leaves(n, o):
    if isinstance(n, list):
        if len(n) >= 2 and isinstance(n[1], dict) and n[1].get('data-type') == 'leaf':
            o.append(n[2]); return o
        for c in n[1:]: leaves(c, o)
    return o
def T(b): return ''.join(leaves(b, []))
def is_quote(b): return isinstance(b[1], dict) and b[1].get('blockquote')

ok_all = True
for ch in ('08', '35', '39', '43'):
    jm = json.loads(fetch(ch, 'jsonml'))
    blocks = jm[2:]
    # split into entries by h3
    heads = [i for i, b in enumerate(blocks) if b[0] == 'h3']
    nums = []
    for i in heads:
        t = T(blocks[i])
        m = t.split('.', 1)[0]
        nums.append(int(m) if m.isdigit() else None)
    # continuity
    cont = nums == list(range(1, len(nums) + 1))
    print(f'\n===== ch{ch}: {len(heads)} 条 ===== 编号: {nums if len(nums)<=13 else str(nums)}  连续:{cont}')
    if not cont: ok_all = False
    # per entry 4-block check
    bad = []
    for k, i in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(blocks)
        seg = blocks[i:end]
        texts = [T(b) for b in seg]
        has = {'meta': any(is_quote(b) and '性价比：' in T(b) for b in seg),
               '说人话': any(t.startswith('说人话：') for t in texts),
               '为什么': any(t.startswith('为什么 / 怎么做：') for t in texts),
               '来源': any(t.startswith('来源：') for t in texts),
               '限制': any(t.startswith('限制与争议：') for t in texts)}
        miss = [k2 for k2, v in has.items() if not v]
        if miss: bad.append((nums[k], miss))
    print('  四块缺失:', bad if bad else '无')
    if bad: ok_all = False
    # new items exact text
    for num, dn in NEW[ch]:
        e = DRAFT[str(dn)]
        real_limit = e['limit'].split('\n\n---')[0].strip()
        i = heads[num - 1]
        end = heads[num] if num < len(heads) else len(blocks)
        seg = blocks[i:end]
        texts = [T(b) for b in seg]
        chk = {
            '标题': T(seg[0]) == f"{num}. {e['title']}",
            '说人话': any(t == '说人话： ' + e['say'] for t in texts),
            '为什么': any(t == '为什么 / 怎么做： ' + e['why'] for t in texts),
            '来源n': sum(1 for t in texts if t in e['sources']) == len(e['sources']),
            '限制': any(t == '限制与争议： ' + real_limit for t in texts),
            '无残留---': not any(t.strip().endswith('---') for t in texts),
            '无合并说明': not any('合并说明' in t for t in texts),
        }
        miss = [k2 for k2, v in chk.items() if not v]
        print(f"  新增第{num}条(draft{dn}) {e['title'][:18]}... -> {'OK' if not miss else 'FAIL '+str(miss)}")
        if miss: ok_all = False
print('\n>>> ALL CHECKS OK' if ok_all else '\n>>> SOME CHECKS FAILED')

# bold count (labels preserved) for new items
for ch in ('08', '35', '39', '43'):
    jm = json.loads(fetch(ch, 'jsonml'))
    blocks = jm[2:]
    nb = 0
    for b in blocks:
        if b[0] == 'p' and len(b) > 2 and isinstance(b[2], list):
            for sp in b[2][1:]:
                if isinstance(sp, list) and len(sp) >= 2 and isinstance(sp[1], dict) and sp[1].get('bold'):
                    nb += 1
    print(f'ch{ch} 加粗标签数: {nb}')

# export markdown
for ch in ('08', '35', '39', '43'):
    md = fetch(ch, 'markdown')
    p = f'{DST}/ch{ch}.md'
    open(p, 'w', encoding='utf-8').write(md)
    print(f'exported ch{ch} -> {p} ({len(md)} chars)')
