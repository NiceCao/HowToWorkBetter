#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge staging/59 进厂 items into ch08/35/39/43 (live DingTalk doc).

Merge plan (new item positions; subsequent items renumber +1):
  ch35  技能投资 : draft5(极高)->item6 ; draft6(高)->item10
  ch39  职场健康 : draft8(极高)->item6 ; draft7(高)->item10
  ch43  职场维权 : draft4(极高)->item5
  ch08  择业反面清单 : draft10(极高)->item5
"""
import sys, json, time, re
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw

HERE = '/home/ubuntu/projects/work-guide-book/out/v5/_scratch/wg3'
IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))
DRAFT = json.load(open(f'{HERE}/draft.json', encoding='utf-8'))

NODES = {'08': IDX['08'][1], '35': IDX['35'][1], '39': IDX['39'][1], '43': IDX['43'][1]}

# ---------------------------------------------------------------- jsonml builders
def h3(text):
    return ["h3", {}, ["span", {"data-type": "text"}, ["span", {"data-type": "leaf"}, text]]]

def meta(text):
    return ["p", {"blockquote": True},
            ["span", {"data-type": "text"}, ["span", {"data-type": "leaf"}, text]]]

def bold_para(label, text):
    return ["p", {}, ["span", {"data-type": "text"},
            ["span", {"bold": True, "data-type": "leaf"}, label],
            ["span", {"data-type": "leaf"}, text]]]

def para(text):
    return ["p", {}, ["span", {"data-type": "text"}, ["span", {"data-type": "leaf"}, text]]]

def bullet(text, list_id):
    return ["p", {"list": {"listId": list_id, "isOrdered": False, "level": 0,
                           "listStyle": {"format": "bullet", "text": "\u25cf", "align": "left"}}},
            ["span", {"data-type": "text"}, ["span", {"data-type": "leaf"}, text]]]

def build_entry(ch, num, draft_num):
    e = DRAFT[str(draft_num)]
    lab = e['labels']
    meta_text = (f"性价比：{lab['性价比']}\n成本：{lab['成本']}\n"
                 f"口径：{lab['口径']}\n证据等级：{lab['证据等级']}")
    src_list_id = f"wg3{ch}{num}src"
    blocks = [
        h3(f"{num}. {e['title']}"),
        meta(meta_text),
        bold_para("说人话：", " " + e['say']),
        bold_para("为什么 / 怎么做：", " " + e['why']),
        bold_para("来源：", ""),
    ]
    for s in e['sources']:
        blocks.append(bullet(s, src_list_id))
    blocks.append(bold_para("限制与争议：", " " + e['limit']))
    return blocks, e

# ---------------------------------------------------------------- helpers on jsonml
def leaves(node):
    out = []
    if isinstance(node, list):
        if len(node) >= 2 and isinstance(node[1], dict) and node[1].get('data-type') == 'leaf':
            if len(node) >= 3 and isinstance(node[2], str):
                out.append(node[2])
            return out
        for c in node[1:]:
            out.extend(leaves(c))
    return out

def text_of(b):
    return ''.join(leaves(b))

def tag_of(b):
    return b[0] if isinstance(b, list) and b else None

def uuid_of(b):
    return b[1].get('uuid') if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) else None

def fetch_jm(ch):
    for _ in range(6):
        r = gw.call('get_document_content', {'nodeId': NODES[ch], 'format': 'jsonml'})
        if r.get('jsonml'):
            return json.loads(r['jsonml'])
        time.sleep(2)
    raise RuntimeError(f'no jsonml ch{ch}')

def find_id(jm, text_startswith, tag=None):
    hits = []
    for b in jm[2:]:
        if tag and tag_of(b) != tag:
            continue
        t = text_of(b)
        if t.startswith(text_startswith):
            hits.append(uuid_of(b))
    assert len(hits) == 1, f'find {text_startswith!r} -> {hits}'
    return hits[0]

def find_id_sub(jm, needle, tag=None):
    hits = []
    for b in jm[2:]:
        if tag and tag_of(b) != tag:
            continue
        if needle in text_of(b):
            hits.append(uuid_of(b))
    assert len(hits) == 1, f'find sub {needle!r} -> {hits}'
    return hits[0]

def save_version(ch):
    return gw.call('save_doc_version', {'nodeId': NODES[ch]})

def do_update(ch, block_id, jm_block):
    j = json.dumps(jm_block, ensure_ascii=False)
    for _ in range(3):
        r = gw.call('update_document_block', {'nodeId': NODES[ch], 'blockId': block_id,
                                              'format': 'jsonml', 'jsonml': j})
        if r.get('success'):
            return r
        print('   update retry', block_id, r); time.sleep(2)
    raise RuntimeError(f'update failed {ch} {block_id}')

def do_insert_after(ch, ref_id, jm_block):
    j = json.dumps(jm_block, ensure_ascii=False)
    for _ in range(3):
        r = gw.call('insert_document_block', {'nodeId': NODES[ch], 'referenceBlockId': ref_id,
                                              'where': 'after', 'format': 'jsonml', 'jsonml': j})
        if r.get('success') and r.get('blockId'):
            return r['blockId']
        print('   insert retry', r); time.sleep(2)
    raise RuntimeError(f'insert failed {ch} after {ref_id}')

def insert_seq(ch, ref_id, blocks):
    ids = []
    ref = ref_id
    for b in blocks:
        nb = do_insert_after(ch, ref, b)
        ids.append(nb); ref = nb
    return ids

def heading_renumber(ch, jm, old_needle, new_prefix):
    bid = find_id(jm, old_needle, tag='h3')
    b = next(x for x in jm[2:] if uuid_of(x) == bid)
    t = text_of(b)
    nt = re.sub(r'^\d+\.\s*', new_prefix, t)
    assert nt != t, f'no renum for {t!r}'
    do_update(ch, bid, h3(nt))
    return bid, nt

def para_renumber(ch, jm, needle, new_prefix_old, new_prefix_new):
    """for preview paragraphs: replace leading '条目 N：'"""
    bid = find_id_sub(jm, needle, tag='p')
    b = next(x for x in jm[2:] if uuid_of(x) == bid)
    t = text_of(b)
    assert t.startswith(new_prefix_old), t
    nt = new_prefix_new + t[len(new_prefix_old):]
    do_update(ch, bid, para(nt))
    return bid, nt

def update_intro(ch, jm, needle, newtext):
    bid = find_id_sub(jm, needle, tag='p')
    b = next(x for x in jm[2:] if uuid_of(x) == bid)
    is_quote = isinstance(b[1], dict) and b[1].get('blockquote')
    do_update(ch, bid, meta(newtext) if is_quote else para(newtext))
    return bid

# ---------------------------------------------------------------- per-chapter edits
def edit_ch35(mode):
    ch = '35'
    jm = fetch_jm(ch)
    b5, e5 = build_entry(ch, 6, 5)     # draft5 -> item6 (极高)
    b6, e6 = build_entry(ch, 10, 6)    # draft6 -> item10 (高)
    new_intro = ("这一章讲怎么判断一门技能值不值得投入，按性价比从高到低排："
                 "前六条是投入低、回报高的动作，先练能独立交付的硬技能、优先练换公司也能用的通用能力、"
                 "持续积累行业认知、把技能更新当长期动作、把重复劳动攒成能带走的能力、让老师傅愿意教你；"
                 "中间四条讲考证、读研或读 MBA、学英语这类花钱多的投入怎么算账，以及在厂里当多能工、拿到技能等级；"
                 "最后一条讲副业从主业延伸起步。")
    print('ch35 plan: item6=draft5(极高) after 5限制 ; item10=draft6(高) after 8限制 ; '
          'renum 6->7,7->8,8->9,9->11 ; intro update')
    for b in b5: print('   NEW6', tag_of(b), text_of(b)[:40])
    for b in b6: print('   NEW10', tag_of(b), text_of(b)[:40])
    return {'ch': ch, 'jm0': jm, 'entries': [(6, b5), (10, b6)],
            'refs': ['这项研究针对企业内的岗位轮换', 'EF 指数是自愿在线测试'],
            'renum': [('6. 考证优先选', '7. '), ('7. 读研或读 MBA', '8. '),
                      ('8. 英语按用途学', '9. '), ('9. 副业先从主业', '11. ')],
            'previews': [], 'intro_needle': '这一章讲怎么判断', 'intro': new_intro}

def edit_ch39(mode):
    ch = '39'
    jm = fetch_jm(ch)
    b8, e8 = build_entry(ch, 6, 8)     # draft8 -> item6 (极高)
    b7, e7 = build_entry(ch, 10, 7)    # draft7 -> item10 (高)
    new_intro = ("这一章讲怎么把身体维持在一个能长期干活的状态，减少久坐、盯屏、熬夜和情绪压力带来的损耗。"
                 "本章十一条按这个顺序排：前六条讲久坐怎么切碎、用眼怎么安排、作息和加班怎么管、"
                 "情绪困扰怎么处理、出差在外怎么保证安全、久站久坐与粉尘噪声怎么防护，"
                 "中间四条讲体检项目怎么选、饮食和活动量怎么补、普通疾病与法定职业病怎么分、夜班倒班怎么减害，"
                 "第十一条讲工伤发生后怎么在时效内申请认定。")
    pv6 = para("条目 6：久站久坐、粉尘噪音——每小时动一动、换一次重心，粉尘噪声岗位戴口罩耳塞，"
               "班前班中班后三次职业健康检查别省")
    pv6n = meta("腕管综合征等职业病有严格限定，腰肌劳损、久站引起的下肢静脉曲张不在目录内，只能按普通病走医保")
    pv10 = para("条目 10：上夜班、两班倒——长期夜班被国际癌症研究机构列为很可能致癌（2A 类），"
                "能争取的是固定班次、下班先睡够、宿舍用遮光帘耳塞")
    pv10n = meta("2A 说的是证据强度，不等于上夜班就会得癌；倒班常由生产安排决定，个人能改的有限")
    return {'ch': ch, 'jm0': jm, 'entries': [(6, b8), (10, b7)],
            'refs': ['这条属通识经验，不同城市、不同性别', '新增目录里被叫作鼠标手的腕管综合征'],
            'renum': [('6. 按年龄和风险', '7. '), ('7. 把每天盐油糖', '8. '),
                      ('8. 先分清普通疾病', '9. '), ('9. 发生工伤后', '11. ')],
            'previews': [
                # (kind, ref_needle, payload)
                ('add', '在陌生城市出事多半在夜里和路上', (pv6, pv6n)),   # after 条目5 note
                ('ren', '条目 6：按年龄和风险', ('条目 6：', '条目 7：')),
                ('ren', '条目 7：把每天盐油糖', ('条目 7：', '条目 8：')),
                ('ren', '条目 8：先分清普通疾病', ('条目 8：', '条目 9：')),
                ('add', '能不能算职业病要看是否在目录内', (pv10, pv10n)),  # after 条目8 note
                ('ren', '条目 9：发生工伤', ('条目 9：', '条目 11：')),
            ],
            'intro_needle': '这一章讲怎么把身体', 'intro': new_intro}

def edit_ch43(mode):
    ch = '43'
    jm = fetch_jm(ch)
    b4, e4 = build_entry(ch, 5, 4)     # draft4 -> item5 (极高)
    new_intro = ("这一章讲被公司侵害权益时怎么把该拿的拿回来：先把事情归类，选对受理渠道和时效，再从入职起把证据留好。"
                 "后面按场景展开，依次是被拖欠工资、乱罚款押工资扣工钱、社保和公积金没按实际工资缴、"
                 "被人格侮辱排挤或性骚扰、上下班受伤、申请劳动仲裁这些常见情形，"
                 "最后是各类劳动问题都能用的官方热线和网上渠道。")
    return {'ch': ch, 'jm0': jm, 'entries': [(5, b4)],
            'refs': ['支付令的缺点是公司一提出书面异议'],
            'renum': [('5. 遇到人格侮辱', '6. '), ('6. 上班受伤要走工伤认定', '7. '),
                      ('7. 申请劳动仲裁按五步走', '8. '), ('8. 公司以竞业限制', '9. '),
                      ('9. 遇到劳动问题先打对热线', '10. '), ('10. 仲裁请求要逐项分开写', '11. '),
                      ('11. 裁决生效后对方不付钱', '12. ')],
            'previews': [], 'intro_needle': '这一章讲被公司侵害权益', 'intro': new_intro}

def edit_ch08(mode):
    ch = '08'
    jm = fetch_jm(ch)
    b10, e10 = build_entry(ch, 5, 10)  # draft10 -> item5 (极高)
    new_intro = ("有些岗位在招聘和合同环节就埋着问题，进去以后才发现收入、保障可能落空。"
                 "本章把择业里常见的几类陷阱拆开讲：无底薪纯提成、试用期不签合同不发工资、入职先收钱、"
                 "老乡工头拉你入传销或赌局、境外高薪招聘、劳务派遣和外包、以租代招、兼职垫钱、抬头虚高。"
                 "每一类都写清判断标准和对应的法律条文。")
    return {'ch': ch, 'jm0': jm, 'entries': [(5, b10)],
            'refs': ['计件单价和定额由企业定'],
            'renum': [('5. 遇到「境外高薪', '6. '), ('6. 面试说「正式岗」', '7. '),
                      ('7. 遇到「以租代招」', '8. '), ('8. 兼职要你先垫钱', '9. '),
                      ('9. 抬头好听却说不清', '10. ')],
            'previews': [], 'intro_needle': '有些岗位在招聘和合同环节', 'intro': new_intro}

EDITS = {'35': edit_ch35, '39': edit_ch39, '43': edit_ch43, '08': edit_ch08}

def apply_chapter(fn, mode):
    plan = fn(mode)
    ch = plan['ch']
    print(f'\n########## ch{ch} ##########')
    # resolve references read-only
    jm = fetch_jm(ch)
    resolved = {}
    for (num, blocks), ref_needle in zip(plan['entries'], plan['refs']):
        resolved[f'insert item{num}'] = find_id_sub(jm, ref_needle, tag='p')
        print(f'  [ref] insert item{num} after {resolved[f"insert item{num}"]} ({ref_needle!r})')
    for old, new in plan['renum']:
        bid = find_id(jm, old, tag='h3')
        print(f'  [ref] renum {old!r} -> {new} @ {bid}')
    for kind, needle, payload in plan['previews']:
        bid = find_id_sub(jm, needle, tag='p')
        print(f'  [ref] preview {kind} {needle!r} @ {bid}')
    ib = find_id_sub(jm, plan['intro_needle'], tag='p')
    print(f'  [ref] intro @ {ib}')
    if mode != 'apply':
        print('   (dry run, no writes)')
        return plan
    # 1) save version
    v = save_version(ch)
    print('  save_doc_version ->', json.dumps(v, ensure_ascii=False))
    jm = fetch_jm(ch)
    # 2) insert new entries (in ref order)
    for (num, blocks), ref_needle in zip(plan['entries'], plan['refs']):
        ref = find_id_sub(jm, ref_needle, tag='p')
        print(f'  insert item{num} after ref {ref} ({ref_needle!r})')
        ids = insert_seq(ch, ref, blocks)
        print('    new blocks:', ids)
    # 3) renumber headings
    jm = fetch_jm(ch)
    for old, new in plan['renum']:
        bid, nt = heading_renumber(ch, jm, old, new)
        print(f'  renum {old!r} -> {nt!r} ({bid})')
    # 4) preview edits
    if plan['previews']:
        jm = fetch_jm(ch)
        for kind, needle, payload in plan['previews']:
            if kind == 'ren':
                bid, nt = para_renumber(ch, jm, needle, payload[0], payload[1])
                print(f'  preview renum {needle!r} -> {nt!r} ({bid})')
            elif kind == 'add':
                # needle identifies the note blockquote (has no text -> use anchor via jsonml text)
                bid = find_id_sub(jm, needle, tag='p')
                ids = insert_seq(ch, bid, list(payload))
                print(f'  preview add after {bid} -> {ids}')
    # 5) intro
    jm = fetch_jm(ch)
    bid = update_intro(ch, jm, plan['intro_needle'], plan['intro'])
    print(f'  intro updated ({bid})')
    # record rollback version
    plan['rollback'] = v
    return plan

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dry'
    only = sys.argv[2] if len(sys.argv) > 2 else None
    res = {}
    for ch in ('35', '39', '43', '08'):
        if only and ch != only:
            continue
        res[ch] = apply_chapter(EDITS[ch], mode)
    json.dump({ch: {k: v for k, v in p.items() if k != 'jm0'} for ch, p in res.items()},
              open(f'{HERE}/apply_result_{mode}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nDONE', mode)
