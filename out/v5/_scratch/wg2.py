#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Work helpers for the v5 merge task (work-guide-book). Talks to the DingTalk docs MCP gateway."""
import sys, json, time
sys.path.insert(0, '/home/ubuntu/projects/work-guide-50/scratch')
import gw  # noqa

IDX = json.load(open('/home/ubuntu/projects/work-guide-50/index.json', encoding='utf-8'))


def node_of(ch):
    return IDX[ch][1]


def fetch_jm(ch, retries=6):
    node = node_of(ch)
    for _ in range(retries):
        res = gw.call('get_document_content', {'nodeId': node, 'format': 'jsonml'})
        if res.get('jsonml'):
            return json.loads(res['jsonml'])
        time.sleep(2)
    raise RuntimeError(f'no jsonml for ch{ch}: {res}')


def blocks_of(jm):
    return jm[2:]


def leaves(node):
    out = []
    if isinstance(node, list):
        if len(node) >= 2 and isinstance(node[1], dict) and node[1].get('data-type') == 'leaf':
            if len(node) >= 3 and isinstance(node[2], str):
                out.append(node[2])
            return out
        for c in node[1:]:
            out.extend(leaves(c))
    return out


def text_of(b):
    return ''.join(leaves(b))


def uid(b):
    return b[1].get('uuid') if isinstance(b[1], dict) else None


# ---- block builders (uuid optional; omit for inserts) ----
def H3(title, uuid=None):
    a = {} if uuid is None else {'uuid': uuid}
    return ['h3', a, ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, title]]]


def META(text, uuid=None):
    a = {'blockquote': True} if uuid is None else {'blockquote': True, 'uuid': uuid}
    return ['p', a, ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, text]]]


def PARA(label, text, uuid=None):
    a = {} if uuid is None else {'uuid': uuid}
    runs = []
    if label:
        runs.append(['span', {'bold': True, 'data-type': 'leaf'}, label])
    runs.append(['span', {'data-type': 'leaf'}, text])
    return ['p', a, ['span', {'data-type': 'text'}] + runs]


def LABEL(text, uuid=None):
    a = {} if uuid is None else {'uuid': uuid}
    return ['p', a, ['span', {'data-type': 'text'}, ['span', {'bold': True, 'data-type': 'leaf'}, text]]]


def BULLET(text, list_id, uuid=None):
    a = {'list': {'listId': list_id, 'isOrdered': False, 'level': 0,
                  'listStyle': {'format': 'bullet', 'text': '\u25cf', 'align': 'left'}}}
    if uuid is not None:
        a['uuid'] = uuid
    return ['p', a, ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, text]]]


def HR(uuid=None):
    a = {} if uuid is None else {'uuid': uuid}
    return ['hr', a, ['span', {'data-type': 'text'}, ['span', {'data-type': 'leaf'}, '']]]


# ---- ops ----
def save_version(ch):
    return gw.call('save_doc_version', {'nodeId': node_of(ch)})


def update_block(ch, block_id, jm_block):
    j = json.dumps(jm_block, ensure_ascii=False)
    for attempt in range(3):
        try:
            r = gw.call('update_document_block', {'nodeId': node_of(ch), 'blockId': block_id,
                                                  'format': 'jsonml', 'jsonml': j})
            if r.get('success'):
                return r
            print('  update fail', block_id, r)
        except Exception as e:
            print('  update err', block_id, e)
        time.sleep(2)
    raise RuntimeError(f'update failed {ch} {block_id}')


def insert_after(ch, ref_block_id, jm_block):
    j = json.dumps(jm_block, ensure_ascii=False)
    for attempt in range(3):
        try:
            r = gw.call('insert_document_block', {'nodeId': node_of(ch), 'referenceBlockId': ref_block_id,
                                                  'where': 'after', 'format': 'jsonml', 'jsonml': j})
            if r.get('success') and r.get('blockId'):
                return r['blockId']
            print('  insert fail', r)
        except Exception as e:
            print('  insert err', e)
        time.sleep(2)
    raise RuntimeError(f'insert failed {ch} after {ref_block_id}')


def insert_entry_after(ch, ref_block_id, jm_blocks):
    """Insert a sequence of blocks after ref; returns list of new blockIds."""
    ids = []
    ref = ref_block_id
    for b in jm_blocks:
        nb = insert_after(ch, ref, b)
        ids.append(nb)
        ref = nb
    return ids
