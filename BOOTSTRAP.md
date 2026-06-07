# LLM Wiki 仓库自举提示词（Bootstrap Prompt v3.1）

> **本文件用途**：将本文件复制到任意空白目录，交给一个具备文件系统与 Shell 工具的 AI Agent（如 Cursor、Claude Code、OpenCode 等）。
> Agent 阅读本文件后，将在该目录中**完整创建**一个符合 LLM Wiki 规范的三层知识操作系统。
>
> **核心理念**：Raw 层（只读事实池，三类子目录固定，Agent 完全不动）/ Wiki 层（Agent 完全拥有的结构化知识编译层）/ Graph 层（结构健康层）。
> Raw 层目录决定加注类型、引文保真、诠释强制加注、Agent 不做主观裁判、增量合并、冲突升级人工裁决、默认自动执行例外才挂起。

---

## 0. 你（Agent）的任务总览

你即将在目标目录（`$TARGET_DIR`）中产出一个**可直接使用的 LLM Wiki 仓库**。完成时，目录结构必须严格如下：

```text
$TARGET_DIR/
├── AGENTS.md                  # 最高操作契约（按本文档 §2 写入）
├── README.md                  # 仓库使用说明（研究者视角）
├── .gitignore                 # 排除索引、缓存与编辑器配置
├── Raw/                       # 只读事实池（Agent 严禁读写之外的任何操作）
│   ├── README.md
│   ├── Sources/               # 他人文档：论文、剪藏、技术规范、书籍
│   ├── Thoughts/              # 自己写的研究笔记、思辨、逻辑推演
│   ├── Records/               # 个人记录：交易日志、聊天记录、复盘日记
│   └── Assets/                # 图片 / PDF 附件（Obsidian 附件库路径）
├── Wiki/                      # 知识编译层（Agent 完全拥有并动态维护）
│   ├── index.md               # 词条目录
│   ├── log.md                 # 操作日志（只增不改）
│   ├── overview.md            # 跨领域活体综述
│   ├── concepts/              # 概念词条（绝对平铺，禁止子文件夹）
│   ├── entities/              # 实体词条（人物 / 机构 / 著作 / 事件）
│   ├── sources/               # 长文 / 原著的 AI 摘要映射
│   ├── syntheses/             # 综述归档（查询答案沉淀）
│   └── disambiguations/       # 消歧义专页
├── Graph/                     # 结构健康层（自动生成，勿手动修改）
│   ├── README.md
│   └── reports/               # 图谱审计报告
└── Tools/                     # 独立工具脚本
    ├── README.md
    ├── health.py              # 结构完整性检查（零 LLM 调用，每次会话必跑）
    ├── lint.py                # 语义与冲突审计（消耗 token）
    └── build_graph.py         # 知识图谱构建与孤岛分析
```

---

## 1. 执行工作流（严格按序）

### 1.0 创建步骤追踪清单

**首先**通过 Agent 可用的任务追踪机制（`todowrite` / `TodoWrite` / 内联 Markdown 清单，视 Agent 环境自动选择）创建追踪清单，步骤 0 本身立即标记完成，其余初始为待处理。每完成一步立即更新状态，最终输出前确认清单全部完成：

- [x] 0. 创建步骤追踪清单
- [ ] 1. 向用户询问关键配置
- [ ] 2. 验证并清理目标目录
- [ ] 3. 创建物理目录结构
- [ ] 4. 写入 `AGENTS.md`
- [ ] 5. 写入 `README.md`
- [ ] 6. 写入 `.gitignore`
- [ ] 7. 写入各层 `README.md`
- [ ] 8. 写入工具脚本骨架
- [ ] 9. 写入 `Wiki/` 初始核心文件
- [ ] 10. 初始化 Git 仓库
- [ ] 11. 追加 bootstrap 记录到 `log.md`
- [ ] 12. 首次 Git 提交
- [ ] 13. 最终验证与报告

### 1.1 向用户询问关键配置

**在写入任何文件之前**，通过一次对话确认以下信息。若用户拒绝回答或说"用默认"，使用括号内的默认值：

1. **检索工具**：使用 `qmd`（推荐）还是其他工具？（默认：`qmd`，不可用则降级为纯文本扫描）
2. **本地 LLM**：是否使用本地 LLM 服务？若是，提供启动命令。（默认：不配置，相关步骤标注"按需配置"）
3. **Git 远程**：是否配置 `origin`？若是，提供 URL。（默认：暂不配置）

### 1.2 验证目标目录

```bash
ls -la "$TARGET_DIR"
```

- 不存在 → `mkdir -p "$TARGET_DIR"`，继续
- 已存在但非空 → 警告用户，要求显式确认是否覆盖
- 已存在且为空 → 直接继续

### 1.3 创建物理目录结构

用 `mkdir -p` 一次性创建 §0 列出的所有目录。注意：

- `Wiki/` 下各子目录**绝对禁止**再建子文件夹
- `Raw/` 下**仅**预建 `Sources/`、`Thoughts/`、`Records/`、`Assets/` 四个固定子目录，严禁新增其他子目录
- `Graph/reports/` 初始为空目录

### 1.4 写入 `AGENTS.md`

使用本文档 §2 的完整模板，按以下规则替换所有占位符：

| 占位符 | 替换为 |
|--------|--------|
| `<YYYY-MM-DD>` | 今日日期（ISO 8601） |
| `<retrieval-tool>` | 用户确认的检索工具名（默认 `qmd`） |
| `<retrieval-tool-embed>` | 对应的索引更新命令（如 `qmd embed --collection wiki`） |
| `<local-llm-cmd>` | 本地 LLM 启动命令；若无则写 `# 按 Tools/README.md 配置` |

