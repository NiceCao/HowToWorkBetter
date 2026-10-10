# -*- coding: utf-8 -*-
"""一键入口：依次调 build_offline.py / build_pdf.py / build_epub.py，产物写到 dist/。

    python3 tools/build_dist.py
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
# 后处理 PDF（书签 + 目录跳转）需要 pypdf，装在专用 venv 里
PDF_VENV = os.path.expanduser('~/.venvs/pdf/bin/python')


def main():
    for name in ('build_offline.py', 'build_pdf.py', 'build_epub.py'):
        print('== run %s ==' % name)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, name)], cwd=ROOT)
        if r.returncode != 0:
            raise SystemExit('[build_dist] %s 失败 (exit=%d)' % (name, r.returncode))
    # PDF 收尾：加书签（大纲）、目录页跳转、封面外链
    py = PDF_VENV if os.path.exists(PDF_VENV) else sys.executable
    print('== run add_pdf_links.py (%s) ==' % py)
    r = subprocess.run([py, os.path.join(TOOLS, 'add_pdf_links.py')], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit('[build_dist] add_pdf_links.py 失败 (exit=%d)' % r.returncode)
    print('\n完成，产物在 dist/：')
    for f in ('HowToWorkBetter.pdf', 'HowToWorkBetter.epub', 'HowToWorkBetter.html'):
        p = os.path.join(ROOT, 'dist', f)
        print('  %-24s %s' % (f, ('%d 字节' % os.path.getsize(p)) if os.path.exists(p) else '缺失!'))


if __name__ == '__main__':
    main()
