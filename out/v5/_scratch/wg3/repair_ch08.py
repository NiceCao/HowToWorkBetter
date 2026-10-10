#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair ch08 heading texts corrupted by the bad renumber (regex now fixed)."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw
HERE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
NODE = IDX['08'][1]

def h3(text):
    return ["h3", {}, ["span", {"data-type": "text"}, ["span", {"data-type": "leaf"}, text]]]

def leaves(n, o):
    if isinstance(n, list):
        if len(n) >= 2 and isinstance(n[1], dict) and n[1].get('data-type') == 'leaf':
            o.append(n[2]); return o
        for c in n[1:]: leaves(c, o)
    return o
def T(b): return ''.join(leaves(b, []))

def fetch():
    for _ in range(6):
        r = gw.call('get_document_content', {'nodeId': NODE, 'format': 'jsonml'})
        if r.get('jsonml'): return json.loads(r['jsonml'])
        time.sleep(2)
    raise SystemExit('fetch failed')

# locate broken heading by a distinctive fragment, replace with correct full text
FIX = [
    ('包机票包食宿」的招聘', '6. 遇到「境外高薪、包机票包食宿」的招聘，先查中介有没有对外劳务合作经营资格'),
    ('先问清劳动合同跟谁签', '7. 面试说「正式岗」的，先问清劳动合同跟谁签、是不是劳务派遣或外包'),
    ('先算清租约回本', '8. 遇到「以租代招」，先算清租约回本要跑多少单，再决定签不签'),
    ('交会费的，不要做', '9. 兼职要你先垫钱、交会费的，不要做——刷单、点赞、日结多是冲着垫钱来的'),
    ('做什么的岗位，先问清职责', '10. 抬头好听却说不清做什么的岗位，先问清职责、带不带人、拿多少钱'),
]
for frag, correct in FIX:
    jm = fetch()
    hits = [b[1]['uuid'] for b in jm[2:] if b[0] == 'h3' and frag in T(b)]
    assert len(hits) == 1, f'{frag} -> {hits}'
    for _ in range(3):
        r = gw.call('update_document_block', {'nodeId': NODE, 'blockId': hits[0],
                                              'format': 'jsonml', 'jsonml': json.dumps(h3(correct), ensure_ascii=False)})
        if r.get('success'):
            print('fixed', hits[0], '->', correct[:34]); break
        print(' retry', r.get('errorMsg', r)); time.sleep(2)
    else:
        raise SystemExit('FAILED ' + frag)
print('done')
