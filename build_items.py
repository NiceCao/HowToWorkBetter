# -*- coding: utf-8 -*-
"""从 book/*.md 解析出全部条目（含元信息与 GitHub 锚点），写到 data/items.json。"""
import glob, json, re, unicodedata

CH = {c['n']: c for c in json.load(open('data/chapters.json', encoding='utf-8'))}

PUNCT = '，。、：；！？（）「」『』《》〈〉·—…“”‘’"\'()[]{}【】,:;!?<>|/@#$%^&*+=~`\\'


def anchor(text):
    """按 GitHub 的 heading 锚点规则生成：小写、去标点、空格转 -"""
    s = text.strip().lower()
    s = ''.join(ch for ch in s if ch not in PUNCT)
    s = re.sub(r'\s+', '-', s)
    return s


def bucket(v, kind):
    """成本统一成三档，便于筛选。"""
    v = (v or '').strip()
    if not v:
        return ''
    if kind == 'money':
        if v.startswith('0') or v.startswith('不花') or '公司承担' in v:
            return '不花钱'
        if v.startswith('少') or v.startswith('低') or v.startswith('几块') or '以内' in v:
            return '少'
        return '中/多'
    if any(v.startswith(x) for x in ('0', '极低', '极少', '低', '少', '顺手')):
        return '少'
    if v.startswith('中'):
        return '中'
    return '多'


def field(head, pattern, default=None):
    m = re.search(pattern, head)
    return m.group(1).strip() if m else default


items = []
for f in sorted(glob.glob('book/*.md')):
    n = int(f[5:7])
    t = open(f, encoding='utf-8').read()
    for b in re.split(r'\n(?=### )', t):
        if not b.startswith('### '):
            continue
        title = b.split('\n', 1)[0][4:].strip()
        num = field(title, r'^(\d+)\.', '0')
        title_text = re.sub(r'^\d+\.\s*', '', title)
        head = b.split('**说人话')[0]
        head = re.sub(r'[*>\s]+', ' ', head)          # 元信息常被写成一行，先压平

        lv = field(head, r'性价[比价][:：]\s*([^ ]+?)(?=\s*成本|\s*口径|\s*证据|$)', '')
        lv = '高' if lv.startswith('高') else ('极高' if lv.startswith('极高') else ('一般' if lv.startswith('一般') else lv))
        money = field(head, r'钱\s*=\s*([^\s]+?)(?=\s|$)', '')
        time = field(head, r'时间\s*=\s*([^\s]+?)(?=\s|$)', '')
        energy = field(head, r'精力\s*=\s*([^\s=]+?)(?=口径|证据|\s|$)', '')
        scope = field(head, r'口径[:：]\s*(.*?)(?=\s*证据等级|$)', '')
        ev = field(head, r'证据等级[:：]\s*([ABCabc])', '').upper()
        scopes = [x.strip() for x in re.split(r'[/／+]', scope) if x.strip()]
        dispute = ('限制与争议' in b)
        # 来源块：统计链接数，以及是否明说「未找到直接相关的官方数据」
        m = re.search(r'\*\*来源[^\n]*\*\*(.*?)(?=\n\*\*|\Z)', b, re.S)
        src = m.group(1) if m else ''
        links = re.findall(r'https?://\S+', src)
        noref = bool(re.search(r'未找到(直接相关的)?官方', src)) or bool(re.search(r'^\s*来源[:：]\s*无\s*$', src, re.M))
        srcs = len({l.rstrip('.,，。') for l in links})
        money, time, energy = bucket(money, 'money'), bucket(time, 'time'), bucket(energy, 'energy')
        scopes = [s for s in dict.fromkeys(s.split('（')[0].replace(' ', '') for s in scopes) if s in ('收入', '职业寿命', '时间精力', '职业自由')]
        items.append({'c': n, 'f': CH[n]['file'][:-3], 'e': int(num), 't': title_text,
                      'lv': lv.replace('性价比', '') or '', 'ev': ev,
                      'm': money, 'tm': time, 'en': energy, 'sc': scopes,
                      'a': anchor(title), 'd': dispute, 'srcs': srcs, 'nr': noref})

json.dump(items, open('data/items.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('items:', len(items))
from collections import Counter
print('性价比:', Counter(i['lv'] for i in items))
print('证据:', Counter(i['ev'] for i in items))
print('钱:', Counter(i['m'] for i in items), '时间:', Counter(i['tm'] for i in items), '精力:', Counter(i['en'] for i in items))
print('口径:', Counter(s for i in items for s in i['sc']))
print('归一后 钱:', Counter(i['m'] for i in items), '\n时间:', Counter(i['tm'] for i in items), '\n精力:', Counter(i['en'] for i in items))
print('无口径:', sum(1 for i in items if not i['sc']))
print('无元信息条目:', sum(1 for i in items if not i['lv'] or not i['ev']))
print('无来源链接条目:', sum(1 for i in items if i['srcs'] == 0), '其中明写来源为无:', sum(1 for i in items if i['nr']))
print('来源链接总数:', sum(i['srcs'] for i in items), '| 来源≥3 条:', sum(1 for i in items if i['srcs'] >= 3))
