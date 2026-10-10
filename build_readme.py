# -*- coding: utf-8 -*-
"""生成《高性价比工作指南》的 README.md。

README 只由这个脚本生成，不要手改 README.md（改了会被覆盖）。
所有数字都从 data/*.json 读出来，不写死：
  - data/chapters.json  ：章节目录（章号、标题、正文文件名、字数、引言）
  - data/blocks.json    ：7 个板块及其章号
  - data/items.json     ：全书条目（章号 c、性价比 lv、证据等级 ev、成本 m/tm/en、口径 sc…）
用法：
    python3 build_readme.py
"""
import json
import os
import re
import sys
from collections import Counter
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# ------------------------------------------------------------------ 读数据
chapters = json.load(open('data/chapters.json', encoding='utf-8'))
blocks = json.load(open('data/blocks.json', encoding='utf-8'))['blocks']
items = json.load(open('data/items.json', encoding='utf-8'))

ch = {c['n']: c for c in chapters}
n_ch = len(chapters)
n_blk = len(blocks)

total = len(items)
lv = Counter(i['lv'] for i in items)          # 性价比档
ev = Counter(i['ev'] for i in items)          # 证据等级
sc = Counter(s for i in items for s in i['sc'])  # 口径
per_ch = Counter(i['c'] for i in items)       # 每章条数

lvH, lvM, lvL = lv['极高'], lv['高'], lv['一般']
evA, evB, evC = ev['A'], ev['B'], ev['C']

CN = "一二三四五六七八九十"


def cn_num(n):
    return CN[n - 1] if 1 <= n <= 10 else str(n)


# ------------------------------------------------------------------ 章节引言
def chapter_intro(c):
    """拿章节的一句话引言：先看 chapters.json，没有就从正文 H1 后第一段取。"""
    intro = (c.get('intro') or [''])[0].strip()
    if intro:
        return intro
    path = os.path.join('book', c['file'])
    if not os.path.exists(path):
        return ''
    for line in open(path, encoding='utf-8').read().splitlines()[1:14]:
        s = line.strip()
        if not s or s.startswith('#') or set(s) <= set('-*_ '):
            continue
        if s.startswith('>'):
            s = s[1:].strip()
        s = s.strip('*').strip()
        # 跳过被挤进来的元信息行（性价比/成本/口径/证据等级、或 √ 要点）
        if re.match(r'^(性价比|成本|口径|证据等级)', s) or s.startswith('√'):
            continue
        return re.split(r'(?<=[。！？])', s)[0].strip() if s else ''
    return ''


# ------------------------------------------------------------------ 徽章
def badge(label, message, color, href):
    src = f"https://img.shields.io/badge/{quote(label)}-{quote(message)}-{color}?style=flat-square"
    return f"[![{label}]({src})]({href})"


badge_items = badge('条目', f'{total} 条', '18794e', 'book/')
badge_ev = badge('证据分级', f'A {evA} · B {evB} · C {evC}', '915930', '#证据分级')
badge_license = badge('许可', 'CC BY 4.0', '565a5f', '#许可')

# ------------------------------------------------------------------ 目录
toc = ""
for b in blocks:
    toc += f"\n**板块{cn_num(b['n'])} · {b['name']}**（{b['desc']}）\n\n"
    for n in b['chapters']:
        c = ch[n]
        title = c['h1'].split(' ', 1)[-1]
        intro = chapter_intro(c)
        toc += f"{n}. [{title}](book/{c['file']})：{intro}（{per_ch.get(n, 0)} 条）\n"
    toc += "\n"

