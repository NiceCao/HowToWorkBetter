#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge staging/57 item 10 into ch11 as a new entry (一般性价比 group).
New entry appended at end of the 一般性价比 group -> becomes item 11.
Also supplements chapter intro (导读) and 本章小结 topic lists.
Run:  python3 ch11_apply.py          (dry run)
      python3 ch11_apply.py --go     (apply)
"""
import json, sys, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

GO = '--go' in sys.argv
CH = '11'

# ---- new entry blocks ----
H3_TITLE = "11. 进厂前问清宿舍收不收费、几人间、饭卡怎么扣，把口头承诺落到纸上"
META_TEXT = "性价比：一般\n成本：钱=0 时间=少 精力=低\n口径：收入 / 时间精力\n证据等级：C"
SHUO = " 宿舍和食堂是很多厂的隐性花销。进厂前把这几样问清：宿舍收不收钱、一个月扣多少、几人间、水电谁出、有没有空调热水；食堂是不是刷工卡、饭菜怎么计价、有没有补贴。所有口头说的，写进录用通知或合同，或者让招工的人发条微信确认。"
WEI = " 问的时候把答案记下来，最好让对方发条微信白纸黑字确认。住宿费、水电费如果从工资里扣，要知道每月大概多少、扣完到手还剩多少，别到发工资才发现少了一大截。宿舍条件、消防通道、热水这些能当天看的就看。发现和说的差太多，趁早决定去留，别被押着工资拖着走。"
LAI = " 无。"
XIAN = " 宿舍、食堂的好坏和收费没有全国统一标准，本条属通识经验，不同厂差异很大。包吃住的厂往往工资开得低一点，把包吃住折成钱算清楚，才知道哪家更划算。"

NEW_BLOCKS = [
    wg2.H3(H3_TITLE),
    wg2.META(META_TEXT),
    wg2.PARA("说人话：", SHUO),
    wg2.PARA("为什么 / 怎么做：", WEI),
    wg2.PARA("来源：", LAI),
    wg2.PARA("限制与争议：", XIAN),
    wg2.HR(),
]

# ---- intro / summary updates ----
DAO_OLD = "本章讲怎么看懂工资之外的福利和补贴：五险一金缴费基数、企业年金、补充医疗、年假、培训预算、员工折扣和各项现金补贴。这些能拿的都核对清楚，并按实际价值折算进总包再比较 offer。"
DAO_NEW = "本章讲怎么看懂工资之外的福利和补贴：五险一金缴费基数、企业年金、补充医疗、年假、培训预算、员工折扣和各项现金补贴，以及进厂打工时要先问清的宿舍、食堂收费这类隐性开销。这些能拿的都核对清楚，并按实际价值折算进总包再比较 offer。"
XIAO_OLD = " 比 offer 时按年度总包算，不只比月薪：把五险一金缴费基数、企业年金、补充医疗、年假、培训预算和各项补贴折算进来。五险一金按实际工资足额缴还是按最低基数缴，直接影响进个人账户的钱，以月薪 1 万、公积金 12% 估算一年差约 2.4 万元。企业年金由单位自愿建立，能参加就参加，先问清缴费比例和归属规则。补充医疗、员工折扣按你可能用到的部分估值。软性福利当加分项，不作为选工作的主要理由。"
XIAO_NEW = XIAO_OLD + "进厂打工的，宿舍收不收费、几人间、饭卡怎么扣，进厂前先问清、把口头承诺落到纸上。"

jm = wg2.fetch_jm(CH)
blocks = wg2.blocks_of(jm)
assert len(blocks) == 120, len(blocks)
# locate anchors
b1, b118, b119 = blocks[1], blocks[118], blocks[119]
assert b1[1].get('blockquote') is True and b1[1]['uuid'] == 'mv0tkujnbad8pphama', b1[1]
assert b118[0] == 'hr' and b118[1]['uuid'] == 'mv0me6g1ws5l6ye9dbm', b118[0]
assert b119[1].get('blockquote') is True and b119[1]['uuid'] == 'mv15e46wjwfcwmak7o', b119[1]
assert wg2.text_of(b1) == DAO_OLD, 'intro text changed?'
assert wg2.text_of(b119).lstrip().startswith('本章小结：'), wg2.text_of(b119)[:30]
# last entry before hr(118) should be item 10
assert wg2.text_of(blocks[108]).startswith('10. 把免费零食'), wg2.text_of(blocks[108])

print('PRE: nblocks=%d  末条目=%s' % (len(blocks), wg2.text_of(blocks[108])[:20]))
print('insert new entry after hr uuid=', b118[1]['uuid'])

if not GO:
    print('DRY RUN — would insert %d blocks, update 导读(block1) + 小结(block119).  No writes.' % len(NEW_BLOCKS))
    sys.exit(0)

# 1) insert new entry after hr(118)
ids = wg2.insert_entry_after(CH, b118[1]['uuid'], NEW_BLOCKS)
print('inserted:', ids)
time.sleep(1)

# 2) update intro (block1) — keep blockquote + uuid
dao_block = ['p', {'blockquote': True, 'uuid': b1[1]['uuid']},
             ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, DAO_NEW]]]
print('update intro:', wg2.update_block(CH, b1[1]['uuid'], dao_block))
time.sleep(1)

# 3) update 小结 (block119) — keep bold label + uuid
xiao_block = ['p', {'blockquote': True, 'uuid': b119[1]['uuid']},
              ['span', {'data-type': 'text'},
               ['span', {'bold': True, 'data-type': 'leaf'}, '本章小结：'],
               ['span', {'data-type': 'leaf'}, XIAO_NEW]]]
print('update 小结:', wg2.update_block(CH, b119[1]['uuid'], xiao_block))
print('DONE')
