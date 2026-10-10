#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 staging/59 的第 1、2、3、9 条并入 ch29 / ch28 / ch24。

- 新增为所在「性价比」分组内的条目；后续条目编号顺移。
- 章首导读 / 本章小结 顺句补上新增内容与条数。
用法: python3 apply.py           (dry run)
      python3 apply.py --go      (write)
"""
import json, re, sys, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-book/out/v5/_scratch')
import wg2

GO = '--go' in sys.argv

# ---------------------------- 新增条目正文（原样照 staging/59） ----------------------------

# ch29 第 1 条 -> 章内第 5 条
E29_1 = {
 'title': "5. 流水线单调重复、心里发闷，靠给自己留一点控制感撑过这一天",
 'meta': "性价比：极高\n成本：钱=0 时间=中 精力=中\n口径：职业寿命\n证据等级：B",
 'say': " 流水线的苦一半在累，一半在“我说了不算”。能改的只有几件小事：把工位收拾顺手、跟线长商量换一两个动作、给自己定当天的产量小目标、休息时离开车间走一圈。控制感多一分，闷的感觉就轻一分。",
 'wei': " Karasek 的工作要求—控制模型发现，高要求加低自主权的组合最容易带来精神紧张；流水线的要求你改不动，能加的是控制感。具体动作：到岗先把工具、物料、椅子高度调到顺手；跟线长申请多做一两道工序，换动作能打断单调；把当天的目标写成一个具体数字，达成就在心里打钩；班中休息一定离开工位，到车间外透气；下班换掉工服再回宿舍，给大脑一个“今天结束了”的信号。",
 'src': [
   "Karasek, R. A. (1979). Job Demands, Job Decision Latitude, and Mental Strain: Implications for Job Redesign. Administrative Science Quarterly, 24(2), 285-308. https://doi.org/10.2307/2392498",
   "国家统计局（2025）. 2024年农民工监测调查报告. https://www.stats.gov.cn/sj/zxfb/202504/t20250430_1959523.html",
   "纪录片《18岁的流水线》（2016，导演 Luojunnan Yin，别名《十八岁的流水线》）. 豆瓣条目 https://movie.douban.com/subject/27028789/",
 ],
 'xian': " 工作要求—控制模型是基于瑞典和美国上世纪七十年代调查提出的框架，不是针对流水线工人的专门实验，控制感能不能加上去还要看线长和工厂管理。把情绪调好只是让人能撑住，工作的单调本身不会因此改变。如果长期失眠、心慌、提不起劲，按第29章的办法去找专业帮助。",
}

# ch29 第 2 条 -> 章内第 6 条
E29_2 = {
 'title': "6. 撑不住的时候别一个人扛：先找身边人开口，再打 12356",
 'meta': "性价比：极高\n成本：钱=0 时间=少 精力=中\n口径：职业寿命\n证据等级：A",
 'say': " 情绪崩了先开口，顺序是：宿舍里信得过的工友、带你的师傅或班长、厂里的工会或人事。这些都没用就别自己扛，打全国统一心理援助热线 12356，免费、可匿名，多数城市每天提供不少于 18 小时。真的撑不住就走人，工作没了可以再找。",
 'wei': " 国家卫生健康委从 2024 年底起把全国心理援助热线统一到 12356，要求 2025 年 5 月 1 日前各地接通，每个设区的市至少一条、每条每天不少于 18 小时。厂里一般有工会，工会对侵害职工权益的行为有权要求纠正。具体做法：把让你难受的事用一句话写下来，写明发生了什么、多久了、影响了什么；找人开口时直接说“我最近状态不对，想跟你说说”，别拐弯；打热线前想好要讲的三件事；出现持续失眠、吃不下、不想上班超过两周，去当地精神卫生中心或综合医院心理科挂号，别当成矫情。",
 'src': [
   "国家卫生健康委（2024）. 关于应用“12356”全国统一心理援助热线电话号码的通知（国卫医政函〔2024〕259号）. https://www.gov.cn/zhengce/zhengceku/202412/content_6994470.htm",
   "新华社（2024）.“12356”将成为全国统一心理援助热线. https://www.gov.cn/lianbo/bumen/202412/content_6994462.htm",
 ],
 'xian': " 热线的接听质量和坐席数量各地不一，打不通可以隔一会儿再打，或先打当地已有的心理援助号码。本条里的开口顺序属通识经验，没有硬规定；《劳动法》第九十六条管的是强迫劳动和侮辱体罚，不涉及心理疏导。",
}

# ch28 第 3 条 -> 章内第 8 条
E28 = {
 'title': "8. 组长当众骂人、爆粗口：当场接住不顶牛，事后留证、找人，必要就报警",
 'meta': "性价比：高\n成本：钱=0 时间=中 精力=高\n口径：职业寿命 / 职业自由\n证据等级：A",
 'say': " 当众被骂，当场只回一句“收到，我马上改”，不顶牛、不对骂，也别摔东西。回到工位把时间、地点、谁在场、原话记下来。对方动手、罚款、扣工钱或者用脏话侮辱人，这已经超出管教的范围，可以找班长、人事、工会，也可以报警。",
 'wei': " 《劳动法》第九十六条规定，用人单位以暴力、威胁或者非法限制人身自由的手段强迫劳动，或者侮辱、体罚、殴打、非法搜查和拘禁劳动者的，由公安机关对责任人员处十五日以下拘留、罚款或者警告，构成犯罪的追究刑事责任。《民法典》第九百九十条、第一千零二十四条把人格权和名誉权写成受保护的权利。当场接住是为了不在气头上把事闹大，事后留证是为了真有纠纷时拿得出东西。具体做：用手机备忘录或小本子记下时间、地点、在场人、原话，有工友愿意作证更好；找工会或人事反映并要求书面回复；涉及动手或人身威胁直接打 110。同时分清“骂事”和“骂人”，说你干得慢属管理，骂你家里人、人格侮辱是另一回事。",
 'src': [
   "全国人大常委会. 中华人民共和国劳动法，第九十六条. https://www.mohrss.gov.cn/SYrlzyhshbzb/zcfg/flfg/201601/t20160119_232110.html",
   "全国人大常委会（2020）. 中华人民共和国民法典，第九百九十条、第一千零二十四条. http://www.npc.gov.cn/npc/c30834/202006/75ba6483b8344591abd07917e1d25cc8.shtml",
 ],
 'xian': " 骂人算不算侮辱、能不能立案，要看具体用词、场合和证据，一线执法和仲裁的判断尺度并不统一，报警不一定立案，但报案记录本身也是证据。真去举报要有换工作的心理准备，派遣工、小时工身份的维权成本更高，先算清楚再动，也可以先拨 12333 或问当地法律援助中心。",
}

# ch24 第 9 条 -> 章内第 9 条
E24 = {
 'title': "9. 厂区的恋爱和异地分居：把“能不能在一个地方”当成正经问题谈",
 'meta': "性价比：一般\n成本：钱=0 时间=多 精力=高\n口径：职业寿命 / 时间精力\n证据等级：C",
 'say': " 厂里的关系来得快也散得快，一个换厂、一个回老家，人就散了。处对象前想清楚两个人在哪个城市、待多久、能不能调到同一个厂或片区。分居两地的定个团聚时间点，别只说再等等。工友圈也要有边界：一起吃饭打球、互相替班可以，借钱、担保、合伙赌钱要设线。",
 'wei': " 国家统计局的数据显示，2024 年外出农民工里有配偶的只占 68.8%，本地农民工是 90.3%；全部农民工里未婚的占 17.1%，男性占 62.4%、女性占 31.7%，男女比例差得远，厂区择偶本身就难；报告还显示进城农民的业余生活主要是上网（53.3%）、休息（45.0%）、朋友聚会（34.9%），圈子基本就在厂区附近。实操上：谈之前把地点和时间摊开讲，能接受就处，接受不了早点了断；异地分居定下具体的团聚日期和攒钱计划；关系里一旦有动手、威胁、翻手机、要钱，按第28章和第43章的办法处理；工友之间借钱只借这次不心疼的数，超过就写借条，写明金额、日期、还款时间，留转账记录。",
 'src': [
   "国家统计局（2025）. 2024年农民工监测调查报告. https://www.stats.gov.cn/sj/zxfb/202504/t20250430_1959523.html",
   "中国新闻网（2025）. 国家统计局发布2024年农民工监测调查报告（全文转载）. http://www.chinanews.com.cn/gn/2025/04-30/10408410.shtml",
 ],
 'xian': " 统计局的数据是全国抽样结果，反映总体比例，不说明某个厂、某个人会怎样。厂区恋爱和异地分居没有强制规定，全靠两个人自己谈，本条的做法属通识经验，也没法保证关系一定稳。厂区感情随换厂而散的现象，纪录片《18岁的流水线》里有具体记录（2016，导演 Luojunnan Yin），但纪录片是影像观察，不是统计数据。",
}

# 来源列表用的 listId（沿用各章已有的来源/正文列表）
SRC_LIST = {'29': 'sgtqjbezckd', '28': 'wrxp1rmve4c', '24': '4gqze0wzrul'}

# 章首导读 / 本章小结 新文本
INTRO = {
 '29': ("情绪管理靠的是一组能重复做的固定动作：把情绪叫出名字、把事实和解读分开、给胡思乱想安排固定时间、"
        "气头上先离场、给改不动的工作留一点控制感。本章十条按从日常到应急的顺序排：前四条处理日常的命名、认知重评、"
        "反刍和愤怒，第五、六条讲流水线这类单调重复、改不动的工作里怎么给自己找控制感，以及撑不住时先找身边的人开口、"
        "再打 12356 求助，第七到第九条应对焦虑、被冤枉和情绪劳动，第十条讲情绪崩溃时的应急四步，以及什么信号下该找专业帮助。"),
 '28': ("职场里针对人格的贬低、骚扰、侮辱这些伤害，大多能对应到具体的法律条文，处理顺序是把行为对清楚、把证据留好、"
        "再选对渠道。本章九条按这个顺序排：前四条讲被反复否定或贬低时怎么记录、留痕，第五、六条讲侮辱、殴打、骚扰发生时"
        "先脱离现场、再报警或走劳动监察，第七条讲平时该存哪五类证据，第八条讲组长当众骂人、爆粗口时当场怎么接住、"
        "事后怎么留证找人，第九条讲什么条件下值得走、被迫解除时怎么主张经济补偿。"),
 '24': ("这一章讲人脉怎么算、怎么维护：先用「能不能互相帮上忙」判断一段关系值不值得维护，再讲怎么认识比你厉害的人、"
        "平时怎么维护，最后是和同事的分寸、遇到甩锅抢功和不想帮的忙怎么处理、活动该不该去、离职后怎么跟前同事来往，"
        "以及厂区恋爱和异地分居怎么把“能不能在一个地方”当正经问题谈。按这个顺序看，也可以只挑自己用得上的一条。"),
}

SUMMARY = {
 '29': ("情绪管理的落点是几个能重复做的固定动作：给情绪命名并记下来；遇到糟心事用 A-B-C-D 四栏把事实和解读分开；"
        "给胡思乱想设固定的想事时间；气头上先离开现场，冷静后再谈；流水线这类单调重复、改不动的工作，"
        "靠给自己留一点控制感撑过一天；撑不住时先找身边的人开口，再走工会或人事这些渠道；把焦虑写成最坏结果清单，"
        "并定一个当天能做的最小动作；被冤枉时先留痕、事后再沟通；把“假装开心”换成先理解对方再回应，并给下班设一个收尾动作；"
        "真崩了，用接地—离开—发泄—想小事四步先稳住，记下触发点。这些做法有的有研究或官方文件支持，有的是行之有效的经验，"
        "但都替代不了专业帮助：情绪问题持续两周以上、影响到上班、睡觉、吃饭，按第 6 条求助，全国统一心理援助热线是 12356。"),
 '28': ("职场伤害可以按行为对号、按渠道处理，不必靠情绪判断。可核对的要点：①反复针对人格、只给否定结论却不给具体要求的反馈，"
        "先按日期、原话和在场人记录；②遇到当众侮辱、殴打、体罚、非法搜查或限制人身自由，报警并投诉到劳动监察；"
        "③性骚扰可依民法典第一千零一十条请求行为人承担民事责任，用人单位负有预防、受理投诉、调查处置的义务，"
        "投诉后有关单位和国家机关应当及时处理并书面告知处理结果；④沟通记录、工作成果、考勤加班、工资合同和辱骂骚扰的原始记录，"
        "按时间线存好；⑤组长当众骂人、爆粗口，当场接住不顶牛，事后按日期记下原话和在场人，找班长、人事、工会反映，"
        "涉及动手或人身威胁直接报警；⑥走留可以按健康、发展、法律红线三个条件判断，离开时区分主动辞职与被迫解除，"
        "被迫解除依劳动合同法第三十八条主张经济补偿。多条官方渠道可以并行，先保证人身安全，再固定证据，最后选择渠道。"),
 '24': ("人脉的可用程度取决于你能提供什么、以及双方有没有实际来往。可核对的做法：①先练出别人用得上的本事，别用添加人数衡量关系；"
        "②把平时联系不多的弱关系用起来，2022 年一项覆盖约 2000 万用户的实验显示，中等偏弱的关系带来的新工作机会最多；"
        "③维护关系抓三件事——答应的事做到、受过帮助记着还、不占别人便宜；④和同事按合作关系处理，分工留痕、有话当面说；"
        "⑤离职后固定节奏维护几位靠谱的前同事，经员工推荐入职者离职率更低，有研究支持；⑥厂区处对象前先把“两个人能不能在一个地方、"
        "待多久”摊开谈，异地分居定一个具体的团聚时间点，工友之间借钱、担保、合伙赌钱要设线。"),
}


def entry_blocks(e, list_id):
    """构造一条新条目的 jsonml 块序列（h3 + 元信息 + 四块 + hr）。"""
    return [
        wg2.H3(e['title']),
        wg2.META(e['meta']),
        wg2.PARA("说人话：", e['say']),
        wg2.PARA("为什么 / 怎么做：", e['wei']),
        wg2.LABEL("来源："),
        *[wg2.BULLET(s, list_id) for s in e['src']],
        wg2.PARA("限制与争议：", e['xian']),
        wg2.HR(),
    ]


# 每章：CH -> dict(anchor_uuid=插入锚点(其后插), new_entries=[...], renumber=[(uuid,old,new)], intro_uuid, summary_uuid)
CH = {
 '29': dict(
   anchor_uuid='mv0r6jqy6l2puar1qn7',   # item4 之后的 hr
   anchor_text_check='4. 气头上先离开现场十分钟',
   new=[E29_1, E29_2],
   renumber=[('mv0r6jr0a1d9pxm5fga', '5.', '7.'),
             ('mv0r6jtpfc1vzv58mi', '6.', '8.'),
             ('mv0r6jx62p02w9me7un', '7.', '9.'),
             ('mv0r6kpvnyhczejoyn', '8.', '10.')],
   intro_uuid='mv0w2ovlusbiu7yooi',
   summary_uuid='mv15i4cpo59dcj0y9hq',
 ),
 '28': dict(
   anchor_uuid='mv0r6hgr3ykduxg76s1',   # item7 之后的 hr（高性价比组末尾）
   anchor_text_check='7. 从现在起按时间线存五类证据',
   new=[E28],
   renumber=[('mv0r6hgv4tswtb79xlb', '8.', '9.')],
   intro_uuid='mv0w22977iy1vpu0x1',
   summary_uuid='mv0utct78o7qi5f4ngm',
 ),
 '24': dict(
   anchor_uuid='mv0r68iz6x4h5yayjxl',   # item8 之后的 hr（一般性价比组末尾）
   anchor_text_check='8. 离职时把交接做干净',
   new=[E24],
   renumber=[],
   intro_uuid='mv0w3i5g5tw8z0r0o2c',
   summary_uuid='mv0uezrfunqi3gmj7v9',
 ),
}


def find(blocks, uid):
    for b in blocks:
        if isinstance(b, list) and len(b) >= 2 and isinstance(b[1], dict) and b[1].get('uuid') == uid:
            return b
    return None


def renum_h3(b, new_num):
    txt = wg2.text_of(b)
    m = re.match(r'^(\d+)\.\s*(.*)$', txt, re.S)
    assert m, txt
    body = m.group(2)
    leaf = [n for n in wg2.leaves(b)]
    # replace whole text: rebuild h3
    return ['h3', {'uuid': b[1]['uuid']},
            ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, '%s. %s' % (new_num, body)]]]


def set_labeled_block(b, label, text):
    """把 bold-label + body 段落改成 新 label + 新 text，保留 uuid。"""
    return ['p', {'blockquote': True, 'uuid': b[1]['uuid']},
            ['span', {'data-type': 'text'},
             ['span', {'bold': True, 'data-type': 'leaf'}, label],
             ['span', {'data-type': 'leaf'}, text]]]


def check_meta(e):
    for k in ('性价比', '成本', '口径', '证据等级'):
        assert k in e['meta'], (k, e['meta'])
    for blk in (e['say'], e['wei'], e['xian']):
        assert blk.strip(), 'empty block'
    assert e['src'], 'no source'


def main():
    plans = {}
    for ch, cfg in CH.items():
        for e in cfg['new']:
            check_meta(e)
        jm = wg2.fetch_jm(ch)
        blocks = wg2.blocks_of(jm)
        anchor = find(blocks, cfg['anchor_uuid'])
        assert anchor is not None, 'anchor missing %s' % ch
        assert anchor[0] == 'hr', ('anchor not hr', anchor[0])
        # 锚点前最近的一条 h3 标题须匹配
        ai = blocks.index(anchor)
        prev_h3 = next(blocks[k] for k in range(ai - 1, -1, -1) if blocks[k][0] == 'h3')
        assert cfg['anchor_text_check'] in wg2.text_of(prev_h3), wg2.text_of(prev_h3)[:40]
        for uid, _o, _n in cfg['renumber']:
            b = find(blocks, uid)
            assert b is not None and b[0] == 'h3', ('renumber target', uid)
        ib = find(blocks, cfg['intro_uuid'])
        sb = find(blocks, cfg['summary_uuid'])
        assert ib is not None and ib[1].get('blockquote') and '本章小结' not in wg2.text_of(ib), wg2.text_of(ib)[:20]
        assert ib is blocks[1], 'intro not at index 1'
        assert sb is not None and '本章小结' in wg2.text_of(sb), wg2.text_of(sb)[:20]
        assert sb is blocks[-1], 'summary not last block'
        plans[ch] = dict(blocks=blocks, anchor=anchor)
        print('ch%s: nblocks=%d  anchor=%s  新条目=%d  顺移=%d' %
              (ch, len(blocks), cfg['anchor_uuid'], len(cfg['new']), len(cfg['renumber'])))

    if not GO:
        print('\nDRY RUN. 不会写入。加 --go 执行。')
        return

    for ch, cfg in CH.items():
        v = wg2.save_version(ch)
        print('\nch%s save_doc_version ->' % ch, v.get('success'),
              json.dumps({k: v[k] for k in v if k != 'logId'}, ensure_ascii=False)[:200])

    # ---- 插入 + 顺移 + 改导读/小结 ----
    for ch, cfg in CH.items():
        # 1) 插入新条目
        ids = wg2.insert_entry_after(ch, cfg['anchor_uuid'],
                                     [b for e in cfg['new'] for b in entry_blocks(e, SRC_LIST[ch])])
        print('ch%s inserted %d blocks, first=%s' % (ch, len(ids), ids[:1]))
        time.sleep(0.8)
        # 2) 顺移后面的条目编号
        for uid, old, new in cfg['renumber']:
            jm = wg2.fetch_jm(ch)
            b = find(wg2.blocks_of(jm), uid)
            assert b is not None, uid
            assert wg2.text_of(b).startswith(old + ' '), wg2.text_of(b)[:20]
            nb = renum_h3(b, new.rstrip('.'))
            r = wg2.update_block(ch, uid, nb)
            print('  ch%s renum %s %s->%s ok=%s' % (ch, uid, old, new, r.get('success')))
            time.sleep(0.6)
        # 3) 章首导读
        jm = wg2.fetch_jm(ch)
        b = find(wg2.blocks_of(jm), cfg['intro_uuid'])
        nb = ['p', {'blockquote': True, 'uuid': cfg['intro_uuid']},
              ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, INTRO[ch]]]]
        r = wg2.update_block(ch, cfg['intro_uuid'], nb)
        print('  ch%s intro ok=%s' % (ch, r.get('success')))
        time.sleep(0.6)
        # 4) 本章小结
        jm = wg2.fetch_jm(ch)
        b = find(wg2.blocks_of(jm), cfg['summary_uuid'])
        nb = ['p', {'blockquote': True, 'uuid': cfg['summary_uuid']},
              ['span', {'data-type': 'text'},
               ['span', {'bold': True, 'data-type': 'leaf'}, '本章小结：'],
               ['span', {'data-type': 'leaf'}, ' ' + SUMMARY[ch]]]]
        r = wg2.update_block(ch, cfg['summary_uuid'], nb)
        print('  ch%s summary ok=%s' % (ch, r.get('success')))
        time.sleep(0.6)
    print('\nDONE')


if __name__ == '__main__':
    main()
