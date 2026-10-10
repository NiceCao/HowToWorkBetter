#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《高性价比工作指南》质检脚本（只用 Python 3 标准库，不装依赖）。

模式：

    python3 tools/check_book.py
        【默认】全书正文质检。逐条检查 book/*.md：
          ① 每条「性价比／成本／口径／证据等级」四项元信息是否齐全（允许写成一行）；
          ② 正文中文字符数是否 ≤800（不含标题行、不含元信息行），超出的列出字数；
          ③ 每章条目编号是否从 1 连续（缺号／重号／乱序都报）；
          ④ 是否有「说人话」块且该块 ≤120 字；
          ⑤ 是否有「来源：」块，且其中至少一条 http(s) 链接，或明写「未找到…官方数据」。
        报告写到 out/check-report.txt 并在终端打印摘要，退出码恒为 0（只报告，不阻断）。

    python3 tools/check_book.py --urls
        在默认质检之外，用 urllib 抽查所有来源链接的 HTTP 状态（超时 15 秒，只报结果不报错），
        按三类打到终端，供 .github/workflows/links.yml 读运行的 Summary：
          1. 确定失效——服务器明确回 404 / 410，链接真的没了，要换；
          2. 连不上——连接超时、DNS 失败或被拒，多半是政府网站挡了境外机房 IP，浏览器能开就不用管；
          3. 加密过旧——TLS 握手谈不拢，浏览器能开、脚本连不上，不用修。
        退出码恒为 0。--limit N 可只抽查前 N 条链接，本地试跑用。

    python3 tools/check_book.py --data
        校验 data/*.json 是否自洽：章节号连续、板块完整覆盖 50 章、条目字段与取值合法。
        这是本脚本早先的默认行为，现保留为 --data，有问题退出码 1。

字数口径：「中文字符数」指汉字（CJK 统一表意文字 U+4E00–U+9FFF），不含标点、数字、
字母和来源里的链接——这正是「中文字符」的字面含义，也避免把一长串 URL 算进正文。
"""
import glob
import json
import os
import re
import socket
import ssl
import sys
import time
import datetime
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, 'book')
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'out')
REPORT = os.path.join(OUT, 'check-report.txt')

# ======================= 目录正文质检（默认模式） =======================
MAX_ENTRY = 800            # 整条正文汉字数参考线（不是硬指标：字数只是提醒你检查，
                           # 判断标准是「读者能不能花最小精力一遍读懂并照做」，
                           # 某条真需要 900 字说清楚就让它超；压丢了关键步骤/条件/金额口径才是问题）
MAX_PLAIN = 120            # 说人话汉字数上限
URL_TIMEOUT = 15           # --urls 时单条链接超时（秒）

CJK = re.compile(r'[\u4e00-\u9fff]')
ENTRY_RE = re.compile(r'^###\s+(\d+)\.\s*(.+?)\s*$')
# 四行元信息允许被挤在一行里写成（全书约 8 条这样写），所以按标签匹配而不是按行数匹配。
META_KEYS = ['性价比', '成本', '口径', '证据等级']
META_LABEL_RE = re.compile(r'^(性价比|成本|口径|证据等级)\s*[：:]')
SRC_START_RE = re.compile(r'^>?\s*\*{0,2}来源\s*[：:]')
# 链接：到空白或中文标点为止；保留 ASCII 括号（DOI 里有，如 …(85)90042-5），
# 但排除全角括号和中文标点，避免把「（需在浏览器打开」这类说明吞进链接。
URL_RE = re.compile(r'https?://[^\s<>「」『』【】（），。；、""\'\'`]+')



def _is_none_src(src_txt: str) -> bool:
    """来源写成「无」的两种形式都算合规：同一行「来源：无」，或下一行列表项「- 无」。"""
    return bool(re.search(r'来源\s*[:：]\s*[-–—•*]?\s*无\s*[。.]?\s*(?:（[^）]{0,40}）)?\s*$',
                          re.sub(r'[\s*]+', ' ', src_txt or '')))
def clean_url(u):
    """削掉链接末尾粘上的标点，并去掉不成对的右括号。"""
    u = u.rstrip('.,;:!?，。；：、')
    while u.endswith(')') and u.count('(') < u.count(')'):
        u = u[:-1]
    return u


def cn_len(s):
    """中文字符数：只数汉字。"""
    return len(CJK.findall(s))


def is_meta_line(line):
    """这一行是不是「性价比/成本/口径/证据等级」元信息（含挤在一行里的写法）。"""
    s = line.strip().lstrip('*>').strip()
    if META_LABEL_RE.match(s):
        return True
    # 一行里同时出现两个以上键名，就是被挤在一行的元信息行
    return sum(k in line for k in META_KEYS) >= 2


def strip_tail(body):
    """去掉最后一条后面的「本章小结」尾巴和分隔线。"""
    for i, l in enumerate(body):
        if '本章小结' in l:
            body = body[:i]
            break
    while body and body[-1].strip() in ('---', ''):
        body = body[:-1]
    return body


def parse_entry(head_line, body):
    """把一个条目解析成检查所需的结构 + 问题清单。"""
    m = ENTRY_RE.match(head_line)
    if not m:
        raise ValueError('不是条目标题行：%r' % head_line)
    num = int(m.group(1))
    title = m.group(2).strip()
    body = strip_tail(body)

    plain_idx = next((i for i, l in enumerate(body) if '说人话' in l), None)
    region = body[:plain_idx] if plain_idx is not None else body

    issues = []  # 每项：(分类, 说明, 怎么改)

    # ① 四项元信息
    region_txt = '\n'.join(region)
    missing = [k for k in META_KEYS if k not in region_txt]
    if missing:
        issues.append((
            '缺元信息',
            '缺少：' + '、'.join(missing),
            '补齐「> 性价比：/成本：/口径：/证据等级：」四项（可写成一行，'
            '如「**性价比：…成本：…口径：…证据等级：…**」）',
        ))

    # ② 正文汉字数（不含标题行、不含元信息行）
    if plain_idx is not None:
        count_lines = [l for i, l in enumerate(body)
                       if not (i < plain_idx and is_meta_line(l))]
    else:
        count_lines = [l for l in body if not is_meta_line(l)]
    body_len = cn_len('\n'.join(count_lines))
    if body_len > MAX_ENTRY:
        issues.append((
            '超字数',
            '正文 %d 字，超过 %d（多 %d 字）' % (body_len, MAX_ENTRY, body_len - MAX_ENTRY),
            '按改稿标准 v2 压缩：撤掉中间小标题，内容并进「说人话」和「为什么/怎么做」两段，'
            '来源只留能直接证明本条的',
        ))

    # ④ 说人话（③ 编号连续性在章级处理）
    plain_len = None
    if plain_idx is None:
        issues.append(('缺说人话', '没有「说人话」块', '补一段「**说人话：**」，开门见结论，≤120 字'))
    else:
        pm = re.search(r'说人话\s*[：:]\s*\*{0,2}\s*(.*)$', body[plain_idx])
        ptxt = pm.group(1).strip() if pm else ''
        if not ptxt:  # 少数写法把正文放在下一行
            parts = []
            for l in body[plain_idx + 1:]:
                s = l.strip()
                if s == '' or s.startswith('**') or s.startswith('>') or s.startswith('#'):
                    break
                parts.append(s)
            ptxt = ''.join(parts)
        plain_len = cn_len(ptxt)
        if plain_len > MAX_PLAIN:
            issues.append((
                '说人话超长',
                '说人话 %d 字，超过 %d（多 %d 字）' % (plain_len, MAX_PLAIN, plain_len - MAX_PLAIN),
                '开门见结论，砍到 120 字内，别堆数字和背景',
            ))

    # ⑤ 来源
    si = next((i for i, l in enumerate(body) if SRC_START_RE.match(l.strip())), None)
    src_links = []
    if si is None:
        issues.append(('缺来源', '没有「来源：」块',
                       '补「**来源：**」，放 1–3 条能直接证明本条的官方来源；没有就写'
                       '「未找到直接相关的官方数据」') or _is_none_src(src_txt))
    else:
        blk = [body[si]]
        j = si + 1
        while j < len(body):
            s = body[j].strip()
            if s == '':
                j += 1
                continue
            if s.startswith('-'):
                blk.append(body[j])
                j += 1
                continue
            break
        src_txt = '\n'.join(blk)
        src_links = [clean_url(u) for u in URL_RE.findall(src_txt)]
        src_links = [u for u in src_links if u]
        if not src_links and '未找到' not in src_txt and not _is_none_src(src_txt):
            issues.append((
                '来源无据',
                '来源块既没有 http(s) 链接，也没有写「无」（或旧的「未找到…官方数据」）',
                '补一条能直接证明本条的官方来源，或按「没有能证明本条的官方来源」'
                '来源栏写「无」（或旧的「未找到…官方数据」）',
            ))

    return {
        'num': num,
        'title': title,
        'body_len': body_len,
        'plain_len': plain_len,
        'src_links': src_links,
        'issues': issues,
    }


def parse_chapter(path):
    text = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    lines = text.split('\n')
    h1 = lines[0].lstrip('# ').strip() if lines and lines[0].startswith('#') else ''
    heads = [i for i, l in enumerate(lines) if ENTRY_RE.match(l)]
    entries = []
    bounds = heads + [len(lines)]
    for k in range(len(heads)):
        entries.append(parse_entry(lines[heads[k]], lines[heads[k] + 1:bounds[k + 1]]))
    return h1, entries


def check_numbering(entries):
    """章内条号是否从 1 连续、有没有缺号/重号/乱序。返回问题文本列表。"""
    nums = [e['num'] for e in entries]
    problems = []
    seen = Counter(nums)
    dups = sorted(n for n, c in seen.items() if c > 1)
    expected = set(range(1, len(nums) + 1))
    missing = sorted(expected - set(nums))
    extra = sorted(set(nums) - expected)
    if dups:
        problems.append('重号：' + '、'.join(str(x) for x in dups))
    if missing:
        problems.append('缺号：' + '、'.join(str(x) for x in missing))
    if extra:
        problems.append('越界编号：' + '、'.join(str(x) for x in extra))
    if nums != sorted(nums):
        problems.append('条号没有按从小到大排列')
    return problems


def fmt_title(t, n=40):
    return t if len(t) <= n else t[:n] + '…'


def render_report(chapters, urls_result):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    n_ch = len(chapters)
    n_entries = sum(len(e) for _, e in chapters)

    over_entry, miss_meta, no_source, miss_plain, over_plain = [], [], [], [], []
    all_links = []
    for h1, entries in chapters:
        for e in entries:
            types = {i[0] for i in e['issues']}
            if '超字数' in types:
                over_entry.append(e)
            if '缺元信息' in types:
                miss_meta.append(e)
            if '来源无据' in types or '缺来源' in types:
                no_source.append(e)
            if '缺说人话' in types:
                miss_plain.append(e)
            if '说人话超长' in types:
                over_plain.append(e)
            all_links.extend(e['src_links'])
    uniq_links = sorted(set(all_links))

    L = []
    L.append('《高性价比工作指南》全书质检报告')
    L.append('生成时间：%s' % now)
    L.append('扫描范围：book/*.md，共 %d 章 %d 条' % (n_ch, n_entries))
    L.append('判定标准：改稿标准 v2（整条 ≤%d 字、说人话 ≤%d 字、来源只放能证明本条的）'
             % (MAX_ENTRY, MAX_PLAIN))
    L.append('字数口径：中文字符 = 汉字（CJK 统一表意文字），不含标点、数字、字母和链接')
    L.append('')
    L.append('=' * 68)
    L.append('一、总览')
    L.append('=' * 68)
    L.append('- 章数：%d' % n_ch)
    L.append('- 条目数：%d' % n_entries)
    L.append('- 正文超 %d 字的条目（提示，只为方便阅读，不是必须压到）：%d' % (MAX_ENTRY, len(over_entry)))
    L.append('- 缺元信息条目：%d' % len(miss_meta))
    L.append('- 无来源条目（无链接且未写「无」）：%d' % len(no_source))
    L.append('- 来源链接总数：%d（去重 %d）' % (len(all_links), len(uniq_links)))
    L.append('- 附：说人话缺失 %d 条、说人话超 %d 字 %d 条' % (len(miss_plain), MAX_PLAIN, len(over_plain)))
    L.append('')

    # 逐章明细：只列有问题的章节
    L.append('=' * 68)
    L.append('二、逐章明细（只列有问题的条目）')
    L.append('=' * 68)
    clean = 0
    for h1, entries in chapters:
        ch_issues = []
        num_prob = check_numbering(entries)
        for e in entries:
            if e['issues']:
                ch_issues.append((e['num'], e['title'], e['issues']))
        if not ch_issues and not num_prob:
            clean += 1
            continue
        L.append('')
        L.append('### %s' % h1)
        if num_prob:
            L.append('  · 章级编号问题：%s → 本章条号应从 1 开始、连续不重（按正文顺序重排）'
                     % '；'.join(num_prob))
        for num, title, issues in ch_issues:
            L.append('- 第%d条《%s》' % (num, fmt_title(title)))
            for cat, desc, fix in issues:
                L.append('  · [%s] %s' % (cat, desc))
                L.append('    → %s' % fix)
    L.append('')
    L.append('（其余 %d 章无问题）' % clean)
    L.append('')

    # 链接抽查
    if urls_result is not None:
        u = urls_result
        L.append('=' * 68)
        L.append('三、来源链接抽查（--urls，超时 %d 秒，只报结果不报错）' % URL_TIMEOUT)
        L.append('=' * 68)
        L.append('- 抽查去重链接：%d 条' % u['checked'])
        L.append('- 正常（HTTP 2xx/3xx）：%d 条' % len(u['ok']))
        L.append('- 确定失效（404/410）：%d 条' % len(u['dead']))
        L.append('- 连不上（超时/DNS/被拒等）：%d 条' % len(u['unreachable']))
        L.append('- 加密过旧（TLS 握手不兼容）：%d 条' % len(u['tls']))
        bad = u['dead'] + u['unreachable'] + u['tls']
        if bad:
            L.append('')
            L.append('非正常链接（最多列 60 条）：')
            for url, why in bad[:60]:
                L.append('  · %s  → %s' % (url, why))
            if len(bad) > 60:
                L.append('  …另有 %d 条' % (len(bad) - 60))
        L.append('')

    # 运行摘要（尾部）
    L.append('=' * 68)
    L.append('四、本次运行摘要')
    L.append('=' * 68)
    L.append('本次运行（%s）：' % now)
    L.append('- 章数 %d，条目数 %d' % (n_ch, n_entries))
    L.append('- 正文超 %d 字条目 %d 条（提示，不按错误算）；缺元信息条目 %d 条；无来源条目 %d 条'
             % (MAX_ENTRY, len(over_entry), len(miss_meta), len(no_source)))
    L.append('- 来源链接总数 %d 条，去重 %d 条' % (len(all_links), len(uniq_links)))
    L.append('- 说人话缺失 %d 条、超长 %d 条' % (len(miss_plain), len(over_plain)))
    if urls_result is not None:
        u = urls_result
        L.append('- 链接抽查：检查 %d 条，正常 %d 条，确定失效 %d 条，连不上 %d 条，加密过旧 %d 条'
                 % (u['checked'], len(u['ok']), len(u['dead']), len(u['unreachable']), len(u['tls'])))
    else:
        L.append('- 链接抽查：本次未开启（加 --urls 抽查来源链接）')
    L.append('')
    L.append('退出码：0（本脚本只报告，不阻断）')
    return '\n'.join(L), {
        'n_ch': n_ch, 'n_entries': n_entries,
        'over': len(over_entry), 'miss_meta': len(miss_meta),
        'no_source': len(no_source), 'links': len(all_links), 'uniq': len(uniq_links),
        'miss_plain': len(miss_plain), 'over_plain': len(over_plain),
    }


def collect_chapters():
    files = sorted(glob.glob(os.path.join(BOOK, '*.md')))
    return [parse_chapter(f) for f in files]


def collect_links(chapters):
    uniq, seen = [], set()
    for _, entries in chapters:
        for e in entries:
            for u in e['src_links']:
                if u not in seen:
                    seen.add(u)
                    uniq.append(u)
    return uniq


def check_url_once(u):
    """请求一次，返回 (分类, 说明)。分类：ok / dead / unreachable / tls。"""
    # 不校验证书：不少老政府站证书链不全，urllib 默认会直接拒连，浏览器却能开。
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(
            u, method='GET',
            headers={'User-Agent': 'Mozilla/5.0 (compatible; check_book.py)'})
        with urllib.request.urlopen(req, timeout=URL_TIMEOUT, context=ctx) as r:
            r.read(256)
            return 'ok', str(getattr(r, 'status', None) or r.getcode())
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return 'dead', 'HTTP %d' % e.code
        return 'unreachable', 'HTTP %d' % e.code
    except urllib.error.URLError as e:
        reason = e.reason
        if isinstance(reason, ssl.SSLError):
            return 'tls', 'TLS：%s' % str(reason)[:50]
        return 'unreachable', str(reason)[:60]
    except (socket.timeout, TimeoutError):
        return 'unreachable', '超时（%ds）' % URL_TIMEOUT
    except Exception as e:  # noqa: BLE001 —— 只报告，不让单条链接把脚本弄崩
        return 'unreachable', type(e).__name__


def check_url(u):
    """请求一条链接，返回 (url, 分类, 说明)。

    404/410 再复验一次：政府站受并发或风控影响会偶发假 404，而「确定失效」是要回去
    换地址的一档，误报代价高。两次都失效才判死。
    """
    cat, why = check_url_once(u)
    if cat == 'dead':
        time.sleep(0.6)
        cat, why = check_url_once(u)
    return u, cat, why


def run_urls(chapters, limit=None):
    urls = collect_links(chapters)
    if limit:
        urls = urls[:limit]
    ok, dead, unreachable, tls = [], [], [], []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(check_url, u): u for u in urls}
        for fut in as_completed(futs):
            u, cat, why = fut.result()
            if cat == 'ok':
                ok.append((u, why))
            elif cat == 'dead':
                dead.append((u, why))
            elif cat == 'tls':
                tls.append((u, why))
            else:
                unreachable.append((u, why))
    for lst in (ok, dead, unreachable, tls):
        lst.sort()
    return {'checked': len(urls), 'ok': ok, 'dead': dead, 'unreachable': unreachable, 'tls': tls}


# ======================= data/*.json 自洽校验（--data） =======================
VALID_LV = {'极高', '高', '一般'}
VALID_EV = {'A', 'B', 'C'}
VALID_SC = {'收入', '职业寿命', '职业自由', '时间精力'}
ITEM_FIELDS = ('c', 'f', 'e', 't', 'lv', 'ev', 'm', 'tm', 'en', 'sc', 'a', 'd')


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def check_data():
    chapters = load('chapters.json')
    blocks = load('blocks.json')['blocks']
    items = load('items.json')

    problems = []

    ns = [c['n'] for c in chapters]
    if ns != list(range(1, len(chapters) + 1)):
        problems.append('章号不是从 1 连续到 %d：%s' % (len(chapters), ns))
    for c in chapters:
        for k in ('n', 'h1', 'file', 'chars'):
            if k not in c:
                problems.append('第 %s 章缺字段 %s' % (c.get('n'), k))
        p = os.path.join(ROOT, 'book', c['file'])
        if not os.path.isfile(p):
            problems.append('第 %s 章的正文文件不存在：%s' % (c['n'], c['file']))

    covered = [n for b in blocks for n in b['chapters']]
    if sorted(covered) != sorted(ns):
        miss = sorted(set(ns) - set(covered))
        extra = sorted(set(covered) - set(ns))
        problems.append('板块没有完整覆盖全部章节（漏 %s；多 %s）' % (miss, extra))
    dup = [n for n, k in Counter(covered).items() if k > 1]
    if dup:
        problems.append('这些章被分进了多个板块：%s' % sorted(dup))

    bad = Counter()
    chap_set = set(ns)
    for it in items:
        for k in ITEM_FIELDS:
            if k not in it:
                bad['缺字段'] += 1
        if it.get('c') not in chap_set:
            bad['章号越界'] += 1
        if it.get('lv') not in VALID_LV:
            bad['性价比取值非法'] += 1
        if it.get('ev') not in VALID_EV:
            bad['证据等级取值非法'] += 1
        if any(s not in VALID_SC for s in it.get('sc', [])):
            bad['口径取值非法'] += 1
    for k, v in bad.items():
        problems.append('条目%s：%d 条' % (k, v))

    lv, ev = Counter(i.get('lv') for i in items), Counter(i.get('ev') for i in items)
    sc = Counter(s for i in items for s in i.get('sc', []))
    print('章节 %d 章，板块 %d 个，条目 %d 条' % (len(chapters), len(blocks), len(items)))
    print('性价比 极高/高/一般 = %d/%d/%d' % (lv['极高'], lv['高'], lv['一般']))
    print('证据 A/B/C = %d/%d/%d' % (ev['A'], ev['B'], ev['C']))
    print('口径 收入/职业寿命/职业自由/时间精力 = %d/%d/%d/%d'
          % (sc['收入'], sc['职业寿命'], sc['职业自由'], sc['时间精力']))

    if problems:
        print('\n发现 %d 个问题：' % len(problems))
        for p in problems:
            print('  - ' + p)
        return 1
    print('\n质检通过：data/*.json 自洽。')
    return 0


# ======================= 入口 =======================
def main():
    args = sys.argv[1:]

    if '--data' in args:
        return check_data()

    chapters = collect_chapters()

    urls_result = None
    if '--urls' in args:
        limit = None
        if '--limit' in args:
            try:
                limit = int(args[args.index('--limit') + 1])
            except (IndexError, ValueError):
                limit = None
        urls_result = run_urls(chapters, limit)
        # 供 .github/workflows/links.yml 读运行的 Summary（分类打到 stdout）
        u = urls_result
        print('抽查全书外链去重后 %d 条：' % u['checked'])
        print('\n1. 确定失效 %d 条（要换地址）：' % len(u['dead']))
        for url, why in u['dead']:
            print('   [%s] %s' % (why, url))
        print('2. 连不上 %d 条（多半是挡了境外 IP，浏览器能开就不用管）：' % len(u['unreachable']))
        for url, why in u['unreachable'][:40]:
            print('   %s —— %s' % (url, why))
        if len(u['unreachable']) > 40:
            print('   …… 其余 %d 条省略' % (len(u['unreachable']) - 40))
        print('3. 加密过旧 %d 条（老政府站，浏览器能开，不用修）：' % len(u['tls']))
        for url, why in u['tls'][:40]:
            print('   %s' % url)
        print('4. 正常 %d 条。' % len(u['ok']))
        print('')

    report, stats = render_report(chapters, urls_result)

    os.makedirs(OUT, exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(report)

    print('《高性价比工作指南》质检完成，报告：out/check-report.txt')
    print('章数 %d，条目数 %d' % (stats['n_ch'], stats['n_entries']))
    print('正文超 %d 字条目 %d 条（提示，不是错误）；缺元信息 %d 条；无来源 %d 条'
          % (MAX_ENTRY, stats['over'], stats['miss_meta'], stats['no_source']))
    print('来源链接总数 %d 条，去重 %d 条' % (stats['links'], stats['uniq']))
    print('说人话缺失 %d 条、超 %d 字 %d 条' % (stats['miss_plain'], MAX_PLAIN, stats['over_plain']))
    if urls_result is not None:
        u = urls_result
        print('链接抽查：检查 %d 条，正常 %d 条，确定失效 %d 条，连不上 %d 条，加密过旧 %d 条'
              % (u['checked'], len(u['ok']), len(u['dead']), len(u['unreachable']), len(u['tls'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
