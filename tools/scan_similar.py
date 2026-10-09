#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书同类问题扫描：找出与「未找到…官方数据」同族的写法问题。"""
import re, glob, os, collections

PATS = {
    '①未找到…官方数据类': r'未找到[^\n。]{0,25}(官方数据|官方口径|统计口径|统计)',
    '②辩论腔标签': r'反方观点|本书立场|正方观点|我方观点',
    '③不是X而是Y对比句': r'(不是|并非)[^，。；\n]{2,20}(而是|，是)',
    '④口号/绝对化': r'没有之一|包治|一劳永逸|稳赚|必然|一定能|绝对不会|永远不要|彻底解决',
    '⑥列表项内加粗(钉钉会显星号)': r'^\s*[-*]\s+\*\*',
    '⑦半角~区间(会变下标)': r'\d~\d',
    '⑧厂商/平台推荐': r'推荐(使用|用|购买|安装)|建议(购买|入手)|首选[^，。\n]{0,6}(工具|软件|平台)',
    '⑩直引号/英文撇号': r'["\']',
}
ARROW = {'⑤括号密集(单条≥4个括号)': None, '⑨来源块无链接也无「无」': None}

tot = collections.Counter()
bych = collections.defaultdict(collections.Counter)
ex = collections.defaultdict(list)

for f in sorted(glob.glob('book/*.md')):
    n = os.path.basename(f)[:2]
    t = open(f, encoding='utf-8').read()
    for name, p in PATS.items():
        for m in re.finditer(p, t, re.M):
            tot[name] += 1; bych[name][n] += 1
            if len(ex[(name, n)]) < 2:
                ln = t[max(0, t.rfind('\n', 0, m.start()) + 1): t.find('\n', m.end())]
                ex[(name, n)].append(ln.strip()[:110])
    for b in re.split(r'\n(?=### )', t):
        if not b.startswith('### '):
            continue
        num = b.split('.', 1)[0].replace('###', '').strip()
        k = len(re.findall(r'（[^）]{1,40}）', b))
        if k >= 4:
            tot['⑤括号密集(单条≥4个括号)'] += 1; bych['⑤括号密集(单条≥4个括号)'][n] += 1
            if len(ex[('⑤括号密集(单条≥4个括号)', n)]) < 3:
                ex[('⑤括号密集(单条≥4个括号)', n)].append(f'第{num}条 {k}个括号')
        m = re.search(r'\*\*来源[:：]\*\*(.*?)(?=\n\*\*|\Z)', b, re.S)
        if m:
            s = m.group(1)
            if 'http' not in s and not re.fullmatch(r'\s*无\s*[。.]?\s*', s):
                tot['⑨来源块无链接也无「无」'] += 1; bych['⑨来源块无链接也无「无」'][n] += 1
                if len(ex[('⑨来源块无链接也无「无」', n)]) < 2:
                    ex[('⑨来源块无链接也无「无」', n)].append(s.strip().replace('\n', ' ')[:110])

for name in list(PATS) + list(ARROW):
    c = bych[name]
    print(f'\n### {name} — 合计 {tot[name]} 处 / {len(c)} 章')
    for ch, k in sorted(c.items()):
        print(f'   ch{ch}({k})', '｜'.join(ex[(name, ch)])[:175])
