# -*- coding: utf-8 -*-
"""一键入口：依次调 build_offline.py / build_pdf.py / build_epub.py，产物写到 dist/。

    python3 tools/build_dist.py
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)


def main():
    for name in ('build_offline.py', 'build_pdf.py', 'build_epub.py'):
        print('== run %s ==' % name)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, name)], cwd=ROOT)
        if r.returncode != 0:
            raise SystemExit('[build_dist] %s 失败 (exit=%d)' % (name, r.returncode))
    print('\n完成，产物在 dist/：')
    for f in ('HowToWorkBetter.pdf', 'HowToWorkBetter.epub', 'HowToWorkBetter.html'):
        p = os.path.join(ROOT, 'dist', f)
        print('  %-24s %s' % (f, ('%d 字节' % os.path.getsize(p)) if os.path.exists(p) else '缺失!'))


if __name__ == '__main__':
    main()
