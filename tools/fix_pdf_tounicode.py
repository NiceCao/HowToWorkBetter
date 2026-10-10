# -*- coding: utf-8 -*-
"""修 Chrome 打印 PDF 的文字层：把 ToUnicode CMap 里指到 Kangxi 部首 / CJK 部首补充
的码位改回对应汉字（画面不变，复制/检索能拿到正确的字）。

背景：Chrome（Skia）在 Noto CJK 这类同时编码了 Kangxi 部首的字体上，给共用 glyph
取最小码位，于是「人」→U+2F08（KANGXI RADICAL MAN）、「长」→U+2ED3。纯标准库实现：
Chrome 输出是 PDF-1.4 经典 xref 表、无对象流，因此可以解压 top-level 的 ToUnicode 流、
改码位、再重建 xref。
"""
import re
import sys
import unicodedata
import zlib

SUPPLEMENT = {  # U+2E80–U+2EFF 部首补充，NFKC 不管，手补实际用到的
    0x2E9F: '母', 0x2EA0: '民', 0x2EB6: '示', 0x2EBB: '民', 0x2EBF: '见',
    0x2EC5: '见', 0x2EC6: '角', 0x2EC9: '贝', 0x2ECB: '车', 0x2ED3: '长',
    0x2ED4: '门', 0x2ED8: '马', 0x2EDA: '页', 0x2EDB: '风', 0x2EDD: '食',
    0x2EE2: '马', 0x2EE3: '骨', 0x2EE4: '黄', 0x2EE5: '艹', 0x2EE7: '氵',
    0x2EE8: '麦', 0x2EE9: '阝', 0x2EEC: '齐', 0x2EEF: '刂', 0x2EF0: '龙',
    0x2EF2: '讠', 0x2EF3: '阝',
}


def _fix_cp(cp):
    if 0x2E80 <= cp <= 0x2FDF:
        ch = unicodedata.normalize('NFKC', chr(cp))
        if ch != chr(cp) and len(ch) == 1:
            return ch
        return SUPPLEMENT.get(cp)
    return None


def _conv_hex(hexs, only_first=False):
    cps = [int(hexs[i:i + 4], 16) for i in range(0, len(hexs), 4)]
    out, changed = [], False
    for i, cp in enumerate(cps):
        rep = _fix_cp(cp) if (i == 0 or not only_first) else None
        if rep is not None:
            out.append(rep)
            changed = True
        else:
            out.append(chr(cp))
    return ''.join(''.join('%04X' % ord(c) for c in out)), changed


_re_bfrange = re.compile(r'^\s*<([0-9A-Fa-f]{2,8})>\s*<([0-9A-Fa-f]{2,8})>\s*<([0-9A-Fa-f]{2,8})>\s*$')
_re_bfchar = re.compile(r'^\s*<([0-9A-Fa-f]{2,8})>\s*<([0-9A-Fa-f]{2,8})>\s*$')


def patch_cmap(data: bytes) -> bytes:
    text = data.decode('latin-1')
    out, changed = [], False
    for line in text.split('\n'):
        m = _re_bfrange.match(line)
        if m and m.group(3) and len(m.group(3)) == 4:
            newdst, ch = _conv_hex(m.group(3), only_first=True)
            if ch:
                changed = True
            line = '<%s> <%s> <%s>' % (m.group(1), m.group(2), newdst)
        else:
            m = _re_bfchar.match(line)
            if m and m.group(2) and len(m.group(2)) <= 8 and len(m.group(2)) % 4 == 0:
                newdst, ch = _conv_hex(m.group(2))
                if ch:
                    changed = True
                line = '<%s> <%s>' % (m.group(1), newdst)
        out.append(line)
    if not changed:
        return data
    return '\n'.join(out).encode('latin-1')


_OBJ_RE = re.compile(rb'(?m)^(\d+)\s+(\d+)\s+obj\b')
_LEN_RE = re.compile(rb'/Length\s+(?:\d+\s+\d+\s+R|\d+)')
_END_OBJ = b'endobj'


def _iter_objects(data):
    pos = 0
    while True:
        m = _OBJ_RE.search(data, pos)
        if not m:
            return
        s = data.find(b'stream', m.end())
        e = data.find(_END_OBJ, m.end())
        if s != -1 and (e == -1 or s < e):
            es = data.find(b'endstream', s)
            e = data.find(_END_OBJ, es if es != -1 else s)
        if e == -1:
            return
        end = e + len(_END_OBJ)
        yield int(m.group(1)), int(m.group(2)), m.start(), data[m.start():end]
        pos = end


def _patch_object(body: bytes):
    """返回修好的对象字节；不需要改的返回原样。"""
    si = body.find(b'stream')
    if si == -1:
        return body
    dict_part = body[:si]
    after = body[si + 6:]
    if after.startswith(b'\r\n'):
        after = after[2:]
    elif after.startswith(b'\n'):
        after = after[1:]
    ei = after.find(b'endstream')
    if ei == -1:
        return body
    raw = after[:ei]
    if raw.endswith(b'\n'):
        raw = raw[:-1]
    if raw.endswith(b'\r'):
        raw = raw[:-1]
    flate = b'FlateDecode' in dict_part
    if flate:
        try:
            dec = zlib.decompress(raw)
        except zlib.error:
            return body
    else:
        dec = raw
    if b'begincmap' not in dec:
        return body
    new = patch_cmap(dec)
    if new == dec:
        return body
    payload = zlib.compress(new, 9) if flate else new
    dict_part = _LEN_RE.sub(b'/Length %d' % len(payload), dict_part, count=1)
    return dict_part.rstrip() + b'\nstream\n' + payload + b'\nendstream\nendobj'


def fix_pdf(path):
    data = open(path, 'rb').read()
    header = data[:data.find(b'\n', data.find(b'\n') + 1) + 1]  # 含二进制注释的两行头
    objs = []
    for num, gen, start, body in _iter_objects(data):
        objs.append((num, gen, _patch_object(body)))
    maxnum = max((o[0] for o in objs), default=0)

    out = bytearray(header)
    offsets = {}
    for num, gen, body in sorted(objs, key=lambda x: x[0]):
        offsets[num] = len(out)
        out += body
        if not out.endswith(b'\n'):
            out += b'\n'

    tpos = data.rfind(b'trailer')
    trailer = data[tpos + len(b'trailer'):].split(b'startxref')[0].strip()
    trailer = re.sub(rb'/Size\s+\d+', b'/Size %d' % (maxnum + 1), trailer, count=1)
    if b'/Size' not in trailer:
        trailer = trailer[:-2] + b'\n/Size %d>>' % (maxnum + 1)

    xref = len(out)
    out += b'xref\n0 %d\n' % (maxnum + 1)
    out += b'0000000000 65535 f \n'
    for n in range(1, maxnum + 1):
        if n in offsets:
            out += b'%010d 00000 n \n' % offsets[n]
        else:
            out += b'0000000000 65535 f \n'
    out += b'trailer\n' + trailer + b'\nstartxref\n%d\n%%%%EOF\n' % xref

    open(path, 'wb').write(bytes(out))
    return len(objs)


if __name__ == '__main__':
    print('objects rewritten:', fix_pdf(sys.argv[1]))
