# -*- coding: utf-8 -*-
"""生成《高性价比工作指南》导航页 index.html（自包含，无外部依赖）"""
import json, html

ch = {c['n']: c for c in json.load(open('data/chapters.json', encoding='utf-8'))}
entries = json.load(open('data/entries.json', encoding='utf-8'))

# ---- 按阶段 ----
stages = [
    ("还没入行：先把方向选对", "这时候选错，后面要用几年去纠正。先看行业、城市、岗位类型，再挑公司。",
     [1, 4, 5, 6, 7, 3, 2, 8]),
    ("拿到 offer：把条件谈清楚", "钱、合同、社保、奖金，入职前能改的都在这时候改。",
     [9, 41, 10, 11, 12, 16]),
    ("入职前 90 天：活下来、站稳", "先弄清规则、做出第一件能看见的成果，别急着比工资。",
     [45, 30, 19, 20, 21, 22, 18]),
    ("站稳后的 1–3 年：把位置做厚", "让决定你晋升的人知道你在做什么，同时别把精力耗在内斗上。",
     [25, 26, 23, 24, 35, 17, 29, 27, 28]),
    ("开始带人：夹在中间怎么当", "中层是信息、责任和人的枢纽，三组关系都要处理。",
     [31, 32, 33, 34, 38]),
    ("遇到风险：被裁、想跳、被欺负", "这类事都有法定流程和时限，按顺序办比情绪化处理有用。",
     [36, 13, 14, 46, 47, 43, 42, 48, 44]),
    ("长期与兜底：身体、退路、老后", "把健康、第二收入和退休待遇提前几年安排好。",
     [49, 39, 15, 40, 50]),
]

# ---- 按职业 ----
roles = [
    ("销售 / 市场 / 商务", "把业绩和动作变成可核对的数字，提成算法写进合同。",
     [32, 9, 12, 26, 24]),
    ("产品 / 技术 / 运营", "把日常动作做成可复核的方法，选清专家线还是管理线。",
     [33, 35, 23, 38, 18]),
    ("HR / 财务 / 法务 / 行政", "后台的价值在风险与效率，守住合规底线。",
     [34, 41, 42, 16, 44]),
    ("管理岗 / 中层", "对上对齐目标，对下定规则，对平级找共同利益。",
     [31, 25, 19, 20, 29]),
    ("体制内 / 考公", "算清收入与稳定性的实际差距，盯住社保与退休待遇。",
     [7, 10, 49]),
    ("应届生 / 实习生", "前两年先摸清规则、做出成果、处好关系。",
     [30, 45, 9, 41]),
    ("蓝领 / 产线 / 服务业", "这一块内容正在筹备（进厂、工地、骑手、仓储、餐饮）。", []),
]

def chlink(n, text=None):
    c = ch[n]
    return f'<a class="ch" href="book/{c["file"]}">{text or ("第 %d 章" % n)}</a>'

def stage_card(title, desc, nums):
    inner = ""
    for n in sorted(nums):
        c = ch[n]
        short = c['h1'].split('：', 1)[-1]
        inner += f'<li><a href="book/{c["file"]}"><b>{n:02d}</b> {html.escape(short)}</a></li>'
    return f'''<section class="card">
      <h3>{html.escape(title)}</h3>
      <p class="desc">{html.escape(desc)}</p>
      <ul class="chs">{inner}</ul>
    </section>'''

def role_card(title, desc, nums):
    if nums:
        chips = " ".join(chlink(n, f'{n:02d}') for n in nums)
    else:
        chips = '<span class="soon">筹备中</span>'
    return f'''<section class="rcard">
      <h3>{html.escape(title)}</h3>
      <p class="desc">{html.escape(desc)}</p>
      <p class="chips">{chips}</p>
    </section>'''