# ------------------------------------------------------------------ 正文
readme = f"""<div align="center">

<img src="og.png" alt="高性价比工作指南 —— 用最少的钱、时间和精力，换回更多的收入、职业寿命和职业自由" width="820">

# 高性价比工作指南

讲怎么选行业、挑公司、谈薪水，怎么在入职头两年站稳，怎么晋升和转型，被裁、被欠薪、受了工伤怎么按流程把该拿的拿回来。法律、社保、工伤这些制度上的内容，按中国大陆的现行规定写。<br>
{total} 条建议，每条写明要花掉什么、能换回什么、证据有多硬；来源只放能直接证明这条论点的官方统计、法规原文、学术论文、书籍与权威报告，确实找不到的写「无」，并在限制里说明这是经验判断。

不用全做：这是按性价比排好的备选单，不是任务清单——挑走一两条就算数。

{badge_items}
{badge_ev}
{badge_license}

### [打开站内检索页](https://nicecao.github.io/HowToWorkBetter/)

<table>
<tr><td align="right"><b>下载</b></td><td align="left">

[PDF](https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.pdf) · [EPUB](https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.epub) · [离线单文件（HTML）](https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.html)

</td></tr>
<tr><td align="right"><b>手机上读</b></td><td align="left">

[上班宝 · 工作指南](https://shangbanbao.com/work.html)（在线检索页的移动版）

</td></tr>
</table>

</div>

---

## 怎么读

不用从第 1 章读到第 {n_ch} 章。全书 {total} 条建议按 {n_blk} 个板块排好，直接跳到你现在用得上的那一条就行。三种进入方式：

- **按你现在在哪一步**：还没入行 → 拿到 offer 谈条件 → 入职前 90 天 → 站稳的 1–3 年 → 开始带人 → 遇到风险（被裁、想跳、被欺负）→ 长期与兜底。
- **按你是做什么的**：销售市场商务 / 产品技术运营 / HR 财务法务行政 / 管理岗 / 体制内 / 应届生 / 蓝领产线服务业（进厂、工地、骑手、仓储、餐饮：计件与加班费、宿舍押金、班组、夜班与久站、被乱罚款怎么维权）。
- **按板块顺读**：照着下面目录，从「选对赛道」往后一个板块一个板块读，每个板块开头一句说明它管哪一段。

三种都能在站内检索页里走：**[https://nicecao.github.io/HowToWorkBetter/](https://nicecao.github.io/HowToWorkBetter/)**。页面能按关键词（「加班」「社保」「提成」「被裁」）、章节、证据等级和成本筛，几个条件能叠着用，点进去直接到具体那一条。

## 每条长什么样

每条建议都由五部分组成：

- **标题**：就是那句建议本身，能直接照做；
- **说人话**：这条在讲什么，一句话结论 + 一个能核对的数字；
- **为什么**：背后的规则、账或机制；
- **来源**：官方统计、法规原文、学术论文与书籍、权威报告，附链接；确实没有的写「无」；
- **限制与争议**：这条在什么情况下不成立、数据是哪一年的、哪里有争议。

## 四种资源（要花掉什么）

每条开头都有一行成本，比如 `成本：钱=0 时间=少 精力=低`。它说的是做这条建议要花掉什么，三个词这么读：

- **钱**：这条要额外花的现金。`0` 是不花自己的钱（公司承担，或本来就要做的事）；`少` 是几十块以内；`中` 及以上是上百到上千（报名费、考证费、体检费、差旅、律师费）。
- **时间**：一次性要搭进去的时间。`少` 是半天以内或顺手就做；`中` 是几个整天；`多` 是要按周、按月往里投。
- **精力**：要占用的注意力、体力和耐受力。`低` 是顺手就做、不费神；`中` 是要占一整块精力；`高` 是要持续消耗、容易累。

第四样资源是 **毅力**——需要长期坚持、容易半途而废的那部分。本书没有单独给毅力打分（条目里只标钱、时间、精力这三样）：需要长期坚持的条目，会把精力标高一档，并在「限制与争议」里写清要坚持多久、什么情况算没做到。

## 证据分级

每条都标证据等级：

| 等级 | 含义 |
| --- | --- |
| A | 有具体数字可查，出处是官方统计（国家统计局、人社部、最高法、卫健委等）、法规原文，或者权威机构的研究报告，能说出数字和口径 |
| B | 有间接支撑，或者只有单一项来源，说不出一个确切的数字 |
| C | 经验做法，没有直接的数据或文献支撑 |

全书 {total} 条里 A 级 {evA} 条、B 级 {evB} 条、C 级 {evC} 条。来源只放能直接证明这条论点的官方统计、法规原文、学术论文、书籍与权威报告，不引二手转述；确实没有直接来源的，来源栏写「无」，正文按通识经验写。

A 级只说明「有具体数字、出处可核」，不说明这个数字一定是因果；法律和政策类条目的 A 级，指的是引到了法条或官方文件原文。

## 性价比档

证据等级只回答「这个数字可不可信」，不回答「这件事值不值得做」。所以每条还标了成本（钱、时间、精力）和口径（换回的是收入、职业寿命、职业自由还是时间精力），合出一个性价比档：

| 档 | 条件 | 条数 |
| --- | --- | --- |
| 极高 | 成本接近零、收益大 | {lvH} |
| 高 | 收益大，或者收益中等而成本极低 | {lvM} |
| 一般 | 有条件再做，或者需要长期投入 | {lvL} |

这一档是从成本和收益排出来的顺序，不是证据等级。**「一般」不等于不该做**——全书的条目都是建议做的，只是这一档要你自己掂量那笔花销值不值。

## 读懂数字（术语表）

正文尽量说人话，但有几类词会反复出现，先在这里交代清楚。

**口径**——这条换回的是哪一类东西，一条可以同时算两类：

| 口径 | 指什么 |
| --- | --- |
| 收入 | 换回现金，或者能折成钱的待遇：涨薪、提成、补贴、少交的税、拿到的赔偿 |
| 职业寿命 | 换回「这份能干多久、往上还有没有空间、会不会被年龄卡掉」 |
| 职业自由 | 换回选择权和脱身能力：不被合同、竞业、违约金捆住手脚，想走能走 |
| 时间精力 | 换回把每天的时间或注意力省下来、要回来 |

全书带各口径的条目数（一条可同时算两类）：收入 {sc['收入']}、职业寿命 {sc['职业寿命']}、职业自由 {sc['职业自由']}、时间精力 {sc['时间精力']}。

其余几个词：

| 词 | 意思 |
| --- | --- |
| 性价比 | 这项建议能换回的好处，和要花掉的成本比出来的档位，见上面「性价比档」 |
| 成本 | 做这条要花掉的钱、时间、精力，见上面「四种资源」 |
| 证据等级 | 这条数字可信到什么程度，分 A、B、C 三档，见上面「证据分级」 |
| ROI | 投入产出比，投进去多少、换回多少。书里说「ROI 高」，就是同样的投入换回更多 |

## 目录（按 {n_blk} 个板块）

{toc}

## 自己跑一份

多数人用不着：站内检索页 **[https://nicecao.github.io/HowToWorkBetter/](https://nicecao.github.io/HowToWorkBetter/)** 是现成的。

想自己重建整本书（书稿是 Markdown，检索页、章节页和这份 README 都由脚本生成，没有后端、没有数据库）：

```bash
git clone https://github.com/NiceCao/HowToWorkBetter.git
cd HowToWorkBetter
python3 build_items.py      # 解析 book/*.md，生成 data/items.json
python3 build_index.py      # 用 data/*.json 生成站内检索页 index.html
python3 build_site.py       # 把 book/*.md 渲染成 ch/*.html（每条带锚点）
python3 build_readme.py     # 生成这份 README.md
python3 tools/check_book.py # 质检：核对 data/*.json 与各脚本用到的数字是否自洽
python3 -m http.server 8000 # 本地预览 http://localhost:8000/
```

需要 Python 3 和 markdown 库（`pip install markdown`）。`data/items.json` 是全书 {total} 条的机器可读清单（章号、条号、标题、性价比、证据等级、成本、口径），`data/chapters.json` 是 {n_ch} 章目录，`data/blocks.json` 是 {n_blk} 个板块。拿去做小程序、每日推送、检索都行。

## 怎么参与

发现某条写错了、数字过时了，或者想补一个主题，去 [GitHub 仓库提 issue](https://github.com/NiceCao/HowToWorkBetter/issues/new/choose)，页面上备好了两个模板：

- **纠错**：写明第几章第几条、原文怎么写的、应该改成什么，附上能查的官方依据；
- **新内容**：说清想加的主题、想让它回答什么问题。

按模板填就行。没有可查的官方来源，纠错就没法改；知乎、公众号这类转述不算依据。

## 来源与免责

数字来自官方统计、法规原文、学术论文与书籍、权威机构报告，每条都标了来源；确实没有直接来源的写「无」。所有内容仅供参考，**不构成法律、医疗、投资建议**；金额、时限、比例以当地主管部门最新规定为准。遇到具体纠纷请咨询专业人士，或拨打 12333（人社）、12348（法律援助）。

## 许可

正文用 [CC BY 4.0](LICENSE) 发布，范围是 `book/`、`docs/` 和本 README 的文字。你可以转载、改编、商用，不用来问作者，但要做到三件事：

- 写明出处：「高性价比工作指南」，附上本仓库链接；
- 附上许可证链接 https://creativecommons.org/licenses/by/4.0/ ；
- 改过内容的要写明改过。书里的法条、社保和赔偿标准经常更新，建议同时写上你同步的是哪一天的版本。

代码用 [MIT](LICENSE-CODE)，范围是 `index.html`、`build_index.py`、`build_items.py`、`build_site.py`、`build_readme.py` 和 `tools/`。

## 致谢

写法与内容逻辑参考开源书《高性价比人生指南》（[eternity4719/HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter)，CC BY 4.0）。本书面向职场，独立编写。
"""

open('README.md', 'w', encoding='utf-8').write(readme)

print("README bytes:", len(readme.encode('utf-8')))
print("章节:", n_ch, "板块:", n_blk, "条目:", total)
print("性价比 极高/高/一般:", lvH, lvM, lvL)
print("证据 A/B/C:", evA, evB, evC)
print("口径 收入/职业寿命/职业自由/时间精力:", sc['收入'], sc['职业寿命'], sc['职业自由'], sc['时间精力'])
