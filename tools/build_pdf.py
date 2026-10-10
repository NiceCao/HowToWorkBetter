# -*- coding: utf-8 -*-
"""生成 A4 打印用 HTML -> 调 google-chrome --print-to-pdf -> dist/HowToWorkBetter.pdf

- A4、页边距 18mm、字号 10.5pt、行高 1.65
- 章名用宋体、正文用黑体
- 封面页 + 目录页（51 章）+ 每章另起一页
- 长链接/表格不溢出（word-break / table-layout:fixed）
"""
import html
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_offline as B  # noqa: E402
from fix_pdf_tounicode import fix_pdf  # noqa: E402

SCRATCH = '/home/ubuntu/.hermes/cache/scratch'
DIST = B.DIST_DIR

PRINT_CSS = """
:root { --serif:%(serif)s; --sans:%(sans)s; }
* { box-sizing:border-box; }
@page { size:A4; margin:18mm; }
html, body { margin:0; padding:0; }
body { font-family:var(--sans); font-size:10.5pt; line-height:1.65; color:#1c1c1e; }
a { color:#b85c00; text-decoration:none; word-break:break-all; overflow-wrap:anywhere; }
p { margin:0 0 .55em; }
ul { margin:0 0 .6em; padding-left:1.4em; }
li { margin:0 0 .25em; }
h1,h2,h3,h4 { page-break-after:avoid; }

.cover { height:245mm; display:flex; flex-direction:column; justify-content:center;
  text-align:center; page-break-after:always; }
.cover .title { font-family:var(--serif); font-weight:700; font-size:40pt; letter-spacing:.08em; margin:0 0 24pt; }
.cover .sub { font-family:var(--serif); font-size:15pt; color:#6b6b70; letter-spacing:.32em; margin:0; }
.cover .rule { width:70pt; height:3pt; background:#e8730c; margin:34pt auto; }
.cover .foot { margin-top:150pt; color:#6b6b70; font-size:9.5pt; line-height:2; }
.cover .foot p { margin:0; }

.toc { page-break-after:always; }
.toc h2 { font-family:var(--serif); font-size:20pt; border-bottom:2pt solid #1c1c1e; padding-bottom:8pt; margin:0 0 4pt; }
.toc ol { list-style:none; margin:0; padding:0; }
.toc li { border-bottom:.5pt solid #e8e8ec; }
.toc a { display:flex; gap:10pt; padding:5.4pt 2pt; color:#1c1c1e; }
.toc a .n { color:#6b6b70; min-width:2.4em; text-align:right; font-size:9pt; }

.chapter { page-break-before:always; }
.chapter > h2 { font-family:var(--serif); font-weight:700; font-size:21pt; line-height:1.4; margin:0 0 10pt; }
.chapter .intro { color:#6b6b70; font-size:10pt; border-left:2.5pt solid #fdf1e5; padding-left:10pt; margin:0 0 14pt; }
.grp { display:inline-block; font-size:9.5pt; font-weight:600; color:#b85c00; background:#fdf1e5;
  border-radius:4pt; padding:2.5pt 9pt; margin:16pt 0 4pt; page-break-after:avoid; }

.item { border-top:.5pt solid #e8e8ec; padding:10pt 0 2pt; page-break-inside:auto; }
.item h3 { font-family:var(--serif); font-weight:700; font-size:13pt; line-height:1.5; margin:0 0 7pt; }
.item h3 .no { color:#6b6b70; font-weight:500; margin-right:5pt; }
.item .meta { background:#f7f7f9; border-radius:5pt; padding:5pt 9pt; font-size:9pt; color:#6b6b70; margin:0 0 8pt; }
.item strong { font-weight:600; }
table { width:100%%; border-collapse:collapse; table-layout:fixed; margin:0 0 .6em; }
th, td { border:.5pt solid #d9d9de; padding:4pt 6pt; font-size:9pt; word-break:break-all; vertical-align:top; }

footer.doc { border-top:.5pt solid #e8e8ec; margin-top:16pt; padding-top:8pt; color:#6b6b70; font-size:9pt; }
"""


def render_chapter_print(ch):
    parts = ['<section class="chapter">']
    parts.append('<h2>%s</h2>' % html.escape(ch['title']))
    if ch['intro']:
        parts.append('<p class="intro">%s</p>' % html.escape(ch['intro']))
    for g in ch['groups']:
        parts.append('<h3 class="grp">%s</h3>' % html.escape(g['name']))
        for it in g['items']:
            no = ('<span class="no">%s</span>' % html.escape(it['id'] + '.') if it['id'] else '')
            meta = ('<p class="meta">%s</p>' % html.escape('　·　'.join(it['meta']))) if it['meta'] else ''
            parts.append('<article class="item"><h3>%s%s</h3>%s\n%s\n</article>'
                         % (no, html.escape(it['title']), meta, B.md_to_html(it['body'])))
    parts.append('</section>')
    return '\n'.join(parts)


def build_print_html(chapters, out_path):
    css = PRINT_CSS % {'serif': B.SERIF, 'sans': B.SANS}
    foot = ''.join('<p>%s</p>' % html.escape(l) for l in B.COVER_LINES)
    toc = '\n'.join(
        '<li><a href="#%s"><span class="n">%d</span><span>%s</span></a></li>'
        % (B.chapter_anchor(c['n']), c['n'], html.escape(c['title'])) for c in chapters)
    body = '\n'.join(render_chapter_print(c) for c in chapters)
    page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{B.BOOK_TITLE}</title>
<style>{css}</style></head><body>
<header class="cover">
  <h1 class="title">{B.BOOK_TITLE}</h1>
  <p class="sub">{B.SUBTITLE}</p>
  <div class="rule"></div>
  <div class="foot">{foot}</div>
</header>
<nav class="toc"><h2>目录</h2><ol>
{toc}
</ol></nav>
<main>
{body}
</main>
<footer class="doc"><p>内容以 CC BY 4.0 授权；代码以 MIT 授权。法律、医疗、投资相关条目仅供参考，不构成建议。</p></footer>
</body></html>'''
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page)
    return out_path


def build():
    chapters = B.load_book()
    os.makedirs(SCRATCH, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)
    src = os.path.join(SCRATCH, 'work-guide-print.html')
    build_print_html(chapters, src)
    out = os.path.join(DIST, 'HowToWorkBetter.pdf')
    cmd = [
        'google-chrome', '--headless', '--no-sandbox', '--disable-gpu',
        '--disable-dev-shm-usage', '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw', '--virtual-time-budget=30000',
        '--print-to-pdf=' + out, 'file://' + src,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(out):
        sys.stderr.write(r.stdout + '\n' + r.stderr + '\n')
        raise SystemExit('[pdf] 生成失败')
    n_obj = fix_pdf(out)  # 修 ToUnicode：把 Kangxi 部首码位改回汉字
    n_items = sum(len(g['items']) for c in chapters for g in c['groups'])
    print('[pdf] %s  章=%d 条=%d 对象=%d 字节=%d'
          % (out, len(chapters), n_items, n_obj, os.path.getsize(out)))
    return out


if __name__ == '__main__':
    build()