# ---- 全书目录 ----
toc = ""
for n in sorted(ch):
    c = ch[n]
    cnt = sum(1 for e in entries if e['chapter'] == n)
    toc += f'<li><a href="book/{c["file"]}"><b>{n:02d}</b> {html.escape(c["h1"].split(" ",1)[-1])}<span class="cnt">{cnt} 条</span></a></li>'

# ---- 全部条目（搜索用） ----
data_json = json.dumps([{"c": e["chapter"], "e": e["entry"], "t": e["title"], "l": e["level"],
                         "f": ch[e["chapter"]]["file"].replace('.md','')} for e in entries],
                       ensure_ascii=False)

tpl = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>《高性价比工作指南》· 怎么用这本书</title>
<style>
:root {{
  --ink:#1c1c1e; --ink2:#6b6b70; --line:#e8e8ec; --bg:#ffffff; --bg2:#f7f7f9;
  --accent:#e8730c; --accent-soft:#fdf1e5;
}}
* {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; }}
h1, h2, h3, p, li, a {{ word-break:keep-all; overflow-wrap:break-word; }}
header h1, h2, .card h3, .rcard h3 {{ text-wrap:balance; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.75 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Source Han Sans SC",sans-serif;
}}
.wrap {{ max-width:920px; margin:0 auto; padding:56px 22px 96px; }}
header h1 {{ font-size:30px; line-height:1.35; letter-spacing:-.01em; margin:0 0 14px; }}
header p.lead {{ color:var(--ink2); font-size:15px; margin:0 0 6px; }}
.meta {{ color:var(--ink2); font-size:13px; margin-top:18px; }}
h2 {{ font-size:20px; margin:56px 0 6px; letter-spacing:-.01em; }}
h2 + p.hint {{ color:var(--ink2); font-size:14px; margin:0 0 20px; }}
.card, .rcard {{ border:1px solid var(--line); border-radius:14px; padding:20px 22px; margin:14px 0; background:var(--bg); }}
.card h3, .rcard h3 {{ font-size:17px; margin:0 0 6px; }}
.desc {{ color:var(--ink2); font-size:14px; margin:0 0 14px; }}
ul.chs {{ list-style:none; padding:0; margin:0; display:grid; grid-template-columns:repeat(auto-fill,minmax(255px,1fr)); gap:8px 18px; }}
ul.chs a {{ display:block; text-decoration:none; color:var(--ink); font-size:14.5px; padding:5px 0; border-bottom:1px dashed transparent; }}
ul.chs a:hover {{ color:var(--accent); }}
ul.chs b {{ color:var(--accent); font-variant-numeric:tabular-nums; margin-right:8px; font-weight:600; }}
.rcard:has(.soon) {{ background:var(--bg2); }}
.chips {{ margin:0; }}
a.ch {{ display:inline-block; text-decoration:none; color:var(--accent); background:var(--accent-soft); border-radius:999px; padding:3px 12px; font-size:13.5px; margin:3px 6px 3px 0; font-variant-numeric:tabular-nums; }}
a.ch:hover {{ background:#f8e2ca; }}
.soon {{ color:var(--ink2); font-size:13.5px; }}
ol.toc {{ list-style:none; counter-reset:none; padding:0; margin:0; }}
ol.toc li {{ border-bottom:1px solid var(--line); }}
ol.toc a {{ display:flex; align-items:baseline; gap:10px; text-decoration:none; color:var(--ink); padding:11px 2px; font-size:15px; }}
ol.toc a:hover {{ color:var(--accent); }}
ol.toc b {{ color:var(--ink2); font-weight:500; font-variant-numeric:tabular-nums; }}
.cnt {{ margin-left:auto; color:var(--ink2); font-size:12.5px; white-space:nowrap; }}
.search {{ position:sticky; top:0; background:rgba(255,255,255,.94); backdrop-filter:saturate(1.4) blur(8px); padding:12px 0; border-bottom:1px solid var(--line); margin-top:26px; z-index:5; }}
input[type=search] {{ width:100%; padding:12px 14px; font-size:15px; border:1px solid var(--line); border-radius:12px; background:var(--bg2); color:var(--ink); }}
input[type=search]:focus {{ outline:2px solid var(--accent-soft); border-color:var(--accent); }}
#hits {{ list-style:none; padding:0; margin:14px 0 0; }}
#hits li {{ padding:10px 2px; border-bottom:1px solid var(--line); font-size:14.5px; }}
#hits a {{ color:var(--ink); text-decoration:none; }}
#hits a:hover {{ color:var(--accent); }}
#hits .lvl {{ color:var(--ink2); font-size:12.5px; margin-left:8px; }}
.empty {{ color:var(--ink2); font-size:14px; padding:16px 2px; }}
footer {{ margin-top:64px; padding-top:22px; border-top:1px solid var(--line); color:var(--ink2); font-size:13px; }}
footer a {{ color:var(--ink2); }}
@media (max-width:520px) {{ .wrap {{ padding:36px 18px 72px; }} header h1 {{ font-size:25px; }} }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>《高性价比工作指南》· 怎么用这本书</h1>
  <p class="lead">50 章、{len(entries)} 条建议，按「你现在在哪一步」和「你是做什么的」两条路进入。每条都写成一句能直接照做的建议，标了性价比档位和证据等级。</p>
  <p class="meta">找不到方向就用下面的搜索；想按章节顺序读，直接翻到最后一节的全书目录。</p>
</header>

<h2>一、按你现在在哪一步</h2>
<p class="hint">从你的处境出发，只看这个阶段要用的章。同一章在不同阶段会重复出现。</p>
{''.join(stage_card(*s) for s in stages)}

<h2>二、按你是做什么的</h2>
<p class="hint">岗位不同，优先看的章不一样；带 ★ 的段落建议先扫一遍。</p>
<div class="roles">
{''.join(role_card(*r) for r in roles)}
</div>

<h2>三、搜一条试试</h2>
<p class="hint">输入关键词，例如「加班」「社保」「被裁」「提成」。点结果跳到那一章。</p>
<div class="search"><input id="q" type="search" placeholder="搜 416 条建议…" autocomplete="off"></div>
<ul id="hits"></ul>

<h2>四、全书目录</h2>
<p class="hint">50 章，每章 8–14 条，条目按性价比从高到低排。</p>
<ol class="toc">{toc}</ol>

<footer>
  <p>内容参考《高性价比人生指南》（<a href="https://github.com/eternity4719/HowToLiveBetter">eternity4719/HowToLiveBetter</a>，CC BY 4.0）的写法与逻辑整理编写。本书文字同样以 CC BY 4.0 授权。</p>
  <p>涉及法律、医疗、投资的条目仅供参考，不构成法律、医疗、投资建议。具体金额与时限以当地主管部门最新规定为准。</p>
</footer>
</div>
<script>
const DATA = {data_json};
const q = document.getElementById('q'), hits = document.getElementById('hits');
function render(kw) {{
  kw = (kw || '').trim();
  if (!kw) {{ hits.innerHTML = '<li class="empty">输入关键词开始搜；清空即关闭结果。</li>'; return; }}
  const res = DATA.filter(d => d.t.includes(kw) || d.l.includes(kw) || String(d.c).padStart(2,'0') === kw);
  if (!res.length) {{ hits.innerHTML = '<li class="empty">没有匹配的条目，换个词试试。</li>'; return; }}
  hits.innerHTML = res.slice(0, 60).map(d =>
    `<li><a href="book/${{d.f}}.md">第 ${{String(d.c).padStart(2,'0')}} 章 · ${{d.e}}. ${{d.t}}</a><span class="lvl">${{d.l}}</span></li>`).join('')
    + (res.length > 60 ? `<li class="empty">共 ${{res.length}} 条，显示前 60 条。</li>` : '');
}}
q.addEventListener('input', e => render(e.target.value));
render('');
</script>
</body>
</html>
'''
open('index.html', 'w', encoding='utf-8').write(tpl)
print("index.html bytes:", len(tpl))