### 1.5 写入 `README.md`

内容要点（用第二人称，5 分钟内可读懂）：

- 一句话定位：这是个人 LLM 知识库，`Raw/` 放原始材料，`Wiki/` 是结构化沉淀
- **Raw 层三类目录说明**：
  - `Sources/`：放他人文档（论文、剪藏、书籍）→ Agent 摄入时加注 `（据文献）`
  - `Thoughts/`：放自己写的研究笔记与思辨 → Agent 摄入时加注 `（个人分析）`
  - `Records/`：放个人记录（交易日志、聊天记录、日记）→ Agent 摄入时加注 `（个人经验）`
- **三步上手**：
  1. 把文件放进 `Raw/` 对应子目录
  2. 在 AI 会话中说 `ingest` 触发摄入
  3. 说 `query: <问题>` 触发查询
- **Obsidian 设置提示**（高亮显示）：`Settings → Files and links` 中将 Attachment 路径设为 `Raw/Assets`，关闭 WikiLinks（改用绝对路径）
- 工具脚本一览：列出 `Tools/` 下所有脚本及触发词
- 关键约定：`Raw/` 完全只读，Agent 只读取，不做任何修改或移动

### 1.6 写入 `.gitignore`

```gitignore
# 检索索引（本地自动生成）
.qmd/
.rag/
.vsearch/

# Python 缓存
__pycache__/
*.pyc
*.pyo

# Obsidian 工作区配置
.obsidian/
workspace.json

# 图谱与工具缓存
Graph/.cache.json

# 临时诊断文件
Wiki/_semantic_lint_context.md
*.tmp

# OS 文件
.DS_Store
Thumbs.db
```

### 1.7 写入各层 `README.md`

**`Raw/README.md`**：
```markdown
# Raw 层说明

本目录是原始事实池，Agent 对此目录只读，不做任何修改或移动。

## 三类固定子目录

| 目录 | 存放内容 | Wiki 摄入时的加注类型 |
|------|----------|----------------------|
| `Sources/` | 他人文档：论文、剪藏、技术规范、书籍 | `（据文献）` |
| `Thoughts/` | 自己写的研究笔记、思辨、逻辑推演 | `（个人分析）` |
| `Records/` | 个人记录：交易日志、聊天记录、复盘日记 | `（个人经验）` |
| `Assets/` | 图片 / 附件（请在 Obsidian 中绑定此目录） | — |

哪些文件已被摄入，通过 `Wiki/log.md` 追踪，无需物理归档。

**核心规则**：Agent 严禁修改或移动 Raw/ 内任何文件，只有读取权限。
```

**`Graph/README.md`**：
```markdown
# Graph 层说明

存放 `build graph` 自动生成的知识图谱数据，请勿手动修改。

- `graph.json`：节点与边的结构化数据
- `graph.html`：基于 vis.js 的可交互可视化页面
- `reports/`：图谱健康报告（`build graph --report` 生成）
```

**`Tools/README.md`**：
```markdown
# Tools 层说明

| 脚本 | 触发词 | LLM 调用 | 频率 |
|------|--------|---------|------|
| `health.py` | `health` | 零 | 每次会话必跑 |
| `lint.py` | `lint` | 是（消耗 token） | 每 10–15 次摄入后 |
| `build_graph.py` | `build graph` | 否 | 按需 |

本地 LLM 配置：<local-llm-cmd>
```

### 1.8 写入工具脚本骨架

三个脚本均为**占位骨架**，每个文件必须满足：
- 文件头注释：说明脚本用途、依赖、调用方式
- 提供 `if __name__ == "__main__":` 入口
- 打印"⚠️ 骨架待实现，请参考 AGENTS.md 对应章节补全逻辑"
- `python Tools/health.py` 不得报语法错误

**`Tools/health.py`** 骨架：
```python
"""
health.py — 结构完整性检查（零 LLM 调用）
用途：检查空文件、索引同步、日志覆盖、断链
依赖：Python 3.8+ 标准库
调用：python Tools/health.py [--json] [--save]
"""

if __name__ == "__main__":
    print("⚠️ 骨架待实现，请参考 AGENTS.md §七 补全检查逻辑")
```

`lint.py` 和 `build_graph.py` 按同样结构写入，分别引用 `AGENTS.md §八` 和 `§九`。

### 1.9 写入 Wiki 初始核心文件

**`Wiki/index.md`**：
```markdown
# Wiki Index

## Overview
- [Overview](overview.md) — 跨领域活体综述

## Concepts
<!-- 摄入后自动填入 -->

## Entities
<!-- 摄入后自动填入 -->

## Sources
<!-- 摄入后自动填入 -->

## Syntheses
<!-- 查询归档后自动填入 -->

## Disambiguations
<!-- 消歧词条后自动填入 -->
```

**`Wiki/overview.md`**：
```markdown
# 跨领域活体综述

> 本文件由 Agent 维护，随每次摄入自动更新。触发条件：当本次摄入产生了跨领域的新联系或修正了已有综述判断时。

<!-- 首次摄入后自动生成内容 -->
```

**`Wiki/log.md`**（bootstrap 记录在 §1.11 写入）：
```markdown
# Wiki 操作日志

<!-- 格式：## [YYYY-MM-DD] <操作> | <标题> -->
<!-- 操作类型：bootstrap / ingest / query / query-synthesis / health / lint / graph / chore / ERROR -->
```

