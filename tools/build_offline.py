# -*- coding: utf-8 -*-
"""拼成自包含单页 HTML -> dist/HowToWorkBetter.html

- 全部 51 章 444 条都在，条目按性价比分组
- 每条的「说人话 / 为什么·怎么做 / 来源 / 限制与争议」四块保留
- 来源里的裸链接转成可点的 <a>，离线也能点、URL 文本可见
- 封面：思源宋体标题 + 副标题 + 底部三行小字；封面不写章数/条数
- 目录列 51 章，锚点可点跳转
- 无任何外部资源（系统字体名），单文件自包含

也被 build_pdf.py / build_epub.py import 复用解析与渲染逻辑。
"""
import glob
import html
import os
import re

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_DIR = os.path.join(ROOT, 'book')
DIST_DIR = os.path.join(ROOT, 'dist')

BOOK_TITLE = '高性价比工作指南'
SUBTITLE = '写给普通打工人'
SITE_URL = 'https://nicecao.github.io/HowToWorkBetter/'
COVER_LINES = [
    '内容取自《高性价比工作指南》（CC BY 4.0）',
    '代码 MIT',
    SITE_URL,
]

SERIF = '"Source Han Serif SC","Noto Serif CJK SC","Noto Serif SC",serif'
SANS = '"Source Han Sans SC","Noto Sans CJK SC","Noto Sans SC",sans-serif'


# --------------------------------------------------------------------------
# 解析 book/*.md
# --------------------------------------------------------------------------
def _linkify(text):
    """把裸 URL 包成 markdown 自动链接 <url>，渲染后可点。"""
    return re.sub(
        r'(https?://[^\s<>()"\u201c\u201d\uff08\uff09\u3001\uff0c\u3002\uff1b\uff1a]+)',
        r'<\1>', text)


def md_to_html(text, xhtml=False):
    return markdown.markdown(
        _linkify(text),
        extensions=['extra', 'sane_lists'],
        output_format='xhtml' if xhtml else 'html')


def _split_meta(body):
    """从条目正文头部剥离 性价比/成本/口径/证据等级 等元信息行。"""
    meta, rest = [], list(body)
    while rest:
        s = re.sub(r'^>\s*', '', rest[0].strip())
        if re.match(r'^(性价比|成本|口径|证据等级)', s):
            meta.append(s)
            rest.pop(0)
            continue
        if not s:
            nxt = ''
            for x in rest[1:]:
                if x.strip():
                    nxt = re.sub(r'^>\s*', '', x.strip())
                    break
            if meta and re.match(r'^(性价比|成本|口径|证据等级)', nxt):
                rest.pop(0)
                continue
        break
    # 去掉尾部分隔线
    while rest and not rest[-1].strip():
        rest.pop()
    rest = [x for x in rest if not re.match(r'^\s*-{3,}\s*$', x)]
    # 列表块前补空行，保证被解析成 <ul>
    fixed = []
    for x in rest:
        if re.match(r'^\s*[-*] ', x) and fixed and fixed[-1].strip() and not re.match(r'^\s*[-*] ', fixed[-1]):
            fixed.append('')
        fixed.append(x)
    return meta, '\n'.join(fixed).strip()


