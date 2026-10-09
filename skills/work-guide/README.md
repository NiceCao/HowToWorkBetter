# 工作指南 skill（work-guide）

让 AI 助手照《高性价比工作指南》回答具体的职场问题：这家公司该不该去、两个 offer 怎么比、被欠薪怎么办、要不要跳槽、试用期怎么谈、社保断了怎么补。

它只做一件事：**先把书里相关条目查出来，再照书的算账方式排好序回答**，每条结论注明出自「第几章第几条」。查不到就说查不到，不凭记忆编数字或法条；只引书里已写明的官方来源，不预测收益、不写推荐。

规则全在 [SKILL.md](SKILL.md) 里，Claude Code 和 Codex 共用同一个文件，不维护两份。

书：50 章、416 条建议，分 7 个板块。正文在 `book/`，结构化数据在 `data/`。在线检索页：<https://nicecao.github.io/HowToWorkBetter/>

## 装到 Claude Code

在本仓库里开 Claude Code，把这个文件放进项目目录的 `.claude/skills/` 就生效；想在任何目录下都能用，复制到个人 skill 目录：

```bash
mkdir -p ~/.claude/skills/work-guide && curl -fsSL -o ~/.claude/skills/work-guide/SKILL.md "https://raw.githubusercontent.com/NiceCao/HowToWorkBetter/main/skills/work-guide/SKILL.md"
```

之后直接问「这家公司值不值得去」「两个 offer 怎么选」「被欠薪了怎么办」就会触发；也可以显式说「用 work-guide 回答」。

## 装到 Codex

在本仓库里开 Codex，读根目录的 `AGENTS.md` 就会找到它；想在任何目录下都能用，复制到 Codex 的个人 skill 目录 `~/.agents/skills`：

```bash
mkdir -p ~/.agents/skills/work-guide && curl -fsSL -o ~/.agents/skills/work-guide/SKILL.md "https://raw.githubusercontent.com/NiceCao/HowToWorkBetter/main/skills/work-guide/SKILL.md"
```

之后直接问问题就会按描述自动触发，也可以输入 `$work-guide` 显式调用。**注意是 `$` 不是 `/`**，新版 Codex 输入 `/work-guide` 会报 `Unrecognized command`。没出现就重启一次 Codex。

## 正文从哪来

本地有这个仓库就读本地的 `book/`；没有就现取：

```bash
git clone --depth 1 https://github.com/NiceCao/HowToWorkBetter.git "${TMPDIR:-/tmp}/htwb"
```

整本不大，浅克隆一次几秒。取不到网络就如实说取不到，不替代正文。

## 三条示例问法

- 「这家公司社保按最低基数缴，还老拖欠工资，值不值得去？」
- 「A 公司月薪高 2 千但不缴公积金，B 公司月薪低但五险一金齐全，怎么比？」
- 「我被裁了，公司只肯给一个月工资，按书里该怎么争取？」

## 改动须知

SKILL.md 里不留任何会跟着正文漂的清单和数值：章目录去读根目录 README 的目录或 `data/chapters.json`，条目的性价比和证据等级去读 `data/items.json` 或正文每条上方的标注。
