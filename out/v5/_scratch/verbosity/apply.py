#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 4 章里 7 个超长「说人话」压到 ≤120 字；砍掉的细节移到同条「为什么/怎么做」。
就地改只用 update_document_block(jsonml)，保留「说人话：」加粗。
用法：python3 apply.py [--dry]
"""
import json, os, sys, copy, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

BASE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/verbosity'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))

# ---- 7 个「说人话」新正文（不含「说人话：」标签，含前导空格 1 个）----
NEW = {
 '39': {17: " 长时间伏案的人，颈肩和腰的不适多半来自连续几个小时不动，不花钱的办法就是把久坐拆成一段一段、每隔一会儿换个姿势。出现手麻、腿疼、走路发飘这类表现的，先去正规医院检查，别当成习惯问题拖着。"},
 '41': {92: " 加班费标准跟工时制度挂钩：标准工时下，延时、休息日、法定节假日工作的报酬标准不同，企业实行别的工时办法要经劳动行政部门批准。请假、调休、加班先跟直属领导说，再用文字确认时间和交接。"},
 '42': {
   6:  " 签谁的名字，谁就对这份文件负责，替人签出了问题先找签字的你。签之前只问两件事：写的是不是自己的名字、自己有没有得到授权；不是自己的名字一律不签。",
   35: " 法律上的商业秘密要同时满足三点：不为公众所知悉、能带来经济利益、公司采取了保密措施；客户名单、报价体系、技术方案、源代码、未公开的经营计划都算。离职时资料不删不拷，对外发文件前先过涉密、客户名单、竞业限制这三道红线。",
   74: " 商业贿赂是用不正当利益换取交易机会或竞争优势，反不正当竞争法2025年修订后，送的和收的都在追责范围内。给客户或上下级送礼前先过三道线：不送可能影响对方公正办事的财物，不送现金、购物卡、有价证券，不送贵重到让人为难的东西。",
 },
 '43': {
   6:  " 被公司侵犯权益，先分清是哪一类事、再找对部门，能少跑冤枉路。欠薪、违法辞退、不给加班费、没签劳动合同属于劳动争议，可以向劳动争议仲裁委员会申请仲裁、不收费；社会保险和住房公积金不在仲裁受理范围内，要单独走行政投诉。",
   21: " 劳动纠纷里能拿回多少，很大程度上取决于你手里有多少能对得上的证据，不少人道理站得住，却因为拿不出记录而吃亏。证据从入职起就按劳动关系、工资报酬、工作内容、公司违法四类攒；微信、钉钉、邮件算电子数据，要留原件，别只留截图。",
 },
}

# ch42 条目8 的「为什么/怎么做」(idx 75) 前插一句，承接从说人话移出的细节
CH42_WHY_PREPEND = (" 反不正当竞争法第八条把交易相对方的工作人员、受委托办理相关事务的单位或者个人，"
                    "以及利用职权或者影响力影响交易的单位或者个人，都列为不得贿赂的对象。")

BLOCKID = {  # 从原始回包整串复制
 ('39',17):'mv15wtrcgk0b6jjd0ep',
 ('41',92):'mv167cb123gjfcmo1f8',
 ('42',6):'mv163hnzlwygumy0339',
 ('42',35):'mv162m648k2e5swnk5m',
 ('42',74):'mv1628645ylbaaq2v55',
 ('43',6):'mv165ooczsp4adbdn7q',
 ('43',21):'mv165djj2x16zqf9fy7',
}
WHY42_ID = 'mv162865zeko41fcvrs'  # ch42 idx75


def find_leaves(node, out=None):
    if out is None: out = []
    if isinstance(node, list):
        if (len(node) >= 3 and node[0] == 'span' and isinstance(node[1], dict)
                and node[1].get('data-type') == 'leaf' and isinstance(node[-1], str)):
            out.append(node); return out
        for c in node[1:]:
            find_leaves(c, out)
    return out


def content_leaf(jm):
    lvs = find_leaves(jm)
    nonbold = [l for l in lvs if not l[1].get('bold')]
    assert len(nonbold) == 1, f'expected 1 nonbold leaf, got {len(nonbold)}'
    return nonbold[0]


def fetch_blocks(node):
    res = gw.call('list_document_blocks', {'nodeId': node, 'startIndex': 0, 'endIndex': 1000, 'format': 'jsonml'})
    return {b['index']: b for b in res['blocks']}


def main():
    dry = '--dry' in sys.argv
    vers = {}
    for ch in ['39', '41', '42', '43']:
        node = IDX[ch][1]
        print(f'\n===== ch{ch} (node {node}) =====')
        blocks = fetch_blocks(node)
        if not dry:
            sv = gw.call('save_doc_version', {'nodeId': node})
            vers[ch] = sv
            print(f'  save_doc_version -> {json.dumps(sv, ensure_ascii=False)}')
        for idx, newtext in sorted(NEW[ch].items()):
            b = blocks[idx]
            exp = BLOCKID[(ch, idx)]
            assert b['blockId'] == exp, f'ch{ch} idx{idx} id {b["blockId"]} != {exp}'
            jm = copy.deepcopy(json.loads(b['jsonml']))
            lf = content_leaf(jm)
            old = lf[-1]
            old_len = len(old) - (1 if old.startswith(' ') else 0)
            new_len = len(newtext) - (1 if newtext.startswith(' ') else 0)
            assert new_len <= 120, f'ch{ch} idx{idx} new_len={new_len} > 120'
            print(f'  idx{idx} {b["blockId"]}: {old_len} -> {new_len} 字')
            if not dry:
                lf[-1] = newtext
                r = gw.call('update_document_block', {'nodeId': node, 'blockId': b['blockId'],
                                                      'format': 'jsonml', 'jsonml': json.dumps(jm, ensure_ascii=False)})
                assert r.get('success'), f'ch{ch} idx{idx} update failed: {r}'
        # ch42 条目8 的为什么前插
        if ch == '42' and not dry:
            b = fetch_blocks(node)[75]
            # index may shift? in-place edit doesn't shift indices; re-fetch to be safe
        if ch == '42' and not dry:
            node2 = IDX['42'][1]
            blocks2 = fetch_blocks(node2)
            b = blocks2[75]
            assert b['blockId'] == WHY42_ID, f'ch42 why id {b["blockId"]} != {WHY42_ID}'
            jm = copy.deepcopy(json.loads(b['jsonml']))
            lf = content_leaf(jm)
            if CH42_WHY_PREPEND not in lf[-1]:
                lf[-1] = CH42_WHY_PREPEND + lf[-1].lstrip(' ')
                r = gw.call('update_document_block', {'nodeId': node2, 'blockId': b['blockId'],
                                                      'format': 'jsonml', 'jsonml': json.dumps(jm, ensure_ascii=False)})
                print(f'  ch42 idx75 为什么前插 -> success={r.get("success")}')
    if not dry:
        json.dump(vers, open(os.path.join(BASE, 'versions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nDRY' if dry else '\nAPPLIED')


if __name__ == '__main__':
    main()
