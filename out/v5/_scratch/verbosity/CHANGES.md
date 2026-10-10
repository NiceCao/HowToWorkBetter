# 说人话瘦身 变更记录（ch39/41/42/43，7 条）

工作目录：/home/ubuntu/projects/work-guide-book
钉钉文档 nodeId 见 /home/ubuntu/projects/work-guide-50/index.json
每章改前已 save_doc_version。

| 章·条 | blockId | 改前(字) | 改后(字) | 回退版本 |
|---|---|---|---|---|
| 第39章 第1条 | mv15wtrcgk0b6jjd0ep | 146 | 93 | 85 |
| 第41章 第8条 | mv167cb123gjfcmo1f8 | 123 | 90 | 77 |
| 第42章 第1条 | mv163hnzlwygumy0339 | 134 | 72 | 90 |
| 第42章 第4条 | mv162m648k2e5swnk5m | 176 | 108 | 90 |
| 第42章 第8条 | mv1628645ylbaaq2v55 | 182 | 111 | 90 |
| 第43章 第1条 | mv165ooczsp4adbdn7q | 140 | 107 | 100 |
| 第43章 第2条 | mv165djj2x16zqf9fy7 | 122 | 110 | 100 |

说明：
- 改动方式：就地改 update_document_block(jsonml)，只替换「说人话：」加粗标签后的正文叶子，「说人话：」加粗标签原样保留；未用 overwrite；未改标题、来源及其它块。
- 移入「为什么/怎么做」的一处：第42章第8条把「第八条不得贿赂对象清单」前插进该条「为什么、怎么做」(idx75, blockId mv162865zeko41fcvrs)；其余 6 条被砍的细节本就在同条「为什么/怎么做」里，故未重复新增。
- 复读校验：7 条正文均 ≤120 字，加粗标签全部保留；各章块数不变（39=141,41=149,42=113,43=163）。
- 导出：get_document_content(format='markdown') 原样覆盖写回 out/v5/ch{39,41,42,43}.md。

回退：revert_doc_version nodeId=<章> savedVersion=<上表回退版本>。
