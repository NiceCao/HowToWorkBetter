# -*- coding: utf-8 -*-
"""按《高性价比人生指南》的 README 体例生成 README.md"""
import re, glob, os, json

files = sorted(glob.glob('book/*.md'))
rows, lv, ev, total = [], None, None, 0
from collections import Counter
L, E = Counter(), Counter()
chapters = []
for f in files:
    n = int(os.path.basename(f)[:2])
    t = open(f, encoding='utf-8').read()
    h1 = [l for l in t.splitlines() if l.startswith('# ')][0][2:].strip()
    title = h1.split(' ', 1)[-1]
    # 章首引言第一句
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    intro = ''
    for l in lines[1:6]:
        if l.startswith(('#', '-', '>')): continue
        intro = re.split(r'(?<=[。！？])', l)[0]
        break
    cnt = len(re.findall(r'^###\s*\d+', t, re.M))
    L.update(re.findall(r'^>?\s*性价比：(\S+)', t, re.M))
    E.update(re.findall(r'^证据等级：(\S+)', t, re.M))
    total += cnt
    chapters.append((n, title, os.path.basename(f), intro, cnt))

evA = E['A']; evB = E['B'] + E['B+'] + E['B-']; evC = E['C']
lvH = L['极高']; lvM = L['高'] + L.get('高（帮你省钱=帮你赚钱）', 0); lvL = L['一般']

blocks = json.load(open('data/blocks.json', encoding='utf-8'))['blocks']
CN = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
toc = ""
for b in blocks:
    toc += f"\n**板块{CN[b['n']-1]} · {b['name']}**（{b['desc']}）\n\n"
    for n, title, fn, intro, cnt in chapters:
        if n in b['chapters']:
            toc += f"{n}. [{title}](book/{fn})：{intro}（{cnt} 条）\n"
    toc += "\n"

readme = f"""<div align="center">

# 高性价比工作指南

讲怎么选行业、挑公司、谈薪水，怎么在入职头两年站稳，怎么晋升和转型，被裁、被欠薪、受了工伤怎么按流程把该拿的拿回来。法律、社保、工伤这些制度上的内容，按中国大陆的现行规定写。<br>
{total} 条建议，每条写明要花掉什么、能换回什么、证据有多硬，来源只引官方统计、法规原文和权威机构报告。

不用全做：这是按性价比排好的备选单，不是任务清单——挑走一两条就算数。

[![条目](https://img.shields.io/badge/%E6%9D%A1%E7%9B%AE-{total}%20%E6%9D%A1-18794e?style=flat-square)](book/)
[![证据分级](https://img.shields.io/badge/%E8%AF%81%E6%8D%AE%E5%88%86%E7%BA%A7-A%20{evA}%20%C2%B7%20B%20{evB}%20%C2%B7%20C%20{evC}-915930?style=flat-square)](#证据分级)
[![许可](https://img.shields.io/badge/%E8%AE%B8%E5%8F%AF-CC%20BY%204.0-565a5f?style=flat-square)](#许可)

### [打开导航页（怎么用这本书）](index.html)

</div>

## 从哪开始读

别从第 1 章顺读。先打开 **[导航页](index.html)**，按两条路进入：

- **你现在在哪一步**：还没入行 → 拿到 offer 谈条件 → 入职前 90 天 → 站稳的 1–3 年 → 开始带人 → 遇到风险（被裁、想跳、被欺负）→ 长期与兜底；
- **你是做什么的**：销售市场商务 / 产品技术运营 / HR 财务法务行政 / 管理岗 / 体制内 / 应届生 / 蓝领产线。

导航页里还能直接搜关键词（「加班」「社保」「提成」「被裁」），跳到具体那一条。

## 目录（按 7 个板块）

{toc}

## 每条长什么样

每条建议由五部分组成：

- **标题**：就是那句建议本身，能直接照做；
- **说人话**：这条在讲什么，一句话结论 + 一个可核对的数字；
- **为什么**：背后的规则、账或机制；
- **来源**：官方统计、法规原文、权威报告，附链接；
- **限制与争议**：这条在什么情况下不成立、数据是哪一年的、哪里有争议。

## 证据分级

每条都标证据等级：

| 等级 | 含义 |
| --- | --- |
| A | 有具体数字可查，出处是官方统计（国家统计局、人社部、最高法、卫健委等）、法规原文，或者权威机构的研究报告，能说出数字和口径 |
| B | 有间接支撑，或者只有单一项来源，说不出一个确切的数字 |
| C | 经验做法，没有直接的数据或文献支撑 |

全书 {total} 条中 A 级 {evA} 条、B 级 {evB} 条、C 级 {evC} 条。来源只引官方统计、法规原文和权威机构报告，不引二手转述；少数站点的链接对脚本不友好，需在浏览器打开。

A 级只说明「有具体数字、出处可核」，不说明这个数字一定是因果。法律和政策类条目的 A 级，指的是引到了法条或官方文件原文。

## 性价比档

证据等级只回答「这个数字可不可信」，不回答「这件事值不值得做」。所以每条还标了成本（钱、时间、精力）和口径（换回的是收入、时间精力还是职业寿命），合出一个性价比档：

| 档 | 条件 | 条数 |
| --- | --- | --- |
| 极高性价比 | 成本接近零、收益大 | {lvH} |
| 高性价比 | 收益大，或者收益中等而成本极低 | {lvM} |
| 一般性价比 | 有条件再做，或者需要长期投入 | {lvL} |

## 结构化数据

- `data/entries.json`：{total} 条建议的清单（章号、条号、标题、性价比档位）；
- `data/chapters.json`：50 章目录与字数。

想拿去做别的应用（小程序、每日推送、检索）可以直接用。

## 来源与免责

数字来自官方统计、法规原文与权威机构报告，每条都标了来源。所有内容仅供参考，**不构成法律、医疗、投资建议**；金额、时限、比例以当地主管部门最新规定为准。遇到具体纠纷请咨询专业人士，或拨打 12333（人社）、12348（法律援助）。

## 许可

正文用 [CC BY 4.0](LICENSE) 发布，范围是 `book/`、`docs/` 和本 README 的文字。你可以转载、改编、商用，不用来问作者，但要做到三件事：

- 写明出处：「高性价比工作指南」，附上本仓库链接；
- 附上许可证链接 https://creativecommons.org/licenses/by/4.0/ ；
- 改过内容的要写明改过。书里的法条、社保和赔偿标准经常更新，建议同时写上你同步的是哪一天的版本。

代码用 [MIT](LICENSE-CODE)，范围是 `index.html`、`build_index.py` 和 `build_readme.py`。

## 致谢

写法与内容逻辑参考开源书《高性价比人生指南》（[eternity4719/HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter)，CC BY 4.0）。本书是面向职场的独立编写。
"""
open('README.md', 'w', encoding='utf-8').write(readme)
print("README bytes:", len(readme), "entries:", total, "A/B/C:", evA, evB, evC, "lv:", lvH, lvM, lvL)
