# -*- coding: utf-8 -*-
"""生成《高性价比工作指南》导航页 index.html（自包含，无外部依赖）"""
import json, html

# 动态统计：章数与条目数（标题/描述里用，避免写死）
try:
    NCH = len(json.load(open("data/chapters.json", encoding="utf-8")))
except Exception:
    NCH = 50
try:
    _it = json.load(open("data/items.json", encoding="utf-8"))
    NIT = len(_it) if isinstance(_it, list) else len(_it.get("items", []))
except Exception:
    NIT = 0

BASE = 'https://github.com/NiceCao/HowToWorkBetter/blob/main/book/'
BASECH = 'ch/'
ch = {c['n']: c for c in json.load(open('data/chapters.json', encoding='utf-8'))}
entries = json.load(open('data/entries.json', encoding='utf-8'))
blocks = json.load(open('data/blocks.json', encoding='utf-8'))['blocks']

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
    ("蓝领 / 产线 / 服务业", "进厂、产线、工地、骑手、仓储、餐饮：计件与加班费怎么算、宿舍押金怎么问、班组里怎么站住、夜班和久站的身体账、被乱罚款怎么维权。",
     [8, 11, 10, 24, 25, 28, 29, 35, 39, 43, 46]),
]

def chlink(n, text=None):
    c = ch[n]
    return f'<a class="ch" href="{BASECH}{c["file"][:-3]}.html">{text or ("第 %d 章" % n)}</a>'

def stage_card(title, desc, nums):
    inner = ""
    for n in sorted(nums):
        c = ch[n]
        short = c['h1'].split('：', 1)[-1]
        inner += f'<li><a href="{BASECH}{c["file"][:-3]}.html"><b>{n:02d}</b> {html.escape(short)}</a></li>'
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

# ---- 全书目录（按板块分组） ----
toc = ""
for b in blocks:
    items = ""
    for n in b['chapters']:
        c = ch[n]
        cnt = sum(1 for e in entries if e['chapter'] == n)
        items += f'<li><a href="{BASECH}{c["file"][:-3]}.html"><b>{n:02d}</b> {html.escape(c["h1"].split(" ",1)[-1])}<span class="cnt">{cnt} 条</span></a></li>'
    toc += (f'<h3 class="blk"><span class="bnum">板块{["一","二","三","四","五","六","七","八","九","十"][b["n"]-1]}</span>'
            f'{html.escape(b["name"])}<span class="bdesc">{html.escape(b["desc"])}</span></h3>'
            f'<ol class="toc">{items}</ol>')

# ---- 全部条目（检索用，带元信息） ----
items = json.load(open('data/items.json', encoding='utf-8'))
data_json = json.dumps(items, ensure_ascii=False, separators=(',', ':'))
blk_of = {c: b['n'] for b in blocks for c in b['chapters']}
blk_json = json.dumps(blk_of)
CN = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]


def chips(group, label, options):
    bs = ''.join(f'<button class="chip" data-g="{group}" data-v="{html.escape(str(v))}">{html.escape(str(t))}</button>'
                 for v, t in options)
    return f'<div class="fgroup"><span class="flabel">{label}</span>{bs}</div>'


filters_html = (
    chips('blk', '板块', [(b['n'], f"{CN[b['n'] - 1]} {b['name']}") for b in blocks])
    + chips('lv', '性价比', [('极高', '极高'), ('高', '高'), ('一般', '一般')])
    + chips('ev', '证据等级', [('A', 'A 级'), ('B', 'B 级'), ('C', 'C 级')])
    + chips('sc', '换回来的是', [('收入', '收入'), ('职业寿命', '职业寿命'), ('职业自由', '职业自由'), ('时间精力', '时间精力')])
    + chips('m', '要花的钱', [('不花钱', '不花钱'), ('少', '少'), ('中/多', '中/多')])
    + chips('tm', '要花的时间', [('少', '少'), ('中', '中'), ('多', '多')])
    + chips('en', '要耗的精力', [('少', '少'), ('中', '中'), ('多', '多')])
    + chips('flag', '引用情况', [('r3', '来源 ≥3 条'), ('r0', '来源：无')])
    + '<div class="fgroup"><button class="chip reset" id="reset">清空筛选</button></div>'
)