### 1.10 初始化 Git 仓库

```bash
cd "$TARGET_DIR"
git init
git add AGENTS.md README.md .gitignore Raw/ Wiki/ Graph/ Tools/
```

### 1.11 追加 bootstrap 记录到 `log.md`

`Wiki/log.md` 末尾追加（将 `<YYYY-MM-DD>` 替换为当天日期）：
```
## [<YYYY-MM-DD>] bootstrap | LLM Wiki OS v3.1 骨架建立
```

### 1.12 首次 Git 提交

```bash
git commit -m "chore: bootstrap LLM Wiki OS v3.1"
```

若用户在 §1.1 提供了远程仓库 URL：
```bash
git remote add origin <URL>
git push -u origin main
```

### 1.13 最终验证与报告

打印：
- 完整目录树（`find . -type f | sort`）
- `git log --oneline`
- 下一步操作提示：
  > 1. 把他人文档放进 `Raw/Sources/`，自己的笔记放进 `Raw/Thoughts/`，个人记录放进 `Raw/Records/`
  > 2. 在 AI 会话中说 `ingest` 触发摄入
  > 3. 说 `query: <问题>` 触发查询
  > 4. 说 `health` 检查仓库健康状态

---

## 2. AGENTS.md 模板（Agent 请将以下内容完整写入目标库）

---

# AGENTS.md（最高操作契约）

本文件是 Agent 每次执行前**必读**的最高宪法。所有工作流、规则、模板均以本文件为唯一权威来源。

---

## 会话启动规程（每次新会话必须首先执行）

```
1. 运行 health 检查（见§七）
2. 读取 Wiki/log.md 最近 10 条记录，了解上次会话的操作上下文
3. 读取 Wiki/index.md，获取当前知识库词条全貌
4. 报告：健康状态摘要 + 上次会话摘要 + 当前词条数
5. 等待研究者指令
```

> **为什么**：Agent 没有跨会话记忆，上述步骤是建立上下文的最低成本方式，避免每次都要研究者重新交代背景。

---

## 快速触发指令

| 指令 | 触发工作流 | 说明 |
|------|-----------|------|
| `ingest` | 裸摄入 | 扫描 `Raw/`，处理所有未摄入文件 |
| `ingest <file>` | 摄入特定文件 | 处理指定文件并归档 |
| `query: <问题>` | 查询工作流 | 先查 Wiki，盲区回退至 Raw，新洞见自动织网 |
| `health` | 健康检查 | 结构完整性检查（零消耗，每次会话必跑） |
| `lint` | 质量审计 | 孤儿页、矛盾、盲区检查（每 10–15 次摄入跑一次） |
| `build graph` | 图谱分析 | 生成上帝节点、脆桥报告 |
| `graph report` | 图谱健康报告 | 输出结构分析 |
| `<retrieval-tool> reindex` | 重建检索索引 | Raw + Wiki 双集合重建 |

或用自然语言描述，Agent 自行映射到对应工作流。

**执行纪律**：Agent 启动任何工作流前，通过当前 Agent 环境可用的任务追踪机制（`todowrite` / `TodoWrite` / 内联 Markdown 清单）创建该工作流各步骤的追踪清单，每完成一步更新一次状态。

---

## 一、Vault 根目录与路径规范

**【根目录定义】**：本契约所有路径及 Obsidian `[[双链]]` 均以 Vault 根目录（即包含 `AGENTS.md`、`Raw/`、`Wiki/`、`Graph/`、`Tools/` 的那一层）为唯一基准面。

**【双链绝对化】**：所有指向 Raw 层或 Wiki 层的链接，必须使用基于 Vault 根目录的绝对路径，严禁使用 `../` 等相对路径，确保 Obsidian Graph View 完整织网。

示例：`[[Wiki/concepts/复杂系统.md]]`、`[[Raw/Sources/某论文.md]]`

**【物理分层结构】**：

```
Vault 根目录/
├── AGENTS.md
├── README.md
├── Raw/                       ← 只读，Agent 严禁修改或移动任何文件
│   ├── Sources/               ← 他人文档
│   ├── Thoughts/              ← 自己的研究笔记
│   ├── Records/               ← 个人记录
│   └── Assets/                ← 附件
├── Wiki/
│   ├── index.md
│   ├── log.md                 ← 追踪已摄入文件的唯一依据
│   ├── overview.md
│   ├── concepts/              ← 绝对平铺，禁止子文件夹
│   ├── entities/
│   ├── sources/
│   ├── syntheses/
│   └── disambiguations/
├── Graph/
│   └── reports/
└── Tools/
```

---

## 二、Raw 层目录与加注规则

Raw 层固定三类子目录，Agent 根据文件所在目录**自动确定加注类型**，无需猜测。这是防止语义漂移的核心机制。

| Raw 子目录 | 存放内容 | Wiki 摄入加注 | 摘要策略 |
|------------|----------|--------------|----------|
| `Sources/` | 他人文档：论文、剪藏、技术规范、书籍 | `（据文献）` | 引文保真；他人观点与推论一律加注 |
| `Thoughts/` | 自己写的研究笔记、思辨、逻辑推演 | `（个人分析）` | 提炼核心论点；个人判断加注 |
| `Records/` | 个人记录：交易日志、聊天记录、复盘日记 | `（个人经验）` | 提炼决策逻辑与经验结论；主观内容加注 |
| `Assets/` | 图片、PDF 附件 | — | 不摄入，仅供其他文件引用 |

