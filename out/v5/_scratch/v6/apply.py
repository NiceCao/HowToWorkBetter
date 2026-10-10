#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compress the 9 oversized 说人话 blocks (ch08/10/13/21/22) to <=120 chars,
moving cut details into the same entry's 为什么/怎么做 bullets."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

NODES = {
 '08': 'vy20BglGWOMng5j4IvLne0BLJA7depqY',
 '10': 'YMyQA2dXW7r5AyYBs1x1AEk38zlwrZgb',
 '13': 'ZX6GRezwJly9M4eqc0m0nG6P8dqbropQ',
 '21': 'mExel2BLV5y5A0rBcp0n753pVgk9rpMq',
 '22': 'Qnp9zOoBVBe3A9EBced3RKN5W1DK0g6l',
}
OUT = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/v6'

# blockId -> (new 说人话 body, expected old non-space count)
SAY = {
 'mv14az4uxm38v0jo78': ("正规公司招人，是公司给你发钱，不该由你交钱。入职前要押金、服装费、资料费、培训费，或让你花钱买「内推名额」「保录取」的，一律拒绝。真从工资里扣损失赔偿，每月不超过当月工资 20%，到手不能低于当地最低工资。", 170),
 'mv14alzkzm6wu78j0e': ("招聘说「正式员工」，合同却可能跟劳务派遣公司或外包公司签，工资、社保、晋升都隔着一层。面试先问清「劳动合同跟谁签」，就能分辨，再决定签不签。", 159),
 'mv14cxmtsaz0akcq1gb': ("社保缴费基数按本人上年度月平均工资确定，奖金、津贴等工资性收入都要计入。单位按最低基数缴属于未足额缴纳，可以要求补缴；当月到手可能多一点，但未来的养老金、公积金和医保个人账户都会少一截。", 194),
 'mv14cpxjm94ur485m7': ("公积金不止买房能用：支付房租、购房、还房贷、装修、交物业费，以及离退休、丧失劳动能力并终止劳动关系、出境定居等情形都能提取。账户里的钱利率不高，短期内不买房，符合条件就取出来用。", 156),
 'mv14cief73wpdokosfw': ("住房公积金是单位和个人按同一比例各缴一笔、都归你个人所有的住房储金，可用来买房、租房、还贷。缴存比例不低于本人上年度月平均工资的 5%，基数越高、进账户的钱越多，单位就等额多配一笔。", 178),
 'mv14cevewqz9cz038xc': ("换城市工作，养老和医疗保险的缴费年限要办转移接续、累计到一起，公积金也一样。不转钱不会消失，但分散在多地会影响退休时在哪领、按什么标准算。在国家社会保险公共服务平台或「掌上 12333」线上提交即可。", 199),
 'mv14i9rsfds5ya0ok2a': ("事实清楚、证据齐全、金额不大的案子，自己申请仲裁就行，打 12348 还能免费咨询；涉及股权激励、竞业限制、商业秘密或金额较大的，再找专业律师。仲裁不收费，律师费一般自己出，经济困难的还能申请免费法律援助。", 121),
 'mv152cbiqtbamzd1wq': ("钉钉、微信、邮件是日常沟通的主渠道，写法直接影响对方要不要回、多快回。一条消息做到三点：一件事一条、分点排版、写清要对方做什么和什么时候要；@ 只圈要动手的人，别 @ 全员；能用文字就别发长语音。", 123),
 'mv151nxxvr3b8rmj36o': ("线上会省了路上时间，也带来新问题：设备出状况、注意力分散、冷场。会前测好麦克风、摄像头和网络，明确主持人和议程；会上到点就开、能开摄像头就开、进会先静音；共享前关掉聊天窗口和私密文件；迟到先道歉，早退提前说一声。", 129),
}

# blockId -> text appended verbatim to the block's leaf
APPEND = {
 'mv14az4wlqfjk1swmtr': "用人单位以担保等名义收取财物的，责令限期退还，并按每人 500 元以上 2000 元以下罚款。",
 'mv14alzlnuyp4vzt6he': "派遣用工只能用在临时性、辅助性、替代性岗位，数量不超过用工总量的 10%；派遣工与正式工干一样的活应同工同酬（《劳动合同法》第六十三条）；小时工按小时算钱，多属非全日制。",
 'mv14cxmvuqofnnq51v': "只要建立劳动关系，单位就有缴纳义务，派遣工由派遣公司缴，跨地区派遣的在用工单位所在地、按当地标准参保。",
 'mv14cpxlgk9odu6gj7': "租房提取多数城市要求连续足额缴存满 3 个月、本人及配偶在当地无自有住房，在公积金小程序或 App 线上申请，很多城市免交租房合同和发票。",
 'mv14ciehtvsyi0yk9rj': "查余额和缴存明细，用微信或支付宝的「全国住房公积金」小程序，也可走当地公积金中心官网、App 或 12329 热线。",
 'mv14cevgpuuhccjdthi': "公积金到新城市开立正常缴存账户后，用「全国住房公积金」小程序或全国平台提交转移接续，原地的余额和缴存记录会转到新账户、合并累计。",
 'mv14i9rt0tnmc82qwql': "；只主张经济补偿或赔偿金",
 'mv152cbjq7unlgnq9em': "能用文字就别发长语音，语音不能搜、不能扫，对方在会议或嘈杂处只能等以后再听；@ 只圈要动手的人，别 @ 全员。",
 'mv1mx3yzw46qltycqva': "会前测好麦克风、摄像头和网络，重要的会提前十分钟进，明确主持人和议程；会上到点就开，能开摄像头就开。",
}