tpl = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>《高性价比工作指南》· {NCH} 章 {NIT} 条，按阶段、职业和板块找建议</title>
<meta name="description" content="写给普通打工人的工作指南：{NCH} 章、{NIT} 条建议，每条写明要花掉什么、能换回什么、证据有多硬。可以按你现在在哪一步、你是做什么的、或按板块找。">
<link rel="canonical" href="https://nicecao.github.io/HowToWorkBetter/">
<meta property="og:type" content="website">
<meta property="og:title" content="高性价比工作指南 · {NCH} 章 {NIT} 条">
<meta property="og:description" content="每条建议都写明要花掉什么、能换回什么、证据有多硬；按阶段、按职业、按板块都能找。">
<meta property="og:url" content="https://nicecao.github.io/HowToWorkBetter/">
<meta property="og:image" content="https://nicecao.github.io/HowToWorkBetter/og.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Book","name":"高性价比工作指南",
"description":"写给普通打工人的工作指南，{NCH} 章 {NIT} 条建议，每条写明成本、收益和证据等级。",
"inLanguage":"zh-CN","url":"https://nicecao.github.io/HowToWorkBetter/",
"image":"https://nicecao.github.io/HowToWorkBetter/og.png",
"author":{{"@type":"Person","name":"作者"}},"license":"https://creativecommons.org/licenses/by/4.0/"}}
</script>
<style>
:root {{
  --ink:#1c1c1e; --ink2:#6b6b70; --line:#e8e8ec; --bg:#ffffff; --bg2:#f7f7f9;
  --accent:#e8730c; --accent-soft:#fdf1e5;
  /* 标题用思源宋体，正文用思源黑体；两款均为开源字体（SIL OFL），装了就用，没装自动落到系统宋/黑体 */
  --serif:"Source Han Serif SC","Noto Serif CJK SC","Noto Serif SC","Songti SC","SimSun",serif;
  --sans:"Source Han Sans SC","Noto Sans CJK SC","Noto Sans SC","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
}}
* {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; }}
h1, h2, h3, p, li, a {{ word-break:keep-all; overflow-wrap:break-word; }}
header h1, h2, .card h3, .rcard h3 {{ text-wrap:balance; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.75 var(--sans);
}}
.wrap {{ max-width:920px; margin:0 auto; padding:56px 22px 96px; }}
header h1 {{ font-family:var(--serif); font-weight:700; font-size:31px; line-height:1.4; letter-spacing:.01em; margin:0 0 14px; }}
header p.lead {{ color:var(--ink2); font-size:15px; margin:0 0 6px; }}
.meta {{ color:var(--ink2); font-size:13px; margin-top:18px; }}
.entry {{ display:flex; flex-wrap:wrap; gap:8px 10px; align-items:center; margin:20px 0 0; }}
.entry a {{ display:inline-block; text-decoration:none; color:var(--accent); background:var(--accent-soft); border-radius:999px; padding:5px 14px; font-size:13.5px; white-space:nowrap; font-weight:500; }}
.entry a:hover {{ background:#f8e2ca; }}
h2 {{ font-family:var(--serif); font-weight:700; font-size:21px; margin:56px 0 6px; letter-spacing:.01em; }}
h2 + p.hint {{ color:var(--ink2); font-size:14px; margin:0 0 20px; }}
.card, .rcard {{ border:1px solid var(--line); border-radius:14px; padding:20px 22px; margin:14px 0; background:var(--bg); }}
.card h3, .rcard h3 {{ font-family:var(--serif); font-weight:700; font-size:17.5px; margin:0 0 6px; line-height:1.5; }}
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
h3.blk {{ font-size:16.5px; margin:34px 0 4px; font-weight:600; }}
h3.blk .bnum {{ display:inline-block; background:var(--accent-soft); color:var(--accent); border-radius:6px; padding:1px 9px; font-size:13px; margin-right:9px; vertical-align:1px; font-weight:600; }}
h3.blk .bdesc {{ display:block; color:var(--ink2); font-size:13.5px; font-weight:400; margin:5px 0 0 0; }}
ol.toc {{ list-style:none; counter-reset:none; padding:0; margin:0 0 6px; }}
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
.filters {{ margin:22px 0 4px; }}
.fgroup {{ display:flex; flex-wrap:wrap; gap:7px; align-items:center; margin:0 0 10px; }}
.flabel {{ color:var(--ink2); font-size:13px; min-width:76px; }}
.chip {{ font:inherit; font-size:13.5px; color:var(--ink); background:var(--bg2); border:1px solid var(--line); border-radius:999px; padding:5px 13px; cursor:pointer; }}
.chip:hover {{ border-color:var(--accent); color:var(--accent); }}
.chip.on {{ background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }}
.chip.reset {{ background:transparent; border-style:dashed; color:var(--ink2); }}
.fcount {{ color:var(--ink2); font-size:13px; margin:12px 0 0; }}
#hits li {{ display:flex; align-items:baseline; gap:12px; }}
#hits a {{ flex:1 1 auto; }}
.cno {{ color:var(--accent); font-variant-numeric:tabular-nums; font-size:13px; margin-right:8px; }}
.tags {{ flex:0 0 auto; white-space:nowrap; }}
.tag {{ display:inline-block; font-size:12px; color:var(--ink2); background:var(--bg2); border-radius:6px; padding:1px 8px; margin-left:6px; }}
.tag.lv {{ color:var(--accent); background:var(--accent-soft); }}
.tag.lv.hot {{ color:#fff; background:var(--accent); }}
.tag.evA {{ color:#1a7f37; background:#eaf7ee; }}
.tag.evB {{ color:#8a6d00; background:#fdf6e3; }}
.tag.evC {{ color:#8a4b00; background:#fdf1e5; }}
@media (max-width:520px) {{ .tags {{ display:none; }} .flabel {{ min-width:100%; }} }}
footer {{ margin-top:64px; padding-top:22px; border-top:1px solid var(--line); color:var(--ink2); font-size:13px; }}
footer a {{ color:var(--ink2); }}
@media (max-width:520px) {{ .wrap {{ padding:36px 18px 72px; }} header h1 {{ font-size:25px; }} }}
mark {{ background:#fff2c2; color:inherit; border-radius:3px; padding:0 2px; }}
.legend {{ border:1px solid var(--line); border-radius:14px; padding:6px 22px 14px; margin:14px 0 0; }}
.legend div {{ border-top:1px solid var(--line); padding:12px 0 2px; font-size:14.5px; color:var(--ink); }}
.legend div:first-child {{ border-top:0; }}
.legend b {{ color:var(--accent); font-weight:600; margin-right:6px; }}
.legend code {{ background:var(--bg2); border-radius:5px; padding:1px 6px; font-size:13px; }}
.sharehint {{ color:var(--ink2); font-size:12.5px; margin:6px 0 0; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --ink:#e8e8ec; --ink2:#a0a0a6; --line:#2c2c31; --bg:#141416; --bg2:#1c1c20; --accent:#f5923c; --accent-soft:#3a2a1a; }}
  body {{ background:var(--bg); color:var(--ink); }}
  .search {{ background:rgba(20,20,22,.94); }}
  input[type=search] {{ background:var(--bg2); color:var(--ink); }}
  .chip {{ background:var(--bg2); color:var(--ink); }}
  a.ch:hover {{ background:#4a3520; }}
  .entry a:hover {{ background:#4a3520; }}
  mark {{ background:#4a3a12; }}
  .tag.evA {{ color:#7bd88f; background:#17301f; }}
  .tag.evB {{ color:#e2c56b; background:#2f2a14; }}
  .tag.evC {{ color:#f0a878; background:#332315; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>《高性价比工作指南》· 检索与指路</h1>
  <p class="lead">{NCH} 章、{len(entries)} 条建议，按「你现在在哪一步」和「你是做什么的」两条路进入。每条都写成一句能直接照做的建议，标了性价比档位和证据等级。</p>
  <p class="meta">没有明确方向，就用第三节的搜索框直接搜关键词；想按章节顺序读，翻到最后一节的「全书目录」。</p>
  <nav class="entry">
    <a href="#find">在线检索</a>
    <a href="https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.pdf">下载 PDF</a>
    <a href="https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.epub">下载 EPUB</a>
    <a href="https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.html">下载离线单页</a>
    <a href="https://shangbanbao.com/work.html">手机上读：上班宝</a>
  </nav>
</header>

<h2>一、按你现在在哪一步</h2>
<p class="hint">从你的处境出发，只看这个阶段要用的章。同一章在不同阶段会重复出现。</p>
{''.join(stage_card(*s) for s in stages)}

<h2>二、按你是做什么的</h2>
<p class="hint">岗位不同，优先看的章不一样；带 ★ 的段落建议先扫一遍。</p>
<div class="roles">
{''.join(role_card(*r) for r in roles)}
</div>

<h2 id="find">三、按条件找</h2>
<p class="hint">七组条件可以叠着用：先圈板块，再挑性价比档位、证据等级、你要换回来的东西，以及愿不愿意花钱、花时间、耗精力。点一条结果，直接跳到那一章的正文位置。</p>
<div class="filters">
{filters_html}
</div>
<div class="search"><input id="q" type="search" placeholder="再搜个关键词，例如 加班 / 社保 / 被裁 / 提成…" autocomplete="off"></div>
<p class="fcount" id="fcount"></p>
<p class="sharehint">你现在的筛选就写在网址里：复制地址栏的链接发给别人，他打开看到的是同一批结果。按 / 可以直接跳到搜索框。</p>
<ul id="hits"></ul>

<h2>四、这些标记什么意思</h2>
<p class="hint">每条建议前面都挂着几个标记，读之前花一分钟弄清楚，能省很多判断成本。</p>
<div class="legend">
  <div><b>性价比</b>：极高 = 花很少的钱、时间和精力就能换回明确好处；高 = 值得做，但要占一点时间或精力；一般 = 有条件再做，或收益取决于你所在的公司和行业。</div>
  <div><b>成本</b>：钱 / 时间 / 精力 三样，写成 <code>钱=0 时间=少 精力=低</code>。钱=0 指不需要额外掏钱；时间是「少（顺手就做）/ 中（几小时或断续几天）/ 多（长期占用）」；精力是「低 / 中 / 高」，指要不要持续费神。</div>
  <div><b>口径</b>：这条建议最终换回来的是什么——收入 / 职业寿命（能干得更久、更稳）/ 职业自由（能选择去哪、做什么）/ 时间精力（少加班、少内耗）。</div>
  <div><b>证据等级</b>：A = 有法条、官方统计或权威报告直接支持；B = 官方数据经过推算，或多个来源互相印证；C = 没有官方数据，属于经验判断，看到 C 请结合自己情况。</div>
  <div><b>来源</b>：只放能直接证明这条论点的出处 —— 官方文件与法条、统计年鉴、同行评议论文、学术书籍与权威期刊都算；证明不了这条的一律不引，确实找不到的写「无」，正文按通识经验说清，不拿别的数据凑数。</div>
</div>

<h2>五、全书目录（按板块）</h2>
<p class="hint">50 章分 7 个板块；点章名看正文（站内页面）。每章内部条目按性价比从高到低排。</p>
{toc}

<footer>
  <p>仓库：<a href="https://github.com/NiceCao/HowToWorkBetter">github.com/NiceCao/HowToWorkBetter</a>（章节原文也在这里的 <code>book/</code>）。</p>
  <p>内容参考《高性价比人生指南》（<a href="https://github.com/eternity4719/HowToLiveBetter">eternity4719/HowToLiveBetter</a>，CC BY 4.0）的写法与逻辑整理编写。本书文字同样以 CC BY 4.0 授权。</p>
  <p>涉及法律、医疗、投资的条目仅供参考，不构成法律、医疗、投资建议。具体金额与时限以当地主管部门最新规定为准。</p>
</footer>
</div>
<script>
const CH = 'ch/';
const ITEMS = {data_json};
const BLK = {blk_json};
const q = document.getElementById('q'), hits = document.getElementById('hits'), fcount = document.getElementById('fcount');
const sel = {{'blk':new Set(), 'lv':new Set(), 'ev':new Set(), 'sc':new Set(), 'm':new Set(), 'tm':new Set(), 'en':new Set(), 'flag':new Set()}};
const esc = s => String(s).replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
const hl = (s, kw) => kw ? esc(s).split(esc(kw)).join('<mark>' + esc(kw) + '</mark>') : esc(s);
function syncUrl() {{
  const parts = [];
  for (const g in sel) sel[g].forEach(v => parts.push(g + '=' + encodeURIComponent(v)));
  const kw = q.value.trim();
  if (kw) parts.push('q=' + encodeURIComponent(kw));
  history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname);
}}
function readUrl() {{
  const h = location.hash.replace(/^#/, '');
  if (!h) return;
  new URLSearchParams(h).forEach((v, k) => {{
    if (k === 'q') {{ q.value = v; return; }}
    if (!sel[k]) return;
    sel[k].add(v);
    const b = [...document.querySelectorAll('.chip')].find(x => x.dataset.g === k && x.dataset.v === v);
    if (b) b.classList.add('on');
  }});
}}
const CN = ['一','二','三','四','五','六','七'];

function match(d) {{
  if (sel.blk.size && !sel.blk.has(String(BLK[d.c]))) return false;
  if (sel.lv.size && !sel.lv.has(d.lv)) return false;
  if (sel.ev.size && !sel.ev.has(d.ev)) return false;
  if (sel.sc.size && !(d.sc || []).some(s => sel.sc.has(s))) return false;
  if (sel.m.size && !sel.m.has(d.m)) return false;
  if (sel.tm.size && !sel.tm.has(d.tm)) return false;
  if (sel.en.size && !sel.en.has(d.en)) return false;
  if (sel.flag.has('r3') && !(d.srcs >= 3)) return false;
  if (sel.flag.has('r0') && d.srcs > 0) return false;
  return true;
}}

function render() {{
  const kw = q.value.trim();
  let res = ITEMS.filter(match);
  if (kw) res = res.filter(d => d.t.includes(kw) || String(d.e) === kw
    || ('第' + String(d.c).padStart(2, '0') + '章').includes(kw) || String(d.c).padStart(2, '0') === kw);
  const shown = res.slice(0, 80);
  if (!res.length) {{
    hits.innerHTML = '<li class="empty">没有符合条件的条目，去掉一个条件再试。</li>';
  }} else {{
    hits.innerHTML = shown.map(d =>
      `<li><a href="${{CH}}${{d.f}}.html#e${{d.e}}"><span class="cno">${{String(d.c).padStart(2,'0')}}-${{d.e}}</span> ${{hl(d.t, kw)}}</a>`
      + `<span class="tags"><span class="tag lv${{d.lv === '极高' ? ' hot' : ''}}">${{esc(d.lv)}}</span>`
      + `<span class="tag ev${{d.ev}}">${{esc(d.ev)}} 级</span>`
      + `<span class="tag">${{esc((d.sc || []).join(' / '))}}</span></span></li>`).join('')
      + (res.length > shown.length ? `<li class="empty">共 ${{res.length}} 条，显示前 ${{shown.length}} 条；再选一个条件缩小范围。</li>` : '');
  }}
  const on = Object.values(sel).reduce((a, s) => a + s.size, 0);
  fcount.textContent = '共 ' + ITEMS.length + ' 条，当前符合条件 ' + res.length + ' 条' + (on ? '（已选条件 ' + on + ' 个）' : '');
  syncUrl();
}}

document.querySelectorAll('.chip').forEach(b => b.addEventListener('click', () => {{
  if (b.id === 'reset') {{
    Object.values(sel).forEach(s => s.clear());
    document.querySelectorAll('.chip.on').forEach(x => x.classList.remove('on'));
    q.value = ''; render(); return;
  }}
  const g = b.dataset.g, v = b.dataset.v;
  if (sel[g].has(v)) {{ sel[g].delete(v); b.classList.remove('on'); }}
  else {{ sel[g].add(v); b.classList.add('on'); }}
  render();
}}));
q.addEventListener('input', render);
document.addEventListener('keydown', e => {{
  if (e.key === '/' && document.activeElement !== q) {{ e.preventDefault(); q.focus(); }}
  if (e.key === 'Escape' && document.activeElement === q) {{ q.value = ''; render(); q.blur(); }}
}});
readUrl();
render();
</script>
</body>
</html>
'''
open('index.html', 'w', encoding='utf-8').write(tpl)
print("index.html bytes:", len(tpl))
