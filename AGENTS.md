# AGENTS.md

这个仓库是《高性价比工作指南》的正文（50 章、416 条）。

- **改这本书**（增删条目、改正文、动脚本）：规则全在 [docs/改稿标准-v2-精简与引用.md](docs/改稿标准-v2-精简与引用.md)，先读完再动手。
- **用这本书回答问题**（该不该去、两个 offer 怎么比、被欠薪怎么办、要不要跳槽、社保怎么补）：按 [skills/work-guide/SKILL.md](skills/work-guide/SKILL.md) 执行，先查条目再答，每条注明出自第几章第几条；装到别处去用的办法见 [skills/work-guide/README.md](skills/work-guide/README.md)。
- **站点**由 `build_index.py`（生成 `index.html`）和 `build_site.py`（生成 `ch/*.html`）产出：**别手改 `index.html` 和 `ch/*.html`**，改正文后按这个顺序重跑：
  `python3 tools/build_entries.py`（重建 `data/entries.json`，检索页的条数统计靠它，漏跑就会显示过期条数）→ `python3 build_items.py` → `python3 build_index.py` → `python3 build_site.py` → `python3 build_readme.py` → `python3 tools/build_refs.py`。
- 图（`og.png`）由 `og.html` 渲染：`google-chrome --headless --no-sandbox --hide-scrollbars --force-device-scale-factor=2 --window-size=1200,630 --screenshot=og.png og.html`。标题用思源宋体、正文用思源黑体（`fonts-noto-cjk`/`fonts-noto-cjk-extra`），图上**不写条数/章数**，避免内容一变就要重做图。