**【加注执行规则】**：

- `Sources/` 文件摄入时：
  - 原始笔记中明确带引号或标注"原文"的内容 → 保真复现，不加注（视为基础事实）
  - 他人文章中的推论、观点、概括 → 写入 Wiki 时强制加注 `（据文献）`
  - 示例：`某理论认为 X 是 Y 的充分条件（据文献）。`

- `Thoughts/` 文件摄入时：
  - 研究者自己的分析判断、逻辑推演 → 写入 Wiki 时强制加注 `（个人分析）`
  - 示例：`休谟的同一性论证在数量与统一性边界处存在逻辑断层（个人分析）。`

- `Records/` 文件摄入时：
  - 所有主观内容、决策记录、经验总结 → 写入 Wiki 时强制加注 `（个人经验）`
  - 示例：`动量策略在高隐含波动率环境下失效概率显著上升（个人经验）。`

**【禁止主观裁判】**：Agent 仅作为"知识整合编译器"，不得独立判断哪种研究观点或诠释"更正确"。

**【禁止自我引用】**：严禁将 Agent 自己之前在 Wiki 词条里写就的总结性言论，作为推导或佐证新事实的"客观证据"。禁止将查询合成内容作为后续推理的"客观依据"。

**【查询合成加注】**：由查询工作流跨词条合成产生的新推论，必须加注 `（据查询合成）`。

---

## 三、词条元数据与排版规范

### 3.1 标准概念词条（`Wiki/concepts/`，命名：中文概念名 或 `TitleCase.md`）

```markdown
---
title: "<精确的概念名称>"
type: concept
aliases: ["<英文名>", "<同义词>", "<缩写>"]
domain: "<根据文件所在 Raw/ 子目录或内容自动判断，自由填写>"
subdomain: "<可选，进一步细分>"
era: "<可选：历史时代 / 年份 / 无>"
tags: []
sources: ["[[Raw/<子目录>/<路径>/...]]"]
related: ["[[Wiki/concepts/相关概念A.md]]"]
# related 字段预留语义边注释（可选，用于未来图谱扩展）：
# - "[[Wiki/concepts/概念B.md]] # supports"
# - "[[Wiki/concepts/概念C.md]] # contradicts"
# - "[[Wiki/concepts/概念D.md]] # extends"
# - "[[Wiki/concepts/概念E.md]] # depends_on"
event_date:                    # 可选：知识内容指向的业务/历史时间，非操作时间（格式 YYYY-MM-DD）
last_updated: YYYY-MM-DD
pending_review: false
---

## 📌 核心定义
（150 字以内，精准的本质定义，严禁前言后语）

## 🎯 核心论点与逻辑演进
（无序列表 `-` 结构化呈现。加注规则见§二：据文献 / 个人分析 / 个人经验 / 据查询合成）

## ⚖️ 边界防御与相近概念区分
* 对比 **[[Wiki/concepts/相近概念X.md]]**：指出本质区别，严禁语义串味。

## 🔗 关联实体
- [[Wiki/entities/相关人物或著作.md]]

## 📜 原始事实追溯
* 来源：[[Raw/<子目录>/<路径>/某原始笔记文件名.md]]
```

### 3.2 实体词条（`Wiki/entities/`，命名：`TitleCase.md`）

**【Concept 与 Entity 边界定义】**：

- **归入 Concept**：抽象的策略、定理、机制、算法、方法论、思想体系。判断标准：可复现、可泛化、不绑定唯一历史实例。例："Bull Put Spread"（期权策略）、"动量效应"（市场机制）、"涅槃"（佛教概念）、"协整"（统计方法）。
- **归入 Entity**：具有唯一历史身份的具体对象。判断标准：存在唯一时空坐标，无法被泛化复现。例：特定人物（David Hume）、现实公司/机构（Federal Reserve）、已发生的独立事件（2008年金融危机）。
- **边界判断规则**：若对某对象能问"这个概念在其他场合还适用吗？"且答案为"是"，归 Concept；若只能问"这件事发生过吗？"，归 Entity。

著作类实体若已有 `Wiki/sources/` 摘要页，实体词条的 `raw_link` 指向摘要页而非重复摘要内容，实体词条只存身份信息与关联概念。

```markdown
---
title: "<人名 / 著作名 / 机构名 / 事件名>"
type: entity
entity_type: <person | work | institution | event>
tags: []
sources: ["[[Raw/<子目录>/<路径>/...]]"]
last_updated: YYYY-MM-DD
---

## 简介
（100 字以内）

## 核心关联概念
- [[Wiki/concepts/概念A.md]]

## 📜 原始事实追溯
* 来源：[[Raw/<子目录>/<路径>/某原始笔记文件名.md]]
```

### 3.3 长文 / 原著摘要映射（`Wiki/sources/`，命名：`kebab-case.md`）

仅由 `Raw/Sources/` 的文件触发。实体词条中同名著作的 `raw_link` 指向本页，不重复摘要。

```markdown
---
title: "<书名 / 长文标题>"
type: source_map
author: "<作者>"
raw_link: "[[Raw/Sources/<路径>/...]]"
last_updated: YYYY-MM-DD
---

## 📑 整体脉络与摘要

## 💡 核心抽取概念
（向 Wiki/concepts/ 建立辐射双链）
- [[Wiki/concepts/概念A.md]]：一句话说明关联（据文献）

## 📜 章节要点
```

