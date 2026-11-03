<div align="center">

# 毛泽东思想方法 · 思考与决策 Skill

**mao-lifelong-counsel**

让 AI 按毛泽东留在著作里的方法帮你想问题：先摸情况，抓主要矛盾，算力量和时间，替对手想，分阶段，定关节，做预案。<br>
**不模仿口吻，复原方法；每一句原话都能回到原文逐字核对。**

[安装](#安装) · [两个版本](#两个版本怎么选) · [示例](examples/) · [工作原理](docs/HOW_IT_WORKS.md) · [回测](docs/EVALUATION.md) · [English](#english)

![Agent Skills](https://img.shields.io/badge/Agent%20Skills-SKILL.md-blue) ![Codex](https://img.shields.io/badge/Codex-supported-green) ![Claude Code](https://img.shields.io/badge/Claude%20Code-supported-green) ![License](https://img.shields.io/badge/license-MIT%20%2B%20CC%20BY--NC--SA%204.0-lightgrey)

</div>

适用于 Codex、Claude Code 以及其他支持 Agent Skills（SKILL.md）开放标准的工具。回答用中文。

## 它能帮你做什么

- **拿主意**：卖公司还是融资，怎样带一个难带的班，要不要跟着客户出海。先给判断再讲理由，并告诉你哪一条事实变了，结论就要变。
- **查出处**：网上流传的一句话是不是他说的，出自哪篇、什么场合，他当时在想什么问题。
- **学方法**：他怎样读书，怎样复盘认错，怎样处理内部分歧，怎样判断形势。

## 亮点

1. **393 个思维模式，都有出处。** 从约 1.3 万张思维切片卡里归纳，覆盖认识与求知、辩证法、组织与领导、斗争与竞争、复盘与修正等 14 个领域，其中 375 个的证据跨三个以上年代。每个模式写明在什么处境下用、推理分几步、「他常问的问题」、不适用的边界。
2. **原话逐字核验。** 配一个约 9,300 篇的分层原文库（选集、文集、建国以来文稿、军事文集、年谱等）和核验脚本。放进引号的话先回原文核对，再按来源层级标出处；网上常见的错引另有易错清单。
3. **按处境找模式。** `find_patterns.py` 把你的处境和 393 个模式的触发条件逐一比对，只把最合用的几个交给模型，不让成堆的材料挤掉分析。
4. **像他那样想，不是像他那样说。** 第三人称，不扮演，原话一般只用零到三条。交出回答前按 13 条自检：账算到能定下来没有，每个相关方按动机推演过没有，检查点能不能计数，等等。
5. **有边界。** 不帮人把同事、家人当敌人，不出整人的方案，改给对事不对人的办法，见[示例 3](examples/03-想斗倒老员工.md)。
6. **盲评回测。** 同一个模型分别装新旧两版回答 6 个问题，由 AI 盲评：新版胜 3 题、平 3 题，没有错引；查出处的一题新版 77 分，旧版 57 分。方法和局限见[回测](docs/EVALUATION.md)。
7. **轻量、离线。** 脚本只用 Python 标准库。

## 一个例子

> **问**：我们是一家 12 人的 B2B SaaS 创业公司……最大的客户占收入 60%，最近还在要求大量定制。账上现金够撑 10 个月。一家行业大厂提出收购意向，估值……比我们心理预期低一半，还要求创始团队留任三年。另一个选择是去融一轮钱，但……投资人说要先看到客户集中度下降。我该怎么想这件事？
>
> **答**（节选）：先说判断：不必马上在「按这个价卖」和「去融资」之间二选一，也不要回绝收购。收购方压价、投资人设条件、大客户要定制，是同一个弱点在三处的表现：一家客户撑着六成收入。问题要换个问法：在 10 个月的现金里，能不能把这个弱点改善到足以改变价格？能，就先改，再拿新数字去谈；改不了，这份报价就是你的保险，要趁手里还有余地把条件谈好。

完整回答和另外三个例子在 [examples/](examples/)。

## 两个版本怎么选

仓库里有两个 skill，方法、393 个模式、原文核验都一样，区别只在晚年（1957–1976）部分的写法：

| | 标准版（默认）<br>`mao-lifelong-counsel` | 完整版<br>`mao-lifelong-counsel-full` |
|---|---|---|
| 晚年理论（继续革命等） | 照样完整介绍，作为思想史，不当作今天的行动建议，不作褒贬 | 按他本人的论述，正面用于决策：下决心、做到底、胜利后不停步 |
| 对他的外部评价 | 不收录任何评价，包括正式结论和研究著作 | 写明不引用、不转述 1981 年和 2021 年两份历史决议 |
| 晚年事件 | 写「他的论述」和「经过」两栏 | 另有一栏「决策启示」（9 处） |
| 方法卡 21 | 「经常检查和改造自己」 | 「斗私批修，不断改造自己」 |

不确定就用标准版。两个版本不要同时装，否则会一起被触发。逐条差别见 [docs/VERSIONS.md](docs/VERSIONS.md)。

## 安装

下面的命令装的是标准版；括号里是装完整版的写法。

**方式一：一条命令**（需要 Node.js 22.20 以上）

```bash
npx skills add LITTLECAT2333/mao-zedong-skill --skill mao-lifelong-counsel -g
```

完整版把 `--skill` 后面换成 `mao-lifelong-counsel-full`。

**方式二：安装脚本**

```bash
git clone https://github.com/LITTLECAT2333/mao-zedong-skill.git
cd mao-zedong-skill
```

- Windows：`powershell -ExecutionPolicy Bypass -File install\install.ps1`（装给 Codex），加 `-Target claude` 装给 Claude Code（完整版再加 `-Edition full`）
- macOS / Linux：`sh install/install.sh`（装给 Codex），或 `sh install/install.sh claude`（完整版：`sh install/install.sh codex full`）

**方式三：手动复制**

把 `skills/mao-lifelong-counsel`（完整版是 `skills/mao-lifelong-counsel-full`）整个文件夹复制到：

- Codex：`~/.codex/skills/` 或 `~/.agents/skills/`（只放一处，免得出现两个同名 skill）
- Claude Code：`~/.claude/skills/`

装好后重启工具。

**关于原文库**：仓库默认不带原文库，原因见 [docs/SOURCES.md](docs/SOURCES.md)。没有原文库时，skill 照样能分析问题，只是原话一律按「未核到」处理，不加引号。原文库的目录结构和安装方法见 [kb/README.md](skills/mao-lifelong-counsel/kb/README.md)。

## 怎么用

- Codex：`$mao-lifelong-counsel 帮我分析：……`（完整版是 `$mao-lifelong-counsel-full`），或者直接说「用毛泽东的方法帮我想想这件事」。
- Claude Code 等：提到毛泽东思想方法、毛选、「教员的方法」时会自动加载。

问的时候尽量给事实：数字、时间、涉及哪几方、你手里有什么、期限是多久。更多见 [docs/USAGE.md](docs/USAGE.md)。

## 它是怎样做出来的

```mermaid
flowchart LR
  A["分层原文库<br/>约 9,300 篇"] --> B["思维切片卡<br/>约 1.3 万张"]
  B --> C["按 14 个领域聚类"]
  C --> D["思维模式 393 个"]
  D --> E["find_patterns.py<br/>按处境检索"]
  E --> F["按主线分析<br/>thinking-engine.md"]
  F --> G["verify_quote.py<br/>逐字核验"]
  G --> H["回答"]
```

每张卡记下一段原文里的场景、思维动作、观点、原话和边界；讲同一个思维动作、跨好几个年代的卡，归纳成一个模式。详见 [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md)。

## 局限

- 它复原的是他留在文字里的思考方法，不是他本人。差别在哪里，见[工作原理](docs/HOW_IT_WORKS.md#它和真人有什么不同)。
- 回答的质量取决于你给的事实；事实不全时，结论只是假设，回答里会说明。
- 部分原文来自扫描件 OCR，个别字可能有误。回测样本小，评审也是 AI。
- 不替代医疗、法律、财务、心理方面的专业意见。

## 参与

最有用的贡献是报告错引：用 Issues 里的「错引报告」模板，写清句子、标的出处和你查到的情况。其他见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

代码采用 MIT（[LICENSE](LICENSE)）；本项目撰写的文字采用 CC BY-NC-SA 4.0（[LICENSE-CONTENT.md](LICENSE-CONTENT.md)）。引用的原文，著作权状态以原出版物为准。

---

## English

**mao-lifelong-counsel** is a Chinese-language Agent Skill (SKILL.md) for Codex, Claude Code and other Agent-Skills-compatible tools. It helps an AI think through decisions and trends with the methods Mao Zedong documented in his own writings: investigation before judgment, finding the principal contradiction, weighing forces and time, thinking from the other side, planning in stages with fallback options.

- **393 thinking patterns** distilled from about 13,000 annotated excerpts, in 14 domains; 375 of them are backed by quotes from three or more decades.
- **Word-for-word quote verification** against a tiered corpus of about 9,300 documents (the corpus itself is not bundled, for copyright reasons; see [docs/SOURCES.md](docs/SOURCES.md)).
- **Pattern retrieval** (`find_patterns.py`) so the model reads only the few patterns that fit the situation.
- Third person, no role-play, zero to three quotes per answer; it will not help users target real people.
- Blind backtest against the previous version: 3 wins, 3 ties, no misquotes ([details](docs/EVALUATION.md)).
- Two editions with the same methods and patterns. The default `mao-lifelong-counsel` presents his late-period (1957–1976) theory as intellectual history, not as advice. `mao-lifelong-counsel-full` keeps the original framing, which applies that theory to decisions. Install only one ([comparison](docs/VERSIONS.md)).

Install: `npx skills add LITTLECAT2333/mao-zedong-skill --skill mao-lifelong-counsel -g`, or copy `skills/mao-lifelong-counsel` into `~/.codex/skills/` (Codex) or `~/.claude/skills/` (Claude Code), then restart the tool.
