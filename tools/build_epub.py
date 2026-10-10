# -*- coding: utf-8 -*-
"""生成 EPUB3 -> dist/HowToWorkBetter.epub

自己写 zip 结构：
- mimetype 必须是第一个条目且不压缩（ZIP_STORED）
- META-INF/container.xml
- OEBPS/content.opf
- OEBPS/nav.xhtml（目录，51 章可点）
- OEBPS/cover.xhtml（封面页）
- OEBPS/chNN.xhtml（每章一个）
- OEBPS/style.css
"""
import html
import os
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_offline as B  # noqa: E402

DIST = B.DIST_DIR
BOOK_UUID = 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, B.SITE_URL + B.BOOK_TITLE))

STYLE = """
:root { --serif:%(serif)s; --sans:%(sans)s; }
body { font-family:var(--sans); line-height:1.7; color:#1c1c1e; margin:0 5%%; }
h1,h2,h3 { font-family:var(--serif); line-height:1.45; }
h1.ch-title { font-weight:700; font-size:1.6em; margin:.4em 0 .5em; }
p.intro { color:#6b6b70; font-size:.92em; border-left:3px solid #fdf1e5; padding-left:.7em; margin:0 0 1.2em; }
h2.grp { display:inline-block; font-size:.86em; font-weight:600; color:#b85c00; background:#fdf1e5;
  border-radius:4px; padding:.15em .7em; margin:1.6em 0 .3em; }
article.item { border-top:1px solid #e8e8ec; padding:1em 0 .3em; }
article.item h3 { font-weight:700; font-size:1.12em; margin:0 0 .6em; }
article.item h3 .no { color:#6b6b70; font-weight:500; margin-right:.4em; }
p.meta { background:#f7f7f9; border-radius:8px; padding:.5em .8em; font-size:.82em; color:#6b6b70; margin:0 0 .9em; }
a { color:#b85c00; text-decoration:none; word-break:break-all; }
p { margin:0 0 .8em; }
ul { margin:0 0 .9em; padding-left:1.4em; }
li { margin:0 0 .3em; }
table { width:100%%; border-collapse:collapse; table-layout:fixed; }
th, td { border:1px solid #d9d9de; padding:.35em .5em; font-size:.86em; word-break:break-all; vertical-align:top; }

.cover { text-align:center; margin-top:30%%; }
.cover .title { font-family:var(--serif); font-weight:700; font-size:2.4em; letter-spacing:.08em; margin:0 0 1em; }
.cover .sub { font-family:var(--serif); font-size:1.1em; color:#6b6b70; letter-spacing:.3em; margin:0; }
.cover .rule { width:64px; height:3px; background:#e8730c; margin:2.4em auto; }
.cover .foot { color:#6b6b70; font-size:.82em; line-height:2; margin-top:18em; }
.cover .foot p { margin:0; }
.cover .url { color:#b85c00; }
nav ol { padding-left:1.4em; }
nav li { margin:.35em 0; }
"""


def xhtml_doc(title, body, css_href='style.css'):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<link rel="stylesheet" type="text/css" href="{css_href}"/>
</head>
<body>
{body}
</body>
</html>
'''


def render_cover():
    foot = ''.join('<p%s>%s</p>' % (' class="url"' if l.startswith('http') else '', html.escape(l))
                   for l in B.COVER_LINES)
    body = (f'<section class="cover">\n'
            f'<h1 class="title">{html.escape(B.BOOK_TITLE)}</h1>\n'
            f'<p class="sub">{html.escape(B.SUBTITLE)}</p>\n'
            f'<div class="rule"></div>\n'
            f'<div class="foot">{foot}</div>\n</section>')
    return xhtml_doc(B.BOOK_TITLE, body)


def render_nav(chapters):
    items = '\n'.join('<li><a href="ch%02d.xhtml">%s</a></li>' % (c['n'], html.escape(c['title']))
                      for c in chapters)
    body = ('<nav epub:type="toc" id="toc">\n<h1>目录</h1>\n<ol>\n%s\n</ol>\n</nav>' % items)
    return xhtml_doc('目录', body)


def render_chapter(ch):
    parts = ['<h1 class="ch-title">%s</h1>' % html.escape(ch['title'])]
    if ch['intro']:
        parts.append('<p class="intro">%s</p>' % html.escape(ch['intro']))
    for g in ch['groups']:
        parts.append('<h2 class="grp">%s</h2>' % html.escape(g['name']))
        for it in g['items']:
            no = ('<span class="no">%s</span>' % html.escape(it['id'] + '.') if it['id'] else '')
            meta = ('<p class="meta">%s</p>' % html.escape('　·　'.join(it['meta']))) if it['meta'] else ''
            parts.append('<article class="item">\n<h3>%s%s</h3>\n%s\n%s\n</article>'
                         % (no, html.escape(it['title']), meta, B.md_to_html(it['body'], xhtml=True)))
    return xhtml_doc(ch['title'], '\n'.join(parts))


CONTAINER = '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''


def build_opf(chapters):
    modified = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="style.css" media-type="text/css"/>',
        '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    ]
    for c in chapters:
        manifest.append('<item id="ch%02d" href="ch%02d.xhtml" media-type="application/xhtml+xml"/>'
                        % (c['n'], c['n']))
    spine = ['<itemref idref="cover"/>', '<itemref idref="nav"/>']
    for c in chapters:
        spine.append('<itemref idref="ch%02d"/>' % c['n'])
    return f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="zh-CN">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{BOOK_UUID}</dc:identifier>
    <dc:title>{html.escape(B.BOOK_TITLE)}</dc:title>
    <dc:language>zh-CN</dc:language>
    <dc:creator>NiceCao</dc:creator>
    <dc:rights>内容 CC BY 4.0；代码 MIT</dc:rights>
    <dc:source>{B.SITE_URL}</dc:source>
    <meta property="dcterms:modified">{modified}</meta>
  </metadata>
  <manifest>
    {'  '.join(manifest)}
  </manifest>
  <spine>
    {'  '.join(spine)}
  </spine>
</package>
'''


def build():
    chapters = B.load_book()
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, 'HowToWorkBetter.epub')

    files = [('OEBPS/style.css', STYLE % {'serif': B.SERIF, 'sans': B.SANS}),
             ('OEBPS/cover.xhtml', render_cover()),
             ('OEBPS/nav.xhtml', render_nav(chapters))]
    for c in chapters:
        files.append(('OEBPS/ch%02d.xhtml' % c['n'], render_chapter(c)))

    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        # mimetype 必须第一个且不压缩
        info = zipfile.ZipInfo('mimetype', date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, 'application/epub+zip')
        zf.writestr('META-INF/container.xml', CONTAINER)
        zf.writestr('OEBPS/content.opf', build_opf(chapters))
        for name, content in files:
            zf.writestr(name, content)

    n_items = sum(len(g['items']) for c in chapters for g in c['groups'])
    n_xhtml = sum(1 for n, _ in files if n.endswith('.xhtml'))
    print('[epub] %s  章=%d 条=%d xhtml=%d 字节=%d'
          % (out, len(chapters), n_items, n_xhtml, os.path.getsize(out)))
    return out


if __name__ == '__main__':
    build()
