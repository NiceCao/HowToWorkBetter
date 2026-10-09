# -*- coding: utf-8 -*-
"""把 book/*.md 渲染成可点的静态站点：ch/NN-章名.html（每条带 #eN 锚点）+ 首页链接改指本地页。"""
import glob, json, re, os, markdown

CH = {c['n']: c for c in json.load(open('data/chapters.json', encoding='utf-8'))}
BLOCKS = json.load(open('data/blocks.json', encoding='utf-8'))['blocks']
ITEMS = json.load(open('data/items.json', encoding='utf-8'))
CN = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
blk_of = {c: b['n'] for b in BLOCKS for c in b['chapters']}

CSS = '''
:root { --ink:#1c1c1e; --ink2:#6b6b70; --line:#e8e8ec; --bg:#fff; --bg2:#f7f7f9; --accent:#e8730c; --accent-soft:#fdf1e5; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; }
a { color:var(--accent); }
.bar { position:sticky; top:0; z-index:5; background:rgba(255,255,255,.95); backdrop-filter:saturate(1.4) blur(8px);
  border-bottom:1px solid var(--line); padding:9px 0; }
.bar .in { max-width:760px; margin:0 auto; padding:0 20px; display:flex; gap:12px; align-items:baseline; font-size:13.5px; color:var(--ink2); }
.bar a { text-decoration:none; }
.bar b { color:var(--ink); font-weight:600; }
.wrap { max-width:760px; margin:0 auto; padding:30px 20px 90px; }
h1 { font-size:26px; line-height:1.4; margin:6px 0 14px; }
.intro { color:var(--ink2); font-size:15px; border-left:3px solid var(--accent-soft); padding-left:14px; margin:0 0 26px; }
h2.grp { font-size:14px; color:var(--accent); background:var(--accent-soft); display:inline-block;
  border-radius:6px; padding:2px 10px; margin:34px 0 6px; font-weight:600; }
section.item { border-top:1px solid var(--line); padding:20px 0 6px; scroll-margin-top:64px; }
section.item h3 { font-size:18.5px; line-height:1.5; margin:0 0 12px; }
section.item h3 .no { color:var(--ink2); font-weight:500; margin-right:6px; font-variant-numeric:tabular-nums; }
.meta { background:var(--bg2); border-radius:12px; padding:12px 14px; font-size:13.5px; color:var(--ink2); margin:0 0 14px; }
.meta p { margin:0; line-height:1.7; }
section.item p { margin:0 0 12px; }
section.item strong { font-weight:600; }
section.item ul { margin:0 0 12px; padding-left:22px; }
section.item li { margin:0 0 6px; }
section.item a { word-break:break-all; }
.hl { background:#fff8e6; border-radius:3px; }
footer { border-top:1px solid var(--line); margin-top:40px; padding-top:18px; color:var(--ink2); font-size:13px; }
'''


def render(md_text):
    return markdown.markdown(md_text, extensions=['extra', 'sane_lists'])


def build_chapter(f):
    n = int(f[5:7])
    raw = open(f, encoding='utf-8').read()
    lines = raw.split('\n')
    out, buf, cur, head, group = [], [], None, '', None
    intro = ''
    i = 0
    # 切块
    segments = []
    for line in lines:
        if re.match(r'^### \d+\.', line) or re.match(r'^## ', line) or re.match(r'^# ', line):
            if cur is not None:
                segments.append((cur, '\n'.join(buf)))
            cur, buf = ('h1' if line.startswith('# ') else ('h2' if line.startswith('## ') else 'item')), [line]
        elif cur is None:
            segments.append(('pre', line))
        else:
            buf.append(line)
    if cur is not None:
        segments.append((cur, '\n'.join(buf)))

    body_parts = []
    for kind, text in segments:
        if kind == 'pre':
            continue
        text = text.strip('\n')
        if kind == 'h1':
            ls = [x for x in text.split('\n') if x.strip()]
            head = re.sub(r'^#\s*', '', ls[0]).strip()
            rest_h1 = '\n'.join(ls[1:]).strip()
            intro_txt = re.sub(r'^>\s*', '', rest_h1).replace('\n', ' ').strip()
            intro = f'<p class="intro">{intro_txt}</p>' if intro_txt else ''
            continue
        if kind == 'h2':
            g = re.sub(r'^##\s*', '', text).strip()
            body_parts.append(f'<h2 class="grp">{g}</h2>')
            continue
        # item
        lines2 = text.split('\n')
        h = re.sub(r'^###\s*', '', lines2[0]).strip()
        m = re.match(r'^(\d+)\.\s*(.*)$', h)
        eid, title = (m.group(1), m.group(2)) if m else ('0', h)
        rest = [x for x in lines2[1:]]
        while rest and not rest[0].strip():
            rest.pop(0)
        meta, body = [], []
        # 元信息：性价比 / 成本 / 口径 / 证据等级，可能写成多行也可能挤在一行
        while rest:
            s = re.sub(r'^>\s*', '', rest[0].strip())
            if re.match(r'^(性价比|成本|口径|证据等级)', s):
                meta.append(s)
                rest.pop(0)
                continue
            if not s:
                nxt = next((re.sub(r'^>\s*', '', x.strip()) for x in rest[1:] if x.strip()), '')
                if meta and re.match(r'^(性价比|成本|口径|证据等级)', nxt):
                    rest.pop(0)
                    continue
            break
        body = [x for x in rest if not re.match(r'^\s*-{3,}\s*$', x)]
        # 列表块前补空行，让 markdown 正确渲染成 <ul>
        fixed = []
        for x in body:
            if re.match(r'^\s*- ', x) and fixed and fixed[-1].strip() and not re.match(r'^\s*- ', fixed[-1]):
                fixed.append('')
            fixed.append(x)
        meta_html = '<div class="meta">' + ''.join(f'<p>{x}</p>' for x in meta) + '</div>' if meta else ''
        body_html = render('\n'.join(fixed).strip())
        body_parts.append(f'<section class="item" id="e{eid}">\n<h3><span class="no">{eid}.</span>{title}</h3>\n{meta_html}\n{body_html}\n</section>')

    items_n = sum(1 for it in ITEMS if it['c'] == n)
    b = blk_of.get(n)
    blk_txt = f"板块{CN[b-1]}·{next(x['name'] for x in BLOCKS if x['n']==b)}" if b else ''
    page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{head} · 高性价比工作指南</title>
<style>{CSS}</style></head><body>
<div class="bar"><div class="in"><a href="../index.html">← 返回检索</a><span>{blk_txt}</span><span>共 {items_n} 条</span></div></div>
<div class="wrap">
<h1>{head}</h1>
{intro}
{''.join(body_parts)}
<footer><p>本页内容以 CC BY 4.0 授权；法律、医疗、投资相关条目仅供参考，不构成建议。原文见 <a href="https://github.com/NiceCao/HowToWorkBetter">GitHub 仓库</a>。</p></footer>
</div></body></html>'''
    out_name = CH[n]['file'][:-3] + '.html'
    open(os.path.join('ch', out_name), 'w', encoding='utf-8').write(page)
    return out_name, len(page)


os.makedirs('ch', exist_ok=True)
tot = 0
for f in sorted(glob.glob('book/*.md')):
    name, size = build_chapter(f)
    tot += size
print('生成章节页:', len(glob.glob('ch/*.html')), '总字节:', tot)