### 3.4 消歧导航页（`Wiki/disambiguations/`，严禁套用上述模板）

```markdown
---
title: "<冲突词>"
type: disambiguation
last_updated: YYYY-MM-DD
---

本词条在不同传统或领域下存在多个完全独立的实质含义，请选择对应专页：

- [[Wiki/concepts/概念（流派A）.md]] — 流派 A 视角的核心要义
- [[Wiki/concepts/概念（流派B）.md]] — 流派 B 视角的核心要义

> ⚠️ 审计守则：若原始笔记未明确指明流派或语境，默认不写入任何消歧专页，输出警告，挂起等待研究者人工确认后分配。
```

### 3.5 综述页（`Wiki/syntheses/`，命名：`kebab-case.md`）

```markdown
---
title: "<查询问题或分析主题>"
type: synthesis
tags: []
sources: ["[[Wiki/concepts/...]]"]
status: open | closed              # 可选：open=问题仍开放，closed=已有确定结论
open_questions: []                 # 可选：本综述尚未解决的子问题列表
event_date:                        # 可选：综述内容指向的业务/历史时间（格式 YYYY-MM-DD）
last_updated: YYYY-MM-DD
---

## 结论

## 论据与引用
- [[Wiki/concepts/概念A.md]]：……（据查询合成）
```

---

## 四、摄入工作流（Ingest Workflow）

**触发**：`ingest` 或 `ingest <file>`

**前提原则**：凡研究者放入 `Raw/` 的文件，均视为已确认需要摄入，Agent 不做二次价值判断。