def parse_chapter(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    n = int(os.path.basename(path)[:2])
    title, intro_lines = '', []
    groups, cur_group, cur_item = [], None, None

    def flush_item():
        nonlocal cur_item
        if cur_item is not None:
            groups[-1]['items'].append(cur_item)
            cur_item = None

    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            continue
        if line.startswith('## '):
            flush_item()
            cur_group = {'name': line[3:].strip(), 'items': []}
            groups.append(cur_group)
            continue
        if line.startswith('### '):
            flush_item()
            h = line[4:].strip()
            m = re.match(r'^(\d+)\.\s*(.*)$', h)
            eid, etitle = (m.group(1), m.group(2)) if m else ('', h)
            cur_item = {'id': eid, 'title': etitle, 'meta': [], 'body': '', 'raw': []}
            continue
        if re.match(r'^\s*-{3,}\s*$', line):
            continue
        if cur_item is not None:
            cur_item['raw'].append(line)
        elif cur_group is not None:
            pass  # 组内、条目前的零散文字忽略
        else:
            intro_lines.append(line)
    flush_item()

    for g in groups:
        for it in g['items']:
            it['meta'], it['body'] = _split_meta(it.pop('raw'))

    intro = ' '.join(x.strip() for x in intro_lines if x.strip())
    intro = re.sub(r'^\s*>\s*', '', intro).strip()
    return {'n': n, 'title': title, 'intro': intro, 'groups': groups}


def load_book():
    chapters = []
    for path in sorted(glob.glob(os.path.join(BOOK_DIR, '*.md'))):
        chapters.append(parse_chapter(path))
    return chapters


def chapter_anchor(n):
    return 'ch%02d' % n


# --------------------------------------------------------------------------
# 渲染
# --------------------------------------------------------------------------
CSS = """
:root { --ink:#1c1c1e; --ink2:#6b6b70; --line:#e8e8ec; --bg:#fff; --bg2:#f7f7f9;
  --accent:#e8730c; --accent-soft:#fdf1e5; --serif:%(serif)s; --sans:%(sans)s; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--bg); color:var(--ink); font:17px/1.85 var(--sans); }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.wrap { max-width:820px; margin:0 auto; padding:0 22px; }

.cover { max-width:820px; margin:0 auto; padding:120px 22px 96px; min-height:88vh;
  display:flex; flex-direction:column; justify-content:center; text-align:center; }
.cover .title { font-family:var(--serif); font-weight:700; font-size:52px; line-height:1.3;
  letter-spacing:.06em; margin:0 0 22px; }
.cover .sub { font-family:var(--serif); font-size:19px; color:var(--ink2); letter-spacing:.28em; margin:0; }
.cover .rule { width:64px; height:3px; background:var(--accent); margin:34px auto; border-radius:2px; }
.cover .foot { margin-top:auto; padding-top:80px; color:var(--ink2); font-size:13px; line-height:2; }
.cover .foot p { margin:0; }
.cover .foot .url { color:var(--accent); word-break:break-all; }

.toc { max-width:820px; margin:0 auto; padding:8px 22px 60px; }
.toc h2 { font-family:var(--serif); font-size:24px; border-bottom:2px solid var(--ink); padding-bottom:12px; margin:0 0 8px; }
.toc ol { list-style:none; counter-reset:c; margin:0; padding:0; }
.toc li { counter-increment:c; border-bottom:1px solid var(--line); }
.toc li a { display:flex; gap:12px; padding:11px 4px; color:var(--ink); }
.toc li a::before { content:counter(c); color:var(--ink2); font-variant-numeric:tabular-nums;
  min-width:1.9em; text-align:right; font-size:13px; }
.toc li a:hover { color:var(--accent); }

.chapter { max-width:820px; margin:0 auto; padding:44px 22px 8px; scroll-margin-top:20px; }
.chapter > h2 { font-family:var(--serif); font-weight:700; font-size:30px; line-height:1.42;
  letter-spacing:.01em; margin:0 0 14px; }
.chapter .intro { color:var(--ink2); font-size:15.5px; border-left:3px solid var(--accent-soft);
  padding-left:14px; margin:0 0 26px; }
.grp { font-family:var(--sans); font-size:14px; color:var(--accent); background:var(--accent-soft);
  display:inline-block; border-radius:6px; padding:3px 11px; margin:34px 0 6px; font-weight:600; }

.item { border-top:1px solid var(--line); padding:22px 0 8px; }
.item h3 { font-family:var(--serif); font-weight:700; font-size:20px; line-height:1.6;
  letter-spacing:.01em; margin:0 0 12px; }
.item h3 .no { color:var(--ink2); font-weight:500; margin-right:7px; font-variant-numeric:tabular-nums; }
.item .meta { background:var(--bg2); border-radius:10px; padding:9px 13px; font-size:13px;
  color:var(--ink2); margin:0 0 14px; line-height:1.8; }
.item p { margin:0 0 12px; }
.item strong { font-weight:600; }
.item ul { margin:0 0 12px; padding-left:24px; }
.item li { margin:0 0 6px; }
.item a { word-break:break-all; }

footer.doc { border-top:1px solid var(--line); max-width:820px; margin:60px auto 0;
  padding:20px 22px 80px; color:var(--ink2); font-size:13px; }
"""


def render_item(it):
    no = ('<span class="no">%s</span>' % html.escape(it['id'] + '.') if it['id'] else '')
    meta = ''
    if it['meta']:
        meta = '<p class="meta">%s</p>' % html.escape('　·　'.join(it['meta']))
    body = md_to_html(it['body'])
    return ('<article class="item">\n'
            '<h3 class="item-title">%s%s</h3>\n%s\n%s\n'
            '</article>' % (no, html.escape(it['title']), meta, body))


def render_chapter(ch):
    parts = ['<section class="chapter" id="%s">' % chapter_anchor(ch['n'])]
    parts.append('<h2 class="ch-title">%s</h2>' % html.escape(ch['title']))
    if ch['intro']:
        parts.append('<p class="intro">%s</p>' % html.escape(ch['intro']))
    for g in ch['groups']:
        parts.append('<h3 class="grp">%s</h3>' % html.escape(g['name']))
        for it in g['items']:
            parts.append(render_item(it))
    parts.append('</section>')
    return '\n'.join(parts)


def build():
    chapters = load_book()
    css = CSS % {'serif': SERIF, 'sans': SANS}
    toe = '\n'.join(
        '<li><a href="#%s">%s</a></li>' % (chapter_anchor(c['n']), html.escape(c['title']))
        for c in chapters)
    body = '\n'.join(render_chapter(c) for c in chapters)
    foot = ''.join('<p%s>%s</p>' % (' class="url"' if l.startswith('http') else '', html.escape(l))
                   for l in COVER_LINES)
    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{BOOK_TITLE}</title>
<meta name="description" content="{BOOK_TITLE}：{SUBTITLE}。逐条给出成本、收益与证据等级。">
<style>{css}</style>
</head>
<body>
<header class="cover" id="top">
  <h1 class="title">{BOOK_TITLE}</h1>
  <p class="sub">{SUBTITLE}</p>
  <div class="rule"></div>
  <div class="foot">{foot}</div>
</header>
<nav class="toc" id="toc">
  <h2>目录</h2>
  <ol>
{toe}
  </ol>
</nav>
<main>
{body}
</main>
<footer class="doc">
  <p>内容以 CC BY 4.0 授权；代码以 MIT 授权。法律、医疗、投资相关条目仅供参考，不构成建议。</p>
  <p>原文仓库：<a href="https://github.com/NiceCao/HowToWorkBetter">{SITE_URL}</a>　·　<a href="#top">回到顶部</a></p>
</footer>
</body>
</html>'''
    os.makedirs(DIST_DIR, exist_ok=True)
    out = os.path.join(DIST_DIR, 'HowToWorkBetter.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    n_items = sum(len(g['items']) for c in chapters for g in c['groups'])
    print('[offline] %s  章=%d 条=%d 字节=%d' % (out, len(chapters), n_items, os.path.getsize(out)))
    return out


if __name__ == '__main__':
    build()