def nz(s):
    return len(''.join(s.split()))

def leaves_nodes(b, out):
    if isinstance(b, list):
        if len(b) >= 2 and isinstance(b[1], dict) and b[1].get('data-type') == 'leaf':
            out.append(b)
            return out
        for c in b[1:]:
            leaves_nodes(c, out)
    return out

def text_of(b):
    return ''.join((n[2] if len(n) >= 3 and isinstance(n[2], str) else '') for n in leaves_nodes(b, []))

def find(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None

def set_say(b, new_text):
    ln = leaves_nodes(b, [])
    bold = [n for n in ln if n[1].get('bold')]
    body = [n for n in ln if not n[1].get('bold')]
    assert len(bold) == 1 and len(body) == 1, f'layout unexpected: {ln}'
    assert text_of(bold[0]) == '说人话：', f'label changed: {text_of(bold[0])!r}'
    old = body[0][2]
    lead = old[:len(old) - len(old.lstrip())]
    body[0][2] = lead + new_text
    return b

def append_leaf(b, extra):
    ln = leaves_nodes(b, [])
    ln[-1][2] = ln[-1][2] + extra
    return b

mode = sys.argv[1] if len(sys.argv) > 1 else 'dry'

# --- verify against list_document_blocks ---
for ch, node in NODES.items():
    r = gw.call('list_document_blocks', {'nodeId': node})
    assert r.get('success'), f'ch{ch} list failed'
    live_ids = {}
    for blk in r['blocks']:
        el = blk.get('element', {})
        bid = el.get('id')
        if not bid:
            continue
        txt = ''
        for k in ('paragraph', 'heading', 'blockquote', 'unorderedList', 'orderedList'):
            v = el.get(k)
            if isinstance(v, dict):
                txt = v.get('text', '')
                break
        live_ids[bid] = txt
    json.dump(live_ids, open(f'{OUT}/liveids_ch{ch}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    mint = sum(1 for i in SAY if i in live_ids)
    print(f'ch{ch} list_document_blocks ok: {len(live_ids)} blocks, {mint} say-ids present')

# --- dry run checks ---
print('\n=== dry run: new 说人话 counts ===')
bad = []
for uid, (new, oldn) in SAY.items():
    c = nz(new)
    flag = 'OK' if c <= 120 else 'TOO LONG'
    if c > 120:
        bad.append(uid)
    print(f'  {uid}  {oldn} -> {c}  {flag}')
    if not new.strip():
        bad.append(uid)
print('APPEND blocks:', len(APPEND), 'total', len(SAY), 'rewrites')
if bad:
    print('!! abort, over-limit:', bad)
    sys.exit(1)

if mode != 'apply':
    print('\ndry run only. pass "apply" to write.')
    sys.exit(0)

# --- apply per chapter ---
CH_OF = {}
for ch in NODES:
    jm = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))
    for b in jm[2:]:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') in SAY:
            CH_OF[b[1]['uuid']] = ch
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') in APPEND:
            CH_OF[b[1]['uuid']] = ch

for ch, node in NODES.items():
    ids = [u for u in list(SAY) + list(APPEND) if CH_OF.get(u) == ch]
    if not ids:
        continue
    v = gw.call('save_doc_version', {'nodeId': node})
    print(f'\nch{ch} save_doc_version -> {v.get("success")} {json.dumps({k: v[k] for k in v if k not in ("logId",)}, ensure_ascii=False)[:200]}')
    jm = json.load(open(f'{OUT}/jm_ch{ch}.json', encoding='utf-8'))
    blocks = jm[2:]
    for uid in ids:
        b = find(blocks, uid)
        assert b is not None, uid
        if uid in SAY:
            set_say(b, SAY[uid][0])
        else:
            append_leaf(b, APPEND[uid])
        j = json.dumps(b, ensure_ascii=False)
        r = gw.call('update_document_block', {'nodeId': node, 'blockId': uid, 'format': 'jsonml', 'jsonml': j})
        print(f'  update {uid} -> success={r.get("success")} {r.get("logId","")}')
        time.sleep(0.4)