**支持格式**：`.md` 直接摄入；`.pdf`、`.docx`、`.pptx`、`.xlsx`、`.html`、`.txt`、`.epub` 等通过 [markitdown](https://github.com/microsoft/markitdown) 自动转换后摄入。`Raw/Assets/` 下的附件不摄入。

**执行步骤（严格按序）**：

**0. 创建追踪清单**：通过当前 Agent 环境可用的任务追踪机制初始化清单，步骤 0 本身设为完成，其余待处理。

**1. 确定加注类型**：读取文件路径，根据 §二 的目录映射表确定本文件的加注类型（`据文献` / `个人分析` / `个人经验`）。此步骤无需检索，直接由路径决定。

**2. 检索预扫描**：摄入前，用检索工具定位已有相关内容：
```bash
<retrieval-tool> query "<核心概念关键词>" --collection wiki --format files --min-score 0.4
```
- 命中得分 ≥ 0.4 的 Wiki 词条 → 进入增量合并流程（见§五）
- 无命中 → 进入新建词条流程

**3. 读取源文件**：完整读取（非 Markdown 先自动转换）。

**4. 读取 Wiki 上下文**：读取 `Wiki/index.md` 和 `Wiki/overview.md` 获取当前全貌。

**5. 执行摄入**：默认全自动执行，仅以下两类情况挂起：

**情况 A — 检测到冲突信号**，挂起并呈现冲突详情（见§五 5.2）：
- 核心定义段出现直接否定关系（新料：A 是 X；已有词条：A 不是 X）
- 数值、年份、因果方向明确冲突
- 同一词汇在新料与已有词条中指向完全不同的对象（触发消歧，见§五 5.3）

**情况 B — 技术性失败**，写入 ERROR 日志，跳过该文件继续处理队列：
- 文件损坏或编码异常，Agent 无法读取内容
- 文件转换失败（markitdown 报错），且研究者未提供备用格式

> **新建词条无需确认**：直接写入，工作流结尾输出"本次新建词条汇总"供研究者复盘。

**6. 新建或增量合并词条**（见§五）：在 `Wiki/` 对应子目录下创建或更新词条，严格执行 §二 加注规则。

**7. 更新索引与综述**：
- 更新 `Wiki/index.md`，在对应分类下添加条目
- 若本次摄入产生了跨领域新联系或修正了已有综述判断，更新 `Wiki/overview.md`

**8. 摄入后验证**：检查新词条中所有 `[[双链]]` 是否指向已存在页面；若存在断链，输出警告并记录。

**9. 追加日志**（这是判断文件已摄入的唯一依据）：
```
## [YYYY-MM-DD] ingest | <标题> | [[Raw/<子目录>/<路径>/<文件名>]]
```
日志条目中必须包含指向原文的双链，以便后续 health 检查和裸摄入扫描正确识别已处理文件。

**10. Git 提交**（严禁 `git add Raw/`，Raw/ 由研究者自行管理）：
```bash
git add Wiki/
git commit -m "ingest: <标题>"
```

**11. 更新检索索引**：
```bash
<retrieval-tool> embed --collection wiki
```

**12. 工作流结尾汇总**：输出本次摄入的新建词条列表与 ERROR 记录数量（若有）。

### 摄入处理顺序建议（效率优化，不影响是否处理）

| 顺序 | 优先处理 | 原因 |
|------|----------|------|
| 1 | `Raw/Thoughts/` 下有明确概念标题（H1/H2）的精修笔记 | 结构清晰，词条边界明确，合并质量最高，作为基石节点 |
| 2 | `Raw/Sources/` 下已含 `[[双链]]` 的结构化笔记 | 关联关系已预标注，图谱织网效率高 |
| 3 | `Raw/Records/` 下的聊天记录、日记、流水账 | 需更多拆分判断，后处理避免阻塞队列 |

---

## 五、增量合并与冲突处理协议

### 5.1 增量合并

新笔记摄入时，先检索 `Wiki/` 是否已有对应词条：
- **无**：根据对应模板新建词条
- **有**：对比 Diff，将新物料细节无缝缝合进对应章节，严禁粗暴覆盖旧词条

### 5.2 冲突处理协议

以下任一情况视为冲突，禁止 Agent 自行裁判，强制挂起：
- 核心定义段出现直接否定关系（新料与已有词条对同一命题给出相反断言）
- 数值、年份、因果方向明确不一致
- 同一词汇在新料与已有词条中指向完全不同的对象

冲突处理格式，强制写入词条：

```markdown
> ⚠️ 争议：
> - 说法 A（来源：[[Raw/<子目录>/<路径>/旧笔记.md]]）：……
> - 说法 B（来源：[[Raw/<子目录>/<路径>/新文件.md]]）：……
> 待研究者人工裁决。
```

同时将该词条 YAML 中的 `pending_review` 强行修改为 `true`，挂起等待研究者指示。

### 5.3 消歧触发规则

一旦发现同一词汇在不同传统或领域下存在实质性定义撕裂：
1. 将原词条升级为消歧导航页（套用 §3.4 模板）
2. 为每个独立含义创建独立词条（文件名：`概念（流派）.md`）
3. 若原始笔记未明确指明流派，输出警告，挂起等待人工确认，不强行分配

---

## 六、查询工作流（Query Workflow）

**触发**：`query: <问题>` 或自然语言提问

查询工作流不只是被动回答，而是知识库生长的主动驱动器。每次查询可能触发三个层次的生长机制。

**执行步骤**：

**0. 创建追踪清单**。

**1. 语义主检索**：
```bash
<retrieval-tool> query "<问题关键词>" --collection wiki --format json -n 8
```
读取命中词条，综合答案，使用 `[[词条名]]` 内联引用标注来源。

**【富格式输出契约】**：根据问题特质主动丰富输出形式：
- **结构化对比**（多流派 / 配置 / 策略对比）→ 提供 Markdown 对比表格
- **数值序列 / 趋势**（数据指标对比）→ 附带 Python matplotlib 绘图代码或 ASCII 趋势图
- **汇报演示**（用户明确提到汇报、演示）→ 使用 Marp Markdown 幻灯片格式输出

**2. 盲区回退**：若 Wiki 集合无命中（得分均低于 0.4），降级检索 Raw 集合：
```bash
<retrieval-tool> query "<问题关键词>" --collection raw --format json -n 8
```
- Raw 命中 → 基于原始笔记作答，末尾附注警告，同时触发生长层次二（见下）
- Raw 仍无命中 → 告知研究者该主题存在知识盲区，建议补充原始笔记

**【生长层次一：综述归档】**：询问用户是否将本次查询答案归档至 `Wiki/syntheses/<slug>.md`。归档后：
```bash
git add Wiki/index.md Wiki/log.md Wiki/syntheses/<slug>.md
git commit -m "query-synthesis: <问题简写>"
<retrieval-tool> embed --collection wiki
```

**【生长层次二：盲区驱动摄入】**：当 Raw 命中时，强制询问：
> ⚠️ 检测到知识盲区：Wiki 层对「<问题关键词>」覆盖不足，但在 Raw 层发现相关文件：
> - `[[Raw/<子目录>/<路径>/xxx.md]]`
> 是否立即对上述文件执行 ingest 以填补盲区？（Y/N）

用户确认后，直接触发摄入工作流（§四）。

**【生长层次三：跨词条合成回哺】**：当同时满足以下两个客观条件时，自动提示归档选项：
- 答案综合了 **3 个及以上**不同 Wiki 词条
- 答案包含原有词条中**未曾出现**的跨概念推论或对比洞见

提示用户确认后执行：
- 将跨词条洞见以 `（据查询合成）` 加注，缝合进相关词条的 `🎯 核心论点` 章节
- 在这些词条的 `related` 字段中补入新发现的关联词条双链
- 更新 `last_updated` 为当日日期
- 追加日志：`## [YYYY-MM-DD] query-synthesis | <问题关键词>`
- Git 提交：
  ```bash
  git add Wiki/concepts/ Wiki/log.md
  git commit -m "query-feedback: <问题关键词> 跨词条回哺"
  ```

**回哺硬性约束**：
- 回哺内容必须加注 `（据查询合成）`，严禁伪装成一手事实
- 若回哺内容与词条既有内容存在矛盾，强制走冲突处理协议（§五 5.2），不得静默覆盖

---

## 七、健康检查工作流（Health Workflow）

**触发**：`health` | **频率**：每次会话启动规程中必跑 | **成本**：零 LLM 调用

运行：`python Tools/health.py [--json] [--save]`

检查项：
- **空文件 / 存根页**：仅有 frontmatter、无正文内容的页面
- **索引同步**：`Wiki/index.md` 条目与磁盘实际文件是否一致
- **日志覆盖**：有词条页面但 `Wiki/log.md` 中缺少对应摄入记录的情况
- **断链检查**：`[[双链]]` 指向不存在页面的情况
- **Raw 目录合规**：`Raw/` 下是否存在 `Sources/`、`Thoughts/`、`Records/`、`Assets/` 以外的子目录（提示研究者手动整理）

`--save` 参数将报告写入 `Wiki/health-report.md` 并 Git 提交。

---

## 八、质量审计工作流（Lint Workflow）

**触发**：`lint` | **频率**：每 10–15 次摄入后执行一次 | **前提**：必须在 health 通过后运行

运行：`python Tools/lint.py`

检查项：
- **孤儿页**：无任何入站 `[[链接]]` 的 Wiki 页面
- **断链**：`[[双链]]` 指向不存在页面
- **内容矛盾**：跨页面存在相互冲突的断言
- **过时综述**：有更新源笔记摄入后，相关词条未同步更新
- **缺失实体页**：在 3 个及以上页面中被提及但没有独立词条的实体
- **稀疏页**：出站 `[[双链]]` 少于 2 条的页面
- **知识盲区**：Wiki 无法回答的常见问题类型，建议补充原始笔记
- **加注缺失**：词条正文中来自 `Sources/` 的内容未加 `（据文献）`，或来自 `Thoughts/` 的内容未加 `（个人分析）`

图谱感知检查（需先运行 `build graph`）：
- **枢纽存根（Hub Stubs）**：度数 > μ+2σ 但内容少于 500 字的节点
- **脆桥（Fragile Bridges）**：两个社区之间仅由 1 条边连接的情况
- **孤立社区**：与其他社区零外部连接的知识孤岛

输出审计报告，询问用户是否保存至 `Wiki/lint-report.md`。保存后 Git 提交。

### Health vs Lint 边界

| 维度 | `health` | `lint` |
|------|----------|--------|
| 范围 | 结构完整性 | 内容质量 |
| LLM 调用 | 零 | 是 |
| 成本 | 免费 | 消耗 token |
| 频率 | 每次会话，优先运行 | 每 10–15 次摄入 |
| 检查项 | 空文件、索引同步、日志同步、断链、Raw 目录合规 | 孤儿、矛盾、知识盲区、缺失实体、加注缺失 |

---

## 九、知识图谱工作流（Graph Workflow）

**触发**：`build graph`

运行：`python Tools/build_graph.py [--open] [--report] [--save]`

若 Python 环境不可用，手动构建：
1. 扫描所有 Wiki 页面，提取全部 `[[双链]]`
2. 构建节点（每页一个）与边（每条链接一条）
3. 推断未被 `[[双链]]` 显式捕获的隐性关联，标注 `INFERRED` 及置信度，写入 `Graph/graph.json`；不写入页面正文，不触发晋升流程
4. 写入 `Graph/graph.json`：`{nodes, edges, inferred_edges, built: date}`
5. 写入 `Graph/graph.html`：基于 vis.js 的自包含可视化页面

Git 提交：
```bash
git add Graph/
git commit -m "graph: rebuild graph data"
```

**图谱健康报告指标**：
- **健康摘要**：边/节点比、孤儿占比、社区数量、链接密度
- **上帝节点（God Nodes）**：度数 > μ+2σ 的枢纽页面（过于宽泛，建议拆分）
- **枢纽存根（Hub Stubs）**：被大量链接但自身内容少于 500 字的空壳
- **脆桥（Fragile Bridges）**：两个大社区间仅 1 条边连接的脆弱地带
- **幽灵枢纽（Phantom Hubs）**：被 2 个及以上页面引用但本身不存在的页面

**硬性规则**：图谱层禁止从断链自动创建页面，只报告；隐性关联（`INFERRED`）仅存入 `graph.json`，不自动写入页面正文，由研究者决定是否手动添加双链。

---

## 十、命名规范与索引格式

**命名规范**：

| 类型 | 规范 | 示例 |
|------|------|------|
| 概念词条 | 中文概念名 或 `TitleCase.md` | `纯粹理性批判.md` |
| 实体词条 | `TitleCase.md` | `ImmanuelKant.md` |
| 长文摘要 | `kebab-case.md` | `thinking-fast-and-slow.md` |
| 消歧词条 | `概念（流派）.md` | `空（佛教）.md` |
| 综述页 | `kebab-case.md` | `karma-across-traditions.md` |

**【kebab-case 中文文件名规则】**：`Wiki/sources/` 和 `Wiki/syntheses/` 的文件名须为简短英文语义词组（2–4个词，kebab-case），严禁使用汉语拼音，严禁保留中文字符。中文源文件须先翻译为英文语义词组再生成文件名。示例：《人性论》→ `treatise-human-nature.md`；《非备兑期权平仓规则》→ `naked-option-exit-rules.md`。

**`index.md` 格式**：

```markdown
# Wiki Index

## Overview
- [Overview](overview.md) — 跨领域活体综述

## Concepts
- [概念名](concepts/概念名.md) — 一行简述

## Entities
- [实体名](entities/EntityName.md) — 一行简述

## Sources
- [书名](sources/slug.md) — 作者，一行简述

## Syntheses
- [分析标题](syntheses/slug.md) — 回答的问题

## Disambiguations
- [消歧词](disambiguations/词条.md) — 涉及的流派列表
```

**`log.md` 格式**：

- **正常记录**：`## [YYYY-MM-DD] <操作> | <标题>`
- **失败记录**：`## [YYYY-MM-DD] ERROR | <操作> | <原因>`

操作类型：`bootstrap` / `ingest` / `query` / `query-synthesis` / `health` / `lint` / `graph` / `chore` / `ERROR`

> **失败可追溯原则**：ERROR 记录与正常记录**同构**，仅在操作类型字段用 `ERROR` 标记。Agent 遇到不可恢复失败（文件转换错误、文件编码损坏、API 调用超时、冲突挂起超时、工具脚本异常退出等）时，必须：
> 1. 立即写入 ERROR 记录到 `Wiki/log.md`
> 2. 继续执行后续独立步骤，不要因单点失败阻塞整个工作流
> 3. 在工作流结尾输出"⚠️ 本次执行产生了 N 条 ERROR 记录，见 log.md"汇总

---

## 十一、临时文件处理规范

**硬性原则**：所有临时生成、与知识库无直接关系的辅助文件，直接删除，绝不进入 Git 跟踪。

| 类型 | 典型示例 | 默认行为 |
|------|---------|---------|
| Lint 上下文 dump | `Wiki/_semantic_lint_context.md` | 删除 |
| 图谱缓存 | `Graph/.cache.json` | `.gitignore` 屏蔽 |
| 工具中间输出 | `Tools/__pycache__/`、`*.pyc` | `.gitignore` 屏蔽 |
| 检索索引目录 | `.qmd/` | `.gitignore` 屏蔽 |
| Obsidian 配置 | `.obsidian/`、`workspace.json` | `.gitignore` 屏蔽 |

**执行纪律**：Agent 在执行 `git add` 前，必须先清理工作目录中的临时文件。

---

## 十二、裸指令默认行为

**【裸摄入默认扫描 `Raw/`】**：当用户发出 `ingest` 指令但未指定具体文件时，默认处理 `Raw/Sources/`、`Raw/Thoughts/`、`Raw/Records/` 下所有尚未被摄入的文件（`Raw/Assets/` 跳过）。判断依据：扫描 `Wiki/log.md`，凡日志中已有对应双链记录的文件视为已处理，其余均列入待摄入队列。Agent 应先给出待摄入清单（标注每个文件所在子目录及对应加注类型），然后直接批量触发摄入工作流（无需逐一确认，除非触发冲突或消歧）。

---

> **Changelog**：
> - **2026-06-07 v3.1** — 五处工程细节修订：①§十命名规范补充 kebab-case 中文强制英文语义词组规则（覆盖 sources/ 和 syntheses/）；②§3.1 Concept Schema 加入可选 `event_date` 字段（业务/历史时间锚点，与 `last_updated` 操作时间严格区分）；③§3.2 Entity 定义前新增 Concept/Entity 边界判断规则（可复现/可泛化→Concept；唯一时空坐标→Entity）；④§3.5 Synthesis Schema 加入可选 `status`、`open_questions`、`event_date` 字段；⑤§3.1 `related` 字段加入语义边类型注释占位（supports/contradicts/extends/depends_on），为未来图谱扩展预留接口，不引入运维负担。
> - **2026-06-07 v3.0** — Raw 层由自由子目录改为固定三类（Sources / Thoughts / Records / Assets），目录决定加注类型（据文献 / 个人分析 / 个人经验），替代原"领域自适应摄入"的主观猜测机制；删除 Draft→Stable 晋升门控，隐性关联仅存 graph.json 不写页面；摄入前新词条确认改为默认自动+结尾汇总；任务追踪机制改为 Agent 环境自适应；查询生长层次三触发条件改为纯客观；Sources 摘要与 Entities 著作词条归属关系明确化；Lint 新增加注缺失检查项；Health 新增 Raw 目录合规检查；去除设计哲学与 §二 的内容重复，合并为单一权威来源（§二）。
> - **2026-06-07 v2.1** — 新增 ERROR 失败记录格式，强化可观测性设计。
> - **2026-06-07 v2.0** — 整合 v1.1 + v4.1，修复摄入挂起机制、补全会话启动规程、恢复工具骨架规范、新增 sources/ 层；Raw/ 完全只读，通过 log.md 追踪已摄入状态。

---

## 3. 使用方法

```bash
# 1. 复制本文件到目标目录
cp BOOTSTRAP_v3.1.md /path/to/new-vault/

# 2. 切换到目标目录
cd /path/to/new-vault

# 3. 在 AI 助手（Cursor / Claude Code 等）会话中说：
#    "请阅读 BOOTSTRAP_v3.1.md 并严格执行其中的 bootstrap 工作流"
```

## 4. 设计哲学（Why v3.1）

这套系统的本质是**隔离与编译**，加上**最小摩擦**。

- **Raw 层三类固定目录**是整个反幻觉体系的锚点：`Sources/`（他人）/ `Thoughts/`（自己分析）/ `Records/`（个人经验）。Agent 无需猜测文件归属，路径即规则。加注类型由目录决定，不依赖 Agent 对正文的主观判断。
- **Wiki 层**是 Agent 维护的知识织网：结构化词条、双链、综述。每次变更必提交。
- **反幻觉的五个机制**（均集中于 §二，不重复散布）：
  1. 目录决定加注类型 → 消除 Agent 对归属的主观猜测
  2. 冲突处理协议（§五 5.2）→ 矛盾不掩盖，挂起等待人工裁决
  3. 禁止自我引用（§二）→ 防止 AI 把自己的总结当事实循环论证
  4. 查询合成加注（§六）→ 跨词条推论永远可追溯
  5. Lint 加注缺失检查（§八）→ 定期审计加注执行情况
- **失败可追溯**（§十 ERROR 记录格式）：失败写入日志，不阻塞后续步骤，工作流结尾汇总。
- **默认自动执行，例外才挂起**：摄入工作流只在冲突或消歧时暂停，新词条自动写入后结尾汇总。知识库只有在维护成本足够低时才能长期运转。
- **会话启动规程**：每次新会话先同步状态（health + log + index），让 Agent 无需研究者重新交代背景即可接续工作。

**版本**：v3.1
