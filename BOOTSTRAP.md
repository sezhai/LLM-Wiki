# LLM Wiki 仓库创建提示词

> **本文件用途**：将本文件复制到任意空白目录，交给一个具备文件系统与 Shell 工具的 AI Agent（如 Claude Code、Cursor、OpenCode 等）。
> Agent 阅读本文件后，将在该目录中**完整创建**一个符合 LLM Wiki 规范的知识操作系统骨架，工具脚本按需生成，不在 bootstrap 阶段预生成。
> **当前版本**：v1.0
> **核心理念**：Raw 层（研究者完全掌管的只读事实池）/ Wiki 层（Agent 完全拥有的结构化知识编译层）/ Graph 层（结构健康层，工具生成，**可选扩展**）。
> 目录决定加注类型、引文保真、诠释强制加注、Agent 不做主观裁判、增量合并、冲突升级人工裁决、默认自动执行例外才挂起。

---

## 0. 你（Agent）的任务总览

你即将在**当前工作目录**（即本文件所在目录，以下简称 `.`）中产出一个**可直接使用的 LLM Wiki 仓库骨架**。执行前无需设置任何变量，所有命令直接在当前目录运行（`.`）。完成时，目录结构必须严格如下：

```text
./
├── AGENTS.md                  # 最高操作契约（按本文档 §2 写入）
├── README.md                  # 仓库使用说明（研究者视角）
├── .gitignore                 # 排除索引、缓存与编辑器配置
├── .llm-wiki/                 # 机器可读配置（纳入 git 跟踪）
│   └── raw-mapping.json       # Raw 子目录→加注类型映射（bootstrap 时自动生成）
├── Raw/                       # 只读事实池（Agent 严禁除读取之外的任何操作）
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
│   ├── sources/               # 长文 / 原著的 AI 摘要映射（自动生成）
│   ├── syntheses/             # 综述归档（查询答案沉淀，自动生成）
│   └── disambiguations/       # 消歧义专页
├── Graph/                     # 【可选扩展】结构健康层（工具生成，勿手动修改）
│   └── README.md
└── Tools/                     # 工具脚本（按需生成，纳入 git 跟踪）
    ├── __init__.py            # 空文件，使 Tools/ 成为 Python 包（bootstrap 时创建）
    └── README.md
```

> **Python 版本要求**：Python 3.9+（所有工具脚本均基于此版本开发；`match` 语句等 3.10+ 特性不使用，确保广泛兼容）。

> **脚本生成原则**：Tools/ 脚本**不在 bootstrap 阶段预生成**。`common.py` 在首次触发任何工具工作流时生成（作为共享依赖先行），其余脚本在首次触发对应工作流时按需生成。生成后立即运行验证，修复通过后才 git 提交。

---

## 1. 执行工作流（严格按序）

### 1.0 创建步骤追踪清单

**首先**通过 Agent 可用的任务追踪机制（`todowrite` / `TodoWrite` / 内联 Markdown 清单，视 Agent 环境自动选择）创建追踪清单，步骤 0 本身立即标记完成，其余初始为待处理。每完成一步立即更新状态，最终输出前确认清单全部完成：

- [x] 0. 创建步骤追踪清单
- [ ] 1. 向用户询问关键配置
- [ ] 2. 验证并清理目标目录
- [ ] 3. 创建物理目录结构
- [ ] 4. 写入 `AGENTS.md`（含步骤 4 末尾立即写入 `.llm-wiki/raw-mapping.json`）
- [ ] 5. 写入 `README.md`
- [ ] 6. 写入 `.gitignore`
- [ ] 6b. 写入 `Tools/requirements.txt` 和 `.env.example`
- [ ] 7. 写入各层 `README.md`
- [ ] 8. 写入 `Wiki/` 初始核心文件
- [ ] 9. 初始化 Git 仓库（含用户配置兜底）
- [ ] 10. 追加 bootstrap 记录到 `log.md`
- [ ] 10b. 清理临时文件（如有）
- [ ] 11. 首次 Git 提交（含完整 `git add`）
- [ ] 12. 最终验证与报告

### 1.1 向用户询问关键配置

**在写入任何文件之前**，通过一次对话确认以下三项。若用户拒绝回答或说"用默认"，使用括号内的默认值：

1. **Raw 层目录**：使用默认四类目录（`Sources / Thoughts / Records / Assets`），还是自定义？（默认：使用四类默认目录。若自定义，请用户列出目录名及各自的加注类型，后续所有涉及 Raw 子目录的规则均以用户提供的映射为准）
2. **Git 远程**：是否配置 `origin`？若是，提供 URL。（默认：暂不配置）
3. **摄入风格偏好**：
   - **A（批量自动）**：说 `ingest` 时自动处理所有未摄入文件，结尾汇总新建词条供复盘（默认）
   - **B（单次参与）**：每次只处理一个文件，摄入后与研究者讨论关键要点，确认重点后再继续下一个

   用户的偏好写入 AGENTS.md §四 摄入工作流的首部注释，作为后续每次触发 `ingest` 的默认行为。

### 1.2 验证目标目录

目标目录为**当前工作目录**（`.`）——即本 bootstrap 文件所在的目录，Agent 无需额外确认路径，所有后续步骤直接在 `.` 下操作。

```bash
ls -la .
```

- 目录为空（仅含本 bootstrap 文件）→ 直接继续
- 目录非空（含其他文件）→ 警告用户，要求显式确认是否在此目录继续

### 1.3 创建物理目录结构

用 `mkdir -p` 一次性创建 §0 列出的所有目录。注意：

- `Wiki/` 下各子目录**绝对禁止**再建子文件夹
- `Raw/` 下**仅**预建用户在 §1.1 确认的子目录（默认为 `Sources/`、`Thoughts/`、`Records/`、`Assets/` 四个）
- `.llm-wiki/` 目录在此步骤创建；`raw-mapping.json` 在 §1.4 写入 AGENTS.md 后立即生成（见 §1.4 末尾说明）
- `Graph/` 初始仅预建根目录；`graph.json` / `graph.html` / `graph-report.md` 由脚本运行时自动生成，**无需预建，也不存在 `Graph/reports/` 子目录**
- `Tools/` 初始预建根目录，并**立即创建空文件 `Tools/__init__.py`**（使 Tools/ 成为 Python 包，确保 `python -c "import Tools.common"` 等验证命令正常工作）

### 1.4 写入 `AGENTS.md`

使用本文档 §2 的完整模板，按以下规则替换所有占位符：

| 占位符 | 替换为 |
|--------|--------|
| `<YYYY-MM-DD>` | 今日日期（ISO 8601） |
| `<raw-dir-table>` | 用户在 §1.1 确认的 Raw 子目录映射表（**含完整 Markdown 表格**，默认如下）；替换时将占位符行与其下方的 HTML 注释行（`<!-- bootstrap 时由...`）**一并删除**，仅保留实际表格内容 |
| `<ingest-style>` | 用户在 §1.1 确认的摄入风格偏好（A 或 B，附简短说明）；替换后同时删除该行所在的 HTML 注释行（`<!-- 当前摄入风格：...`），仅保留实际风格文字 |

**`<raw-dir-table>` 默认替换内容**（用户未自定义时使用）：

```markdown
| Raw 子目录 | 存放内容 | Wiki 摄入加注 | 摘要策略 |
|------------|----------|---------------|----------|
| `Sources/` | 他人文档：论文、剪藏、技术规范、书籍 | `（据文献）` | 引文保真；他人观点与推论一律加注 |
| `Thoughts/` | 自己写的研究笔记、思辨、逻辑推演 | `（个人思考）` | 提炼核心论点；个人判断加注 |
| `Records/` | 个人记录：交易日志、聊天记录、复盘日记 | `（个人经验）` | 提炼决策逻辑与经验结论；主观内容加注 |
| `Assets/` | 图片、PDF 附件 | — | 不独立摄入；摄入父文件时按需读取被引用的图片以补充上下文 |
```

**写入 `.llm-wiki/raw-mapping.json`**（AGENTS.md 写入完成后立即执行）：

将用户确认的 Raw 子目录映射写入机器可读配置文件，供 `common.load_allowed_raw_dirs()` 稳定读取，避免运行时解析 AGENTS.md Markdown 表格。默认内容：

```json
{
  "version": 1,
  "dirs": [
    {"name": "Sources",  "annotation": "据文献",   "ingest": true},
    {"name": "Thoughts", "annotation": "个人思考", "ingest": true},
    {"name": "Records",  "annotation": "个人经验", "ingest": true},
    {"name": "Assets",   "annotation": null,        "ingest": false}
  ]
}
```

用户自定义目录时，按相同结构生成对应条目。`ingest: false` 的目录（如 `Assets/`）在"Raw 目录合规"检查中视为合法目录，不触发警告。

### 1.5 写入 `README.md`

内容要点（用第二人称，5 分钟内可读懂）：

- 一句话定位：这是个人 LLM 知识库，`Raw/` 放原始材料，`Wiki/` 是结构化沉淀
- **Raw 层目录说明**（按用户在 §1.1 确认的目录列出，默认为四类）：
  - `Sources/`：放他人文档（论文、剪藏、书籍）→ Agent 摄入时加注 `（据文献）`
  - `Thoughts/`：放自己写的研究笔记与思辨 → Agent 摄入时加注 `（个人思考）`
  - `Records/`：放个人记录（交易日志、聊天记录、日记）→ Agent 摄入时加注 `（个人经验）`
  - `Assets/`：图片与 PDF 附件（仅作为其他文件的附件被引用，不独立摄入）
- **Wiki 层用户可见分类**（sources / syntheses 标注为自动生成，研究者无需手动管理）：
  - `concepts/`：概念词条（可以查询和浏览）
  - `entities/`：人物、机构、著作、事件
  - `sources/`（自动生成）：长文摘要，由摄入工作流自动维护
  - `syntheses/`（自动生成）：查询答案沉淀，由查询工作流自动归档
- **三步上手**：
  1. 把文件放进 `Raw/` 对应子目录
  2. 在 AI 会话中说 `ingest` 触发摄入
  3. 说 `query: <问题>` 触发查询
- **Obsidian 设置提示**（高亮显示）：`Settings → Files and links` 中将 Attachment 路径设为 `Raw/Assets`，将 **New link format** 设置为 **Absolute path in vault**（绝对路径模式），确保 Obsidian 生成的链接与本仓库 `[[Wiki/concepts/xxx.md]]` 格式一致
- 工具脚本说明：`Tools/` 下脚本按需生成，说 `health` / `ingest` / `lint` / `build graph` 等触发词时自动生成对应脚本后执行
- 关键约定：`Raw/` 完全只读，Agent 只读取，不做任何修改或移动
- **Graph 层说明**（标注为可选）：说 `build graph` 可生成知识图谱，是可选的进阶功能，前 50 次摄入无需使用
- **首次生成脚本**（新会话标准话术，按序发送）：

  > 以下话术在 bootstrap 完成后、首次使用各工作流前发送给 Agent。每条话术触发一个脚本的生成与验证，顺序不可颠倒（common.py 必须最先生成）。

  **Step 1 — common.py（任何其他脚本之前必须先生成）**
  ```
  请阅读 AGENTS.md §脚本生成原则 和 §七【common.py 最低规格】，生成 Tools/common.py。
  生成后运行 python -c "import Tools.common; print('common.py OK')" 验证，
  无报错即为通过，报错则本次会话内修复，通过后 git commit。
  ```

  **Step 2 — health.py（每次新会话必跑，建议优先生成）**
  ```
  请阅读 AGENTS.md §七【health.py 最低规格】，生成 Tools/health.py。
  从 common.py 导入共享工具，禁止重复实现。
  生成后运行 python Tools/health.py 验证，通过后 git commit。
  ```

  **Step 3 — ingest.py（首次说 `ingest` 前生成）**
  ```
  请阅读 AGENTS.md §四【ingest.py 最低规格】，生成 Tools/ingest.py。
  从 common.py 导入共享工具，禁止重复实现。
  生成后运行 python Tools/ingest.py --validate-only 验证，通过后 git commit。
  ```

  **Step 4 — lint.py（首次说 `lint` 前生成）**
  ```
  请阅读 AGENTS.md §八【lint.py 最低规格】，生成 Tools/lint.py。
  从 common.py 导入共享工具，禁止重复实现。不实现断链检查（归属 health.py）。
  生成后运行 python Tools/lint.py --help 验证，通过后 git commit。
  ```

  **Step 5 — query.py（首次说 `query:` 前生成）**
  ```
  请阅读 AGENTS.md §六【query.py 最低规格】，生成 Tools/query.py。
  从 common.py 导入共享工具，禁止重复实现。
  生成后运行 python Tools/query.py --help 验证，通过后 git commit。
  ```

  **Step 6 — build_graph.py（可选，50+ 词条后再生成）**
  ```
  请阅读 AGENTS.md §九【build_graph.py 最低规格】，生成 Tools/build_graph.py。
  从 common.py 导入共享工具，禁止重复实现。
  生成后运行 python Tools/build_graph.py --help 验证，通过后 git commit。
  ```

  > **脚本报错时**：在同一会话内直接粘贴错误信息让 Agent 修复，不要新开会话。

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

# Python 虚拟环境
venv/
.venv/
env/

# 环境变量（含 API Key 等敏感配置，不入库）
.env

# Obsidian 工作区配置
.obsidian/
workspace.json

# 图谱与工具缓存
Graph/.cache.json

# 临时诊断与摄入状态文件
Wiki/_semantic_lint_context.md
*.tmp
.ingest-state.json   # 风格 B 摄入暂停时的状态存档，脚本运行完毕后自动删除

# 工具运行时生成的报告（需用户显式确认保存后才写入，此处仍屏蔽以防误提交）
Wiki/health-report.md
Wiki/lint-report.md

# OS 文件
.DS_Store
Thumbs.db

# 注意：.llm-wiki/ 目录（含 raw-mapping.json）需纳入 git 跟踪，此处不屏蔽
# 注意：Tools/__init__.py 需纳入 git 跟踪，此处不屏蔽
```

### 1.6b 写入 `Tools/requirements.txt` 和 `.env.example`

**`Tools/requirements.txt`**（最小依赖集，按需扩充）：

```
markitdown>=0.1.0
```

**`.env.example`**（环境变量模板，复制为 `.env` 后填入实际值）：

```dotenv
# LLM 后端选择（可选，默认依次尝试 opencode / claude CLI）
# LLM_BACKEND=claude

# 语义图谱推断模型（可选，设置后 build graph 启用 Pass 2 语义推断边）
# LLM_MODEL_FAST=claude-haiku-4-5-20251001

# qmd 搜索引擎路径（可选，若未在 PATH 中则指定完整路径）
# QMD_BIN=/usr/local/bin/qmd

# 本地或兼容 OpenAI 格式的模型服务端点（可选，用于接入 Ollama / vLLM 等本地推断服务）
# OPENAI_API_BASE=http://localhost:8000/v1
# OPENAI_API_KEY=sk-local
# CUSTOM_LLM_MODEL=llama3-70b
```

> 研究者首次部署时：`cp .env.example .env`，按需填入实际值。`.env` 已由 `.gitignore` 屏蔽，不会入库。

### 1.7 写入各层 `README.md`

**`Raw/README.md`**（面向研究者，不含 Agent 摄入规则）：

```markdown
# Raw 层说明

本目录是原始事实池，由你（研究者）完全掌管。Agent 对此目录只读，不做任何修改或移动。

## 子目录说明

| 目录 | 存放内容 |
|------|----------|
| `Sources/` | 他人文档：论文、网页剪藏、技术规范、书籍 |
| `Thoughts/` | 自己写的研究笔记、思辨、逻辑推演 |
| `Records/` | 个人记录：交易日志、聊天记录、复盘日记 |
| `Assets/` | 图片与附件（建议在 Obsidian 中将 Attachment 路径绑定到此目录） |

## 使用说明

- 把文件放入对应子目录后，在 AI 会话中说 `ingest` 即可触发摄入
- 哪些文件已被摄入，通过 `Wiki/log.md` 追踪，无需自行标记
- 你可以随时新增文件；若需重命名或移动已摄入文件，请告知 Agent 以更新日志哈希
- 若需从 Raw/ 中**删除**已摄入的文件，请告知 Agent 执行 `chore: delete` 协议，以清理日志中的悬空记录
- **Agent 严禁修改或移动 Raw/ 内任何文件**
```

**`Graph/README.md`**：

```markdown
# Graph 层说明

【可选扩展】存放 `build graph` 工作流自动生成的知识图谱数据，请勿手动修改。
前 50 次摄入无需使用此功能；知识库积累到一定规模后再考虑启用。

- `graph.json`：节点与边的结构化数据（含语义边类型）
- `graph.html`：基于 vis.js 的可交互可视化页面
- `graph-report.md`：图谱健康报告（运行 `build graph` 并选择保存后生成）

所有文件均由 Tools/build_graph.py 生成，直接放在本目录下，无子目录。
```

**`Tools/README.md`**：

````markdown
# Tools 层说明

所有工具脚本按需生成：说触发词时，若脚本不存在则先生成再执行。
common.py 是所有脚本的共享依赖，在首次触发任何工具工作流时优先生成。
`__init__.py` 由 bootstrap 阶段自动创建，使 Tools/ 成为 Python 包。

## Python 依赖

运行工具脚本前，建议先安装依赖：

```bash
pip install -r Tools/requirements.txt
```

`requirements.txt` 在 bootstrap 时自动生成，包含核心依赖（markitdown 等）。
`qmd` 是独立 CLI 工具，安装方式见 [github.com/tobi/qmd](https://github.com/tobi/qmd)（可选，不安装时自动降级）。

**Python 版本要求**：Python 3.9+。

## Agent 触发类（对话中说触发词即可）

| 脚本 | 触发词 | LLM 调用 | 频率 |
|------|--------|----------|------|
| `common.py` | 自动（任何工具工作流首次触发时） | 零 | 一次性生成 |
| `health.py` | `health` | 零 | 每次会话必跑 |
| `ingest.py` | `ingest` / `ingest <file>` / `ingest <N>` / `ingest all` | 是（摄入阶段） | 按需，有新文件时运行 |
| `lint.py` | `lint` | 是（消耗 token） | 每 10–15 次摄入后 |
| `query.py` | `query: <问题>` | 是（查询阶段） | 按需 |
| `build_graph.py` | `build graph` | 条件性 | 按需（可选扩展） |

> `build_graph.py` Pass 1（提取显式双链）零 LLM 调用；设置 `LLM_MODEL_FAST` 环境变量可选启用 Pass 2 语义推断边（消耗 token）。

其他脚本（如 PDF 转换等）可在需要时告知 Agent 按需生成。
````

### 1.8 写入 Wiki 初始核心文件

**`Wiki/index.md`**：

```markdown
# Wiki Index

## Overview
- [Overview](overview.md) — 跨领域活体综述

## Concepts


## Entities


## Sources


## Syntheses


## Disambiguations

```

**`Wiki/overview.md`**：

```markdown
# 跨领域活体综述

> 本文件由 Agent 维护。更新触发条件：本次摄入新增或修改了 **2 个及以上不同领域**的词条，或现有综述中某条判断被新料直接否定。单领域摄入不更新本文件。
> **"不同领域"判断规则**：比较本次摘入词条的 frontmatter `domain` 字段值（如 `经济学`、`哲学`、`技术`）；两个词条的 `domain` 字段字符串不相同即视为"不同领域"。`domain` 为空时，视为独立领域（`__unset`）参与比较。

```

**`Wiki/log.md`**（bootstrap 记录在 §1.10 写入）：

```markdown
# Wiki 操作日志

<!-- 格式：## [YYYY-MM-DD] <操作类型> | <标题> [| 附加字段...] -->
<!-- 操作类型：bootstrap / ingest / query / query-synthesis / health / lint / graph / chore / ERROR -->
<!-- ingest 完整格式：## [YYYY-MM-DD] ingest | <标题> | [[Raw/<子目录>/<路径>/<文件名>]] | sha256:<前32位十六进制> | slug:<slug> -->
<!-- query-synthesis 完整格式：## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<slug> -->
```

### 1.9 初始化 Git 仓库

```bash
git init
git branch -M main
```

**Git 用户配置兜底**：检查全局 Git 用户是否已配置，若未配置则为本仓库设置局部默认值：

```bash
git config user.name 2>/dev/null | grep -q . || git config --local user.name "LLM Wiki Agent"
git config user.email 2>/dev/null | grep -q . || git config --local user.email "llm-wiki@local"
```

（仅执行 `git init`、`git branch -M main` 和配置兜底，`git add` 在 §1.11 一次性完成）

### 1.10 追加 bootstrap 记录到 `log.md`

`Wiki/log.md` 末尾追加（将 `<YYYY-MM-DD>` 替换为当天日期；日期使用 Agent 运行环境的系统本地日期 `date +%Y-%m-%d`，与后续摄入记录时区保持一致）：

```
## [<YYYY-MM-DD>] bootstrap | LLM Wiki OS v1.0 骨架建立
```

### 1.10b 清理临时文件（如有）

在执行 `git add` 之前，按 §十一 的执行纪律检查并清理工作目录中的临时文件（`__pycache__/`、`*.pyc`、`*.tmp` 等）。Bootstrap 阶段通常不产生临时文件，本步骤作为防御性检查确保 `git add` 前工作目录干净。

### 1.11 首次 Git 提交

```bash
git add AGENTS.md README.md .gitignore .env.example .llm-wiki/ Raw/ Wiki/ Graph/ Tools/
git commit -m "chore: bootstrap LLM Wiki OS v1.0"
```

若用户在 §1.1 提供了远程仓库 URL：

```bash
git remote add origin <URL>
git push -u origin main
```

### 1.12 最终验证与报告

打印：
- 完整目录树（`find . -type f | sort`）
- `git log --oneline`
- 下一步操作提示：
  > 1. 把他人文档放进 `Raw/Sources/`，自己的笔记放进 `Raw/Thoughts/`，个人记录放进 `Raw/Records/`
  > 2. 在 AI 会话中说 `ingest` 触发摄入（首次会先自动生成所需工具脚本）
  > 3. 说 `query: <问题>` 触发查询
  > 4. 说 `health` 检查仓库健康状态

---

## 2. AGENTS.md 模板（Agent 请将以下内容完整写入目标库）

---

# AGENTS.md（最高操作契约）

<!-- version: v1.0 | created: <YYYY-MM-DD> | last_schema_updated: <YYYY-MM-DD> -->

本文件是 Agent 每次执行前**必读**的最高宪法。所有工作流、规则、模板均以本文件为唯一权威来源。

---

## AGENTS.md 修订记录

| 版本 | 日期 | 修订内容 | 修订原因 |
|------|------|----------|----------|
| v1.0 | `<YYYY-MM-DD>` | 初始版本（含 rename 追踪链、health 日志覆盖兼容逻辑、哈希检查限定 ingest 类型、Raw 合规检查豁免规则、slug 冲突检查、临时文件清理步骤、冲突信号结构性重构判断、PYTHON_BIN 跨平台探测、原子写入、chore:delete 协议、超大文件卡点、QMD_AVAILABLE 模块级缓存） | bootstrap |

> **何时修订 AGENTS.md**：当研究者与 Agent 在协作过程中发现某条规则反复产生不符合预期的结果，或某个工作流与实际使用习惯持续偏差时，应讨论是否修订本文件。修订后更新上表，并在 log.md 中追加 `chore | AGENTS.md 修订 vX.X`。

---

## 会话启动规程（每次新会话必须首先执行）

```
1. 运行 health 检查（说 health，见§七）
   ├── 若 Tools/common.py 不存在：先生成它（见§七【common.py 最低规格】），验证通过后继续
   └── 若 Tools/health.py 不存在：先生成它（见§七【health.py 最低规格】），验证通过后执行
2. 读取 Wiki/log.md 最近 10 条记录，了解上次会话的操作上下文
3. 读取 Wiki/index.md，获取当前知识库词条全貌
4. 报告：健康状态摘要 + 上次会话摘要 + 当前词条数
5. 等待研究者指令
```

> **为什么**：Agent 没有跨会话记忆，上述步骤是建立上下文的最低成本方式，避免每次都要研究者重新交代背景。

---

## 脚本生成原则

**Tools/ 脚本按需生成，不在 bootstrap 阶段预生成。**

生成顺序约束：
1. `common.py` 必须最先生成，在首次触发任何工具工作流时优先生成（其他所有脚本从此导入，禁止各自实现重复逻辑）
2. 其他脚本在首次触发对应工作流时生成
3. 生成任何脚本前，先检查 `common.py` 是否存在；不存在则先生成它

生成后立即验证（将 `<script_name>` 替换为实际脚本文件名，例如 `health.py`）：
```bash
python Tools/<script_name>.py --help
```
**例外**：`common.py` 是纯函数库，不含 CLI 入口，验证方式为：
```bash
python -c "import Tools.common; print('common.py OK')"
```
若报错，在同一会话内修复，修复通过后才纳入 git 提交。

> **`Tools/__init__.py` 说明**：bootstrap 阶段已创建此空文件，确保上述验证命令可正常执行。若因故缺失，重新创建空文件即可：`touch Tools/__init__.py`。

---

## 快速触发指令

| 指令 | 触发工作流 | 说明 |
|------|-----------|------|
| `ingest` | 摄入工作流 | 扫描 `Raw/`，处理所有未摄入文件 |
| `ingest <file>` | 摄入特定文件 | 处理指定文件并归档 |
| `query: <问题>` | 查询工作流 | 先查 Wiki，盲区回退至 Raw，新洞见自动织网 |
| `health` | 健康检查 | 结构完整性检查（零消耗，每次会话必跑） |
| `lint` | 质量审计 | 孤儿页、矛盾、盲区检查（每 10–15 次摄入跑一次） |
| `build graph` | 图谱分析 | 【可选扩展】生成上帝节点、脆桥报告 |
| `chore: move <旧路径> → <新路径>` | Raw 文件迁移归档 | 更新 log.md 中对应记录的路径字段，不重新摄入内容 |
| `chore: rename Wiki/<旧路径> → Wiki/<新路径>` | Wiki 词条重命名 | 更新所有双链、index.md 及日志，不重新摄入内容 |
| `chore: delete <Raw路径>` | Raw 文件删除归档 | 在 log.md 中追加删除记录，消除 health 的悬空路径警告 |

或用自然语言描述，Agent 自行映射到对应工作流。

**执行纪律**：
- **ingest**：通过当前 Agent 环境可用的任务追踪机制创建该工作流各步骤的追踪清单，每完成一步更新一次状态
- **query / health / lint / graph**：使用内联步骤标注推进，不强制创建任务追踪条目
- **Python 解释器探测**：执行任何 `python` 命令前，按平台分支探测：
  - **Unix/macOS**：`.venv/bin/python` → `venv/bin/python` → `python3` → `python`
  - **Windows**：`.venv\Scripts\python.exe` → `venv\Scripts\python.exe` → `python`

  `common.py` 中的 `PYTHON_BIN` 常量封装了完整探测逻辑（含 `sys.platform` 判断），其余所有脚本通过 `subprocess` 调用时统一使用 `common.PYTHON_BIN`，确保虚拟环境在 Agent 子进程中始终生效。

---

## 一、路径规范

**【根目录定义】**：本契约所有路径及 Obsidian `[[双链]]` 均以 Vault 根目录（即包含 `AGENTS.md`、`Raw/`、`Wiki/`、`Graph/`、`Tools/` 的那一层）为唯一基准面。

**【双链绝对化】**：所有指向 Raw 层或 Wiki 层的链接，必须使用基于 Vault 根目录的绝对路径，严禁使用 `../` 等相对路径，确保 Obsidian Graph View 完整织网。

示例：`[[Wiki/concepts/复杂系统.md]]`、`[[Raw/Sources/某论文.md]]`

---

## 二、Raw 层目录与加注规则

Raw 层由研究者完全掌管，Agent 只读取，不做任何修改或移动。Raw 层子目录在 bootstrap 时由研究者确认，Agent 根据文件所在目录**自动确定加注类型**，无需猜测。这是防止语义漂移的核心机制。

<raw-dir-table>

<!-- bootstrap 时由 §1.4 替换为用户确认的目录映射表；默认内容见 §1.1 确认流程 -->

**【加注执行规则】**：

- `Sources/` 文件摄入时：
  - 原始笔记中明确带引号或标注"原文"的内容 → 保真复现，不加注（视为基础事实）
  - 他人文章中的推论、观点、概括 → 写入 Wiki 时强制加注 `（据文献）`
  - 示例：`某理论认为 X 是 Y 的充分条件（据文献）。`

- `Thoughts/` 文件摄入时：
  - 研究者自己的思考、判断、逻辑推演 → 写入 Wiki 时强制加注 `（个人思考）`
  - 示例：`休谟的同一性论证在数量与统一性边界处存在逻辑断层（个人思考）。`

- `Records/` 文件摄入时：
  - 所有主观内容、决策记录、经验总结 → 写入 Wiki 时强制加注 `（个人经验）`
  - 示例：`动量策略在高隐含波动率环境下失效概率显著上升（个人经验）。`

**【Assets 定位与图片读取规则】**：`Assets/` 目录不独立摄入——图片本身不产生 Wiki 词条。当摄入含图片引用的 Markdown 文件时，Agent **在该次摄入流程内**读取被引用的图片作为补充上下文：
1. 先完整读取文本内容，按正常流程生成词条草稿
2. 识别文中 `![[Raw/Assets/...]]` 或 `![](...)` 引用的图片路径
3. 逐一尝试读取相关图片，捕获视觉信息（图表数据、流程图结构、截图文字等）；图片不可读时按以下顺序降级处理：
   - **Agent 具备多模态能力但文件损坏/格式不支持**：输出警告 `⚠️ 图片不可读: <路径>（原因：格式不支持或文件损坏）`，跳过该图片
   - **Agent 本身不具备图像识别能力**：输出警告 `⚠️ 图片不可读: <路径>（原因：当前 Agent 无多模态能力）`，跳过该图片；在对应词条的相关章节记录 `（图片引用：<路径>，内容待人工补充）`
   - 两种情况均不阻塞摄入流程，继续处理其余内容
4. 将可读图片信息补充进对应词条的相关章节，标注 `（图示补充）`

**【禁止主观裁判】**：Agent 仅作为"知识整合编译器"，不得独立判断哪种研究观点或诠释"更正确"。

**【禁止自我引用】**：严禁将 Agent 自己之前在 Wiki 词条里写就的总结性言论，作为推导或佐证新事实的"客观证据"。禁止将查询合成内容作为后续推理的"客观依据"。

**【禁止推断型事实填补】**：当来源文件中某项信息缺失时，Agent **严禁**根据上下文合理性进行推断补全——例如推测未标注的日期、填补缺失的引用、推断因果链条中未明确陈述的中间步骤。缺失即缺失：标注为空白或写入 `（来源缺失，待补充）`，绝不以"看似合理"替代实际证据。这是防止知识库"看似合理但从未存在过的知识"污染的核心防线。

**【查询合成加注】**：由查询工作流跨词条合成产生的新推论，必须加注 `（据查询合成，未经来源验证）`，与直接来源于 Raw 层的事实明确区分。

---

## 三、词条元数据与排版规范

> **词条类型说明**：研究者需要关注和浏览的词条是 **concepts**（抽象概念）和 **entities**（具体对象）两类。`sources/` 和 `syntheses/` 由 Agent 自动生成和维护，研究者无需手动管理。`disambiguations/` 在遇到歧义词时按需生成。

### 命名规范（唯一权威来源）

| 词条类型 | 命名规范 | 示例 |
|----------|----------|------|
| 概念词条（`concepts/`） | 中文概念名（首选）或 `TitleCase.md`（仅当概念本身是英文专有名词或无通行中文译名时使用） | `纯粹理性批判.md`、`BullPutSpread.md` |
| 实体词条（`entities/`） | `TitleCase.md` | `ImmanuelKant.md` |
| 长文摘要（`sources/`） | `kebab-case.md`（英文语义词组，2–4词） | `thinking-fast-and-slow.md` |
| 消歧词条（`disambiguations/`） | `概念（流派）.md` | `空（佛教）.md` |
| 综述页（`syntheses/`） | `kebab-case.md`（英文语义词组，2–4词） | `karma-across-traditions.md` |

**【kebab-case 中文文件名规则】**：`Wiki/sources/` 和 `Wiki/syntheses/` 的文件名须为简短英文语义词组，严禁使用汉语拼音，严禁保留中文字符。中文源文件须先翻译为英文语义词组再生成文件名。示例：《人性论》→ `treatise-human-nature.md`；《非备兑期权平仓规则》→ `naked-option-exit-rules.md`。

**【slug 一致性原则】**：同一来源文件在不同会话中必须生成相同的 slug。生成 slug 后立即记录至 log.md 的 `slug:` 字段。若检测到 slug 冲突（相同 slug 对应不同来源文件），输出警告，等待研究者手动确认重命名，不自动覆盖。

### 3.1 标准概念词条（`Wiki/concepts/`）

```markdown
---
title: ""
type: concept
aliases: ["", "", ""]
domain: "<根据文件所在 Raw/ 子目录或内容自动判断，自由填写>"
subdomain: ""
era: "<可选：历史时代 / 年份 / 无>"
tags: []
sources: ["[[Raw///...]]"]
related: ["[[Wiki/concepts/相关概念A.md]]"]
# related 字段语义边类型注释（可选，供 build_graph.py 读取以生成加权边）：
# - "[[Wiki/concepts/概念B.md]] # supports"
# - "[[Wiki/concepts/概念C.md]] # contradicts"
# - "[[Wiki/concepts/概念D.md]] # extends"
# - "[[Wiki/concepts/概念E.md]] # depends_on"
event_date:                    # 可选：知识内容指向的业务/历史时间（格式 YYYY-MM-DD）
last_updated: YYYY-MM-DD
pending_review: false
---

## 📌 核心定义
（150 字以内，精准的本质定义，严禁前言后语）

## 🎯 核心论点与逻辑演进
（无序列表 `-` 结构化呈现。加注规则：据文献 / 个人思考 / 个人经验 / 据查询合成，未经来源验证）

## ⚖️ 边界防御与相近概念区分
* 对比 **[[Wiki/concepts/相近概念X.md]]**：指出本质区别，严禁语义串味。

## 🔗 关联实体
- [[Wiki/entities/相关人物或著作.md]]

## 📜 原始事实追溯
* 来源：[[Raw///某原始笔记文件名.md]]
```

**【Concept 与 Entity 边界定义】**：

- **归入 Concept**：抽象的策略、定理、机制、算法、方法论、思想体系。判断标准：可复现、可泛化、不绑定唯一历史实例。例：「Bull Put Spread」（期权策略）、「动量效应」（市场机制）、「涅槃」（佛教概念）、「协整」（统计方法）。
- **归入 Entity**：具有唯一历史身份的具体对象。判断标准：存在唯一时空坐标，无法被泛化复现。例：特定人物（David Hume）、现实公司/机构（Federal Reserve）、已发生的独立事件（2008年金融危机）。
- **边界判断规则**：若对某对象能问"这个概念在其他场合还适用吗？"且答案为"是"，归 Concept；若只能问"这件事发生过吗？"，归 Entity。

著作类实体若已有 `Wiki/sources/` 摘要页，实体词条的 `raw_link` 指向摘要页而非重复摘要内容，实体词条只存身份信息与关联概念。

### 3.2 实体词条（`Wiki/entities/`，命名：`TitleCase.md`）

```markdown
---
title: "<人名 / 著作名 / 机构名 / 事件名>"
type: entity
entity_type: person | organization | work | event
tags: []
sources: ["[[Raw///...]]"]
last_updated: YYYY-MM-DD
---

## 简介
（100 字以内）

## 核心关联概念
- [[Wiki/concepts/概念A.md]]

## 📜 原始事实追溯
* 来源：[[Raw///某原始笔记文件名.md]]
```

### 3.3 长文 / 原著摘要映射（`Wiki/sources/`，命名：`kebab-case.md`）

仅由 `Raw/Sources/` 的文件触发。实体词条中同名著作的 `raw_link` 指向本页，不重复摘要。

```markdown
---
title: "<书名 / 长文标题>"
type: source_map
author: ""
raw_link: "[[Raw/Sources//...]]"
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
title: ""
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
title: ""
type: synthesis
tags: []
sources: ["[[Wiki/concepts/...]]"]
status: open | closed              # open=问题仍开放，closed=已有确定结论
open_questions: []                 # 本综述尚未解决的子问题列表
event_date:                        # 可选：综述内容指向的业务/历史时间（格式 YYYY-MM-DD）
last_updated: YYYY-MM-DD
---

## 结论

## 论据与引用
- [[Wiki/concepts/概念A.md]]：……（据查询合成，未经来源验证）
```

---

## 四、摄入工作流（Ingest Workflow）

**触发**：`ingest` 或 `ingest <file>`

<!-- 当前摄入风格：<ingest-style>（见 AGENTS.md §1.1 配置） -->

**【脚本检查】**：触发摄入时，若 `Tools/common.py` 不存在，先生成它；若 `Tools/ingest.py` 不存在，先生成它（规格见本节末尾），验证通过后再执行摄入。

**【裸摄入默认行为】**：当用户发出 `ingest` 指令但未指定具体文件时，默认处理 `Raw/Sources/`、`Raw/Thoughts/`、`Raw/Records/` 下所有尚未被摄入的文件（`Raw/Assets/` 跳过）。

**【超大文件处理】**：在读取源文件（步骤 5）前，检查文件字符数：若单文件超过 **200,000 字符**（约 100,000 汉字），输出警告：
> ⚠️ 大文件警告：`<路径>`（约 X 万字符），一次性摄入可能超出上下文窗口。建议：
> - 输入 `ingest <路径> --chapter` 按章节分批摄入（Agent 将尝试识别标题结构分段）
> - 或手动将文件拆分为多个子文件后重新摄入

挂起等待研究者确认，不自动强行摄入。若研究者确认 `--all-at-once`，照常执行但追加警告至日志。

**【批量摄入上限】**：扫描完成后，若待摄入队列超过 **5 个文件**，Agent 须暂停并提示：

> ⚠️ 检测到 N 个待摄入文件，超出单次处理建议上限（5 个）。一次性处理过多文件可能导致上下文溢出，建议分批执行。
> - 输入 `ingest 5` 处理前 5 个，完成后再次说 `ingest` 处理下一批（Agent 将转换为 `python Tools/ingest.py --n 5`）
> - 输入 `ingest all` 确认本次全量处理（适合文件较短、内容集中的情况，Agent 将转换为 `python Tools/ingest.py --all`）

若用户选择 `ingest all` 或文件数量 ≤ 5，直接继续执行，不再提示。

> **风格 B 与批量上限的组合**：风格 B 模式下每个文件处理后均需讨论确认，本身已是逐个处理。因此风格 B 用户触发批量上限提示时，**建议选择 `ingest all`**——因为风格 B 的逐个暂停机制比批量上限更细粒度，不存在上下文溢出风险。提示信息对风格 B 用户可注明此建议。

**【去重判断依据】**：扫描 `Wiki/log.md`，以文件路径与 SHA-256 哈希双重匹配作为去重主键：
- 路径存在于 log.md 且当前文件哈希与 log.md 中记录的哈希一致 → 已摄入，跳过
- 路径存在于 log.md 但当前哈希不匹配 → 文件已被修改，输出警告，询问是否重新摄入。**确认重新摄入时，走增量合并流程（§五 5.1），绝不直接覆盖原有词条**；新内容与旧词条对比 Diff 后无缝缝合，若存在冲突信号则强制走冲突处理协议（§五 5.2）
- 路径不在 log.md → 未摄入，加入队列

> **为什么用哈希而非仅用路径**：文件重命名或移动后，纯路径匹配会导致同一内容被重复摄入；哈希匹配在路径变更后仍能正确识别已处理文件。

**【新摄入前残留清理】**：在扫描待摄入队列（步骤 1）开始前，检查仓库根目录是否存在 `.ingest-state.json`：
- **存在**：输出警告 `⚠️ 检测到上次未完成的摄入状态文件（.ingest-state.json）。若上次摄入因意外中断，可说 ingest --continue 恢复；否则说 ingest --discard 删除该文件并重新开始。`，挂起等待研究者确认，不自动删除（避免误删有效断点状态）。
- **不存在**：直接继续。

Agent 应先给出待摄入清单（标注每个文件所在子目录及对应加注类型），然后按摄入风格偏好执行（批量自动 / 单次参与）。

**前提原则**：凡研究者放入 `Raw/` 的文件，均视为已确认需要摄入，Agent 不做二次价值判断。

**支持格式**：`.md` 直接摄入；`.pdf`、`.docx`、`.pptx`、`.xlsx`、`.html`、`.txt`、`.epub` 等通过 [markitdown](https://github.com/microsoft/markitdown) 自动转换后摄入。转换前先检测 `markitdown` 是否可用（`which markitdown` 或 `markitdown --version`）；不可用则输出警告 `⚠️ markitdown 未安装，非 Markdown 文件将无法转换，请运行 pip install markitdown 后重试`，并跳过该文件（写入 ERROR 日志），不阻塞其余文件的摄入。`Raw/Assets/` 下的附件不摄入。

**执行步骤（严格按序）**：

> **步骤序列的双重身份**：以下步骤同时服务于两个目的：①当 `Tools/ingest.py` 已存在时，这是 **ingest.py 的实现规格**——脚本按此逻辑运行，Agent 只需运行脚本并按退出码行事（exit 0 继续、exit 1 汇报错误、exit 2 挂起等待裁决）；②当脚本**尚未生成**时，这是 Agent 的手动兜底操作路径。两种情况下步骤语义完全相同，差别仅在于执行者。

**【ingest.py 存在时的 Agent 操作】**：
1. 创建追踪清单（仅含"运行脚本 → 按退出码处理"两步）
2. 运行：`python Tools/ingest.py [file_path ...]`
3. 按退出码行事：
   - exit 0 → 执行步骤 13（qmd 更新）和步骤 14（汇总）
   - exit 1 → 读取 log.md 中的 ERROR 记录，向用户汇报，继续下一文件
   - exit 2 → 将脚本打印的 `[NEEDS_REVIEW]` 或 `[DISCUSS]` 内容转发至对话界面，等待研究者指令

创建追踪清单并实时更新（脚本不存在时执行以下手动步骤）。

**步骤 1. 去重扫描**：读取 `Wiki/log.md`，扫描全部 `ingest` 记录，建立路径→哈希映射表，判断哪些文件需要处理（未摄入 / 已修改 / 跳过）。

**步骤 2. 计算文件哈希**（对进入队列的文件逐一执行）：

使用 Python `hashlib.sha256` 计算（脚本内部实现；跨平台兼容，不依赖 `sha256sum` 命令）。取哈希前 32 位十六进制字符，用于步骤 11 的日志写入与后续去重校验。

**步骤 3. 确定加注类型**：读取文件路径，根据 §二 的目录映射表确定本文件的加注类型（`据文献` / `个人思考` / `个人经验`）。此步骤无需检索，直接由路径决定。

**步骤 4. 检索预扫描**：摄入前，定位已有相关内容。优先使用 qmd（调用 `common.QMD_AVAILABLE` 常量判断，定义见 §七【common.py 最低规格】）；否则逐级降级：

```bash
# 优先路径（qmd 可用时）
qmd query "<关键词>" --collection wiki --format json -n 8
# 从 JSON 结果中解析 file 字段获取命中页面路径

# 降级路径一：读取 Wiki/index.md，对标题和一行简述做关键词匹配

# 降级路径二（index 匹配不足时）：全文搜索
grep -r "<关键词>" Wiki/ --include="*.md" -l
```

- 命中相关 Wiki 词条 → 进入增量合并流程（见§五）
- 无命中 → 进入新建词条流程

**步骤 5. 读取源文件**：完整读取（非 Markdown 先自动转换）。读取前执行超大文件检查（见本节【超大文件处理】）。含图片的 Markdown 文件按 §二【Assets 定位与图片读取规则】步骤处理（含图片不可读的降级策略）。对 PDF / DOCX 等经 markitdown 转换的文件，若原始文件中存在内嵌图片但转换后的 Markdown 中无任何图片路径，追加警告 `⚠️ 内嵌图片已剥离: <原始文件路径>`，不阻塞摄入流程。

**步骤 6. 读取 Wiki 上下文**：读取 `Wiki/index.md` 和 `Wiki/overview.md` 获取当前全貌。

**步骤 7. 执行摄入**：默认全自动执行，仅以下情况挂起：

**情况 A — 检测到冲突信号**，挂起并呈现冲突详情：
- 新料与现有词条对同一命题给出相反断言 → 挂起
- 数值、年份、因果方向明确不一致 → 挂起
- 同一词汇在新料与已有词条中指向完全不同的对象 → 挂起
- **核心定义发生结构性重构**：新料对词条核心定义不是"增补细节"而是"重构组成要素或要素关系"——判断标准：若按新料改写后原有定义将完全无法成立（而非仅被补充或细化），强制挂起（与 §5.2 定义一致）
- 其余情况默认自动合并，不挂起

**情况 B — 技术性失败**，写入 ERROR 日志，跳过该文件继续处理队列：
- 文件损坏或编码异常，Agent 无法读取内容
- 文件转换失败（markitdown 报错），且研究者未提供备用格式

> **新建词条无需确认**：直接写入，工作流结尾输出"本次新建词条汇总"供研究者复盘。

**步骤 7.5（Slug 冲突预检，内嵌于步骤 7 执行顺序中）**：在确定拟写入词条的文件名（slug）后、执行写入之前，调用 `common.check_slug_conflict(slug, target_dir, operation_type)` 执行冲突检查。

- 无冲突 → 继续执行步骤 8
- 发现冲突 → **挂起**，输出：
  > ⚠️ Slug 冲突：拟生成文件 `<slug>.md` 已存在，对应来源为 `[[Raw/.../<已有文件>]]`。
  > 请指定新的 slug，或确认覆盖（若两篇文件属同一主题的不同版本）。

  等待研究者人工确认后，方可继续写入，不自动覆盖。

**【exit 2 两种子情况的恢复路径】**：exit 2 有两种子情况，恢复方式完全不同，Agent 必须根据打印前缀区分：

- **`[NEEDS_REVIEW]`（冲突 / Slug 冲突）**：`.ingest-state.json` 未写入（冲突发生在步骤 8 之前或步骤 7.5 阶段）。研究者裁决完毕后，Agent 以 **完整参数重新运行** `python Tools/ingest.py <file_path>`，不使用 `--continue`（因为词条尚未写入，需从头执行步骤 8）。
- **`[DISCUSS]`（风格 B 讨论暂停）**：`.ingest-state.json` 已写入（词条已在步骤 8 写入完毕）。研究者确认后，Agent 以 `--continue <file_path>` 恢复，脚本读取状态文件直接从步骤 9 继续。

> **注意**：若风格 B 模式下步骤 8 写词条时触发了内容冲突（强制走 §五 5.2 协议），脚本打印 `[NEEDS_REVIEW]`，此时词条已写入争议格式（含 `⚠️ 争议` 块，`pending_review: true`）。研究者完成裁决、Agent 更新词条后，再以 `--continue <file_path>` 执行步骤 9–12，完成后续索引更新与提交。

**【摄入风格 B 专项说明】**：当 AGENTS.md 配置的摄入风格为 B（单次参与）时，`ingest.py` 在每个文件的词条写入完成后（步骤 8 结束、步骤 9 执行前）将当前文件路径、slug、标题写入 `.ingest-state.json`（见下方 JSON 结构规格），打印 `[DISCUSS] <词条名>` 并以 exit 2 退出。Agent 捕获此信号后，将词条草稿摘要转发至对话界面，与研究者讨论关键要点；研究者确认后，Agent 以 `--continue <file_path>` 参数重新调用脚本，脚本读取 `.ingest-state.json` 恢复上下文并执行步骤 9–12，完毕后删除 `.ingest-state.json`，然后继续队列中的下一个文件。脚本**严禁**在步骤 8 之前 exit 2（草稿写入前不中断），确保研究者看到的是已成形的词条而非空文件。

**`.ingest-state.json` 结构规格**（风格 B 暂停时写入，`--continue` 时读取，执行完毕后删除）：

```json
{
  "version": 1,
  "file_path": "Raw/Sources/某文章.md",
  "slug": "some-article",
  "title": "某文章标题",
  "target_wiki_path": "Wiki/sources/some-article.md",
  "paused_at_step": 9,
  "created_at": "YYYY-MM-DDTHH:MM:SS"
}
```

字段说明：`file_path` 为 Raw 层原始文件路径；`slug` 为词条文件名（去后缀）；`target_wiki_path` 为已写入的词条路径；`paused_at_step` 固定为 `9`（恢复后从步骤 9 继续）；`created_at` 为 ISO 8601 时间戳。

> **多文件批量处理时的挂起行为**：遇到 exit 2 时，仅挂起当前文件，等待研究者裁决完成后继续队列中的下一个文件，不终止整个摄入队列。

**步骤 8. 新建或增量合并词条**：在 `Wiki/` 对应子目录下创建或更新词条，严格执行 §二 加注规则。

**步骤 9. 更新索引与综述**：
- 更新 `Wiki/index.md`，在对应分类下添加条目
- 若本次摄入触发了 overview 更新条件（见 `Wiki/overview.md` 顶部注释：新增或修改了 2 个及以上不同 `domain` 的词条，或现有综述中某条判断被新料直接否定），更新 `Wiki/overview.md`

**步骤 10. 摄入后验证**：检查新词条中所有 `[[双链]]` 是否指向已存在页面；若存在断链，输出警告并记录。

**步骤 11. 追加日志**（哈希前 32 位与路径双重记录，是判断文件已摄入的唯一依据）：

```
## [YYYY-MM-DD] ingest | <标题> | [[Raw/<子目录>/<路径>/<文件名>]] | sha256:<前32位十六进制> | slug:<生成的文件名>
```

> **`slug:` 字段填写规则**：
> - `sources/` 词条：填写 kebab-case 文件名（去除 `.md` 后缀），例如 `thinking-fast-and-slow`
> - `syntheses/` 词条：同上
> - `concepts/` 词条：填写词条文件名（去除 `.md` 后缀），例如 `纯粹理性批判` 或 `ComplexSystems`
> - `entities/` 词条：填写词条文件名（去除 `.md` 后缀），例如 `ImmanuelKant`
> - 一次摄入产生多个词条时，以首个新建词条的文件名为准，其余在同一日志行内附加说明，格式为：`slug:<主slug> (+<次级词条1>, +<次级词条2>)`，例如：`slug:thinking-fast-and-slow (+认知偏差, +DanielKahneman)`

**步骤 12. Git 提交**（严禁 `git add Raw/`，Raw/ 由研究者自行管理）：

```bash
git add Wiki/ Tools/
git commit -m "ingest: <标题>"
```

**步骤 13. 更新检索索引**（qmd 可用时执行，不可用时跳过，通过 `common.QMD_AVAILABLE` 判断）：

```bash
qmd embed --collection wiki
```

**步骤 14. 工作流结尾汇总**：输出本次摄入的新建词条列表与 ERROR 记录数量（若有）。

> 📁 **提示**：Wiki 已更新并提交。`Raw/` 的新增文件尚未纳入 Git 跟踪（由研究者自行管理）。若需将原始物料一并版本化，请手动执行：
> ```bash
> git add Raw/ && git commit -m "raw: add source materials"
> ```

---

**【ingest.py 最低规格】**（首次触发 ingest 时生成）：

- 入参：
  - `[file_path ...]`：指定文件路径，缺省则扫描全部未摄入文件
  - `[--n <N>]`：仅处理队列前 N 个文件（对应用户输入 `ingest 5` → Agent 转换为 `python Tools/ingest.py --n 5`）
  - `[--all]`：忽略批量上限，全量处理（对应用户输入 `ingest all`）
  - `[--validate-only]`：仅验证环境（检查 Python 版本 ≥ 3.9、markitdown 可用性、`.llm-wiki/raw-mapping.json` 可读性），打印验证结果后退出，不执行任何摄入操作
  - `[--continue <file_path>]`：风格 B 专用——跳过步骤 1–8，对指定文件路径直接从步骤 9 开始执行。脚本在 `[DISCUSS]` exit 2 前将当前文件路径、slug、标题写入 `.ingest-state.json`（临时状态文件，位于仓库根目录，已由 `.gitignore` 显式屏蔽）；`--continue` 时读取此文件恢复上下文，执行完毕后删除该文件
  - `[--discard]`：删除残留的 `.ingest-state.json` 并退出，不执行摄入（对应用户说 `ingest --discard`）
- **退出码语义**（三值协议，Agent 必须按退出码决定后续行为）：
  - `exit 0` = 全部成功，Agent 继续执行后续步骤
  - `exit 1` = 硬错误（文件损坏、转换失败等），ERROR 已记录至 log.md，Agent 汇报后继续下一文件
  - `exit 2` = 需人工介入，含两种子情况：
    - **冲突 / Slug 冲突**：打印 `[NEEDS_REVIEW] <原因>`，Agent 捕获后停止 Shell 操作，转发至对话等待研究者指令
    - **风格 B 讨论暂停**：打印 `[DISCUSS] <词条名>`，Agent 捕获后将词条草稿摘要转发至对话界面与研究者讨论，研究者确认后 Agent 以 `--continue <file_path>` 参数重新调用脚本，脚本读取 `.ingest-state.json` 恢复上下文执行步骤 9–12
  - **Agent 不得自行重试或修改代码**，exit 2 后一律等待研究者自然语言指令
- 核心逻辑：步骤 1 扫描 log.md 去重 → 步骤 2 计算 sha256 前 32 位 → **步骤 7.5 Slug 冲突预检**（冲突则打印 `[NEEDS_REVIEW]` 并 exit 2）→ 步骤 8 写词条（使用 `common.write_file()` 原子写入）→ **风格 B 检查**（若摄入风格为 B，将当前状态按 `.ingest-state.json` 结构规格写入文件，打印 `[DISCUSS] <词条名>` 并 exit 2；`--continue <file_path>` 时读取 `.ingest-state.json` 恢复上下文，跳至步骤 9，执行完毕后删除该文件）→ 步骤 9–11 更新 index/overview/log → 步骤 12 git 提交；复用 `common.py` 的共享工具
- **脚本严禁使用 `input()` 等阻塞式等待**

---

## 五、增量合并与冲突处理协议

### 5.1 增量合并

新笔记摄入时，先检索 `Wiki/` 是否已有对应词条：
- **无**：根据对应模板新建词条
- **有**：对比 Diff，将新物料细节无缝缝合进对应章节，严禁粗暴覆盖旧词条
- **注意**：若新词条仅是已有词条的参数化变体、局部实现或狭窄场景特例，优先合并进已有词条。

### 5.2 冲突处理协议

**【冲突权威定义】**：以下任一情况视为冲突，禁止 Agent 自行裁判，强制挂起：
- 核心定义段出现直接否定关系（新料与已有词条对同一命题给出相反断言）
- 数值、年份、因果方向明确不一致
- 同一词汇在新料与已有词条中指向完全不同的对象
- **核心概念定义发生结构性重构**：新料对词条的核心定义不是"增补细节"，而是"重构组成要素或要素关系"——判断标准：若按新料改写后，原有的定义将完全无法成立（而非仅被补充或细化）。例：旧词条定义 A 为"属性 X"，新料论证 A 必须被理解为"X 与 Y 的必然同时在场"，则原定义被结构性替换，强制挂起。

冲突处理格式，强制写入词条：

```markdown
> ⚠️ 争议：
> - 说法 A（来源：[[Raw///旧笔记.md]]）：……
> - 说法 B（来源：[[Raw///新文件.md]]）：……
> 待研究者人工裁决。
```

同时将该词条 YAML 中的 `pending_review` 强行修改为 `true`，挂起等待研究者指示。

**【pending_review 裁决流程】**：研究者完成裁决后，告知 Agent 处理结果（保留说法 A / 保留说法 B / 两者并存并注明适用场景）。Agent 收到裁决指令后：
1. 删除词条中的 `⚠️ 争议` 块，按裁决结果更新正文内容
2. 将该词条 YAML 中的 `pending_review` 改回 `false`
3. 更新 `last_updated` 为当日日期
4. 追加日志：`## [YYYY-MM-DD] chore | 裁决 pending_review: <词条名>`
5. Git 提交：`git add Wiki/ && git commit -m "chore: resolve pending_review <词条名>"`

> `health.py` 检查项中包含 `pending_review: true` 词条扫描，运行 `health` 时会列出所有待裁决词条，提示研究者处理。

### 5.3 消歧触发规则

一旦发现同一词汇在不同传统或领域下存在实质性定义撕裂：
1. 将原词条升级为消歧导航页（套用 §3.4 模板）
2. 为每个独立含义创建独立词条（文件名：`概念（流派）.md`）
3. 若原始笔记未明确指明流派，输出警告，挂起等待人工确认，不强行分配

---

## 六、查询工作流（Query Workflow）

**触发**：`query: <问题>` 或自然语言提问

**【脚本检查】**：若需要命令行查询，检查 `Tools/query.py` 是否存在；不存在则先生成（规格见本节末尾）。

查询工作流不只是被动回答，而是知识库生长的主动驱动器。每次查询可能触发三个层次的生长机制。

**执行步骤**（内联推进，不创建追踪清单）：

**步骤 1. 开放问题预读**：检索前，先扫描 `Wiki/syntheses/` 中 `status: open` 的词条，作为"已知开放问题"的上下文背景，避免重复推导已知盲区。

**步骤 2. 语义主检索**：

优先使用 qmd（通过 `common.QMD_AVAILABLE` 常量判断）；否则逐级降级：

```bash
# 优先路径
qmd query "<问题关键词>" --collection wiki --format json -n 8

# 降级路径一：读取 Wiki/index.md，关键词匹配，结合 Graph/graph.json（若存在）做邻居扩展

# 降级路径二（index 匹配不足时）：全文搜索
grep -r "<关键词>" Wiki/ --include="*.md" -l
```

读取命中词条，综合答案，使用 `[[词条名]]` 内联引用标注来源。

**【富格式输出契约】**：根据问题特质主动丰富输出形式：
- **结构化对比**（多流派 / 配置 / 策略对比）→ 提供 Markdown 对比表格
- **数值序列 / 趋势**（数据指标对比）→ 附带 Python matplotlib 绘图代码或 ASCII 趋势图
- **汇报演示**（用户明确提到汇报、演示）→ 使用 Marp Markdown 幻灯片格式输出

**步骤 3. 盲区回退**：若 Wiki 集合无命中，降级检索 Raw 集合（同样通过 `common.QMD_AVAILABLE` 判断）：

```bash
# 优先路径
qmd query "<问题关键词>" --collection raw --format json -n 8

# 降级路径：直接读取 Raw/ 相关文件做关键词匹配
grep -r "<问题关键词>" Raw/ --include="*.md" -l
```

- Raw 命中 → 基于原始笔记作答，末尾附注警告，同时触发生长层次二（见下）
- Raw 仍无命中 → 告知研究者该主题存在知识盲区，建议补充原始笔记

**步骤 4. 生长机制触发**：

**【生长层次一：综述归档】**：查询完成后，询问研究者是否归档本次答案：

> 📌 是否将本次答案归档为 `Wiki/syntheses/<slug>.md`？（Y/N，或指定路径）

slug 生成规则：将问题关键词翻译为 2–4 词英文语义词组（kebab-case），与 §三【命名规范】中 syntheses 规则一致，生成后记录至 log.md 的 `slug:` 字段以确保跨会话一致性。

**归档前执行 slug 冲突检查**：调用 `common.check_slug_conflict(slug, 'Wiki/syntheses/', 'query-synthesis')`——若冲突，询问研究者是否指定新 slug 或确认覆盖，不自动覆盖。

无冲突时归档并执行：

```bash
git add Wiki/index.md Wiki/log.md Wiki/syntheses/<slug>.md
git commit -m "query-synthesis: <问题关键词>"
```

若 qmd 可用（`common.QMD_AVAILABLE`）：`qmd embed --collection wiki`

**【生长层次二：盲区驱动摄入】**：当 Raw 命中时，强制询问：
> ⚠️ 检测到知识盲区：Wiki 层对「<问题关键词>」覆盖不足，但在 Raw 层发现相关文件：
> - `[[Raw/<子目录>/<路径>/xxx.md]]`
> 是否立即对上述文件执行 ingest 以填补盲区？（Y/N）

用户确认后，直接触发摄入工作流（§四）。

**【生长层次三：跨词条合成回哺】**：当答案综合了 **3 个及以上**不同 Wiki 词条时，自动提示归档选项（须用户显式确认后执行）；用户未确认或明确拒绝时，跳过回哺，继续对话，不挂起，不写入任何词条：
- 将跨词条洞见以 `（据查询合成，未经来源验证）` 加注，缝合进相关词条的 `🎯 核心论点` 章节，但不得加入 `📌 核心定义` 章节
- 在这些词条的 `related` 字段中补入新发现的关联词条双链
- 更新 `last_updated` 为当日日期
- 追加日志：`## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<slug>`
- Git 提交：
  ```bash
  git add Wiki/concepts/ Wiki/entities/ Wiki/index.md Wiki/log.md
  git commit -m "query-feedback: <问题关键词> 跨词条回哺"
  ```

**回哺硬性约束**：
- 回哺内容必须加注 `（据查询合成，未经来源验证）`，严禁伪装成一手事实
- 若回哺内容与词条既有内容存在矛盾，强制走冲突处理协议（§五 5.2），不得静默覆盖

---

**【query.py 最低规格】**（首次需要命令行查询时生成）：

- 入参：`"<问题>"` / `[--save]` / `[--save <path>]`
- 退出码：`0` = 成功
- 核心逻辑：
  1. 读取 `Wiki/index.md`，用关键词匹配筛选相关页面；若 `Graph/graph.json` 存在，对命中页面进行图谱邻居扩展
  2. **检索裁剪**：命中页面超过 8 个时，优先保留直接关键词命中页，邻居扩展页按相关性截断至总数不超过 12 个，避免上下文膨胀导致质量下降
  3. 综合命中页面，用 LLM 生成 Markdown 答案（含 `[[wikilink]]` 引用）
  4. **slug 生成**：将问题关键词翻译为 2–4 词英文语义词组（kebab-case），不得使用汉语拼音
  5. `--save` 或 `--save <path>`：**写入前调用 `common.check_slug_conflict(slug, 'Wiki/syntheses/', 'query-synthesis')`**——若 slug 已存在且来源为不同问题，打印 `[NEEDS_REVIEW] slug 冲突：<slug>.md 已存在` 并以 exit 2 退出，等待研究者指定新 slug 或确认覆盖；无冲突则将答案写入 `Wiki/syntheses/<slug>.md`，更新 index，追加日志（含 `slug:<slug>` 字段）
- **LLM 不可用时**：返回占位答案（包含命中的相关词条路径列表）并提示用户，不抛出未捕获异常；超时按同等处理。与 lint.py 降级策略一致。

---

## 七、健康检查工作流（Health Workflow）

**触发**：`health` | **频率**：每次会话启动规程中必跑 | **成本**：零 LLM 调用

**Health vs Lint 快速对比**（唯一权威来源，§八末尾不重复）：

| 维度 | `health` | `lint` |
|------|----------|--------|
| 范围 | 结构完整性 | 内容质量 |
| LLM 调用 | 零 | 是 |
| 成本 | 免费 | 消耗 token |
| 频率 | 每次会话，优先运行 | 每 10–15 次摄入 |
| 检查项 | 空文件、索引同步、日志覆盖、断链、Assets 断链、Raw 目录合规、哈希一致性、pending_review 扫描 | 孤儿、矛盾、过时综述、缺失实体、稀疏页、加注缺失、slug 冲突、语义近似词条检测（可选）、知识盲区推荐、图谱张力（可选） |

**【脚本检查】**：若 `Tools/common.py` 不存在，先生成它；若 `Tools/health.py` 不存在，先生成它（规格见本节末尾），验证通过后执行。

直接运行（内联步骤推进，不创建追踪清单）：`python Tools/health.py [--json] [--save]`

**检查项**：
- **空文件 / 存根页**：仅有 frontmatter、无正文内容的页面
- **索引同步**：`Wiki/index.md` 条目与磁盘实际文件是否一致
- **日志覆盖**：有词条页面但 `Wiki/log.md` 中缺少对应记录的情况。判断时须兼容 rename 追踪链：若词条文件名无直接对应的 `ingest` slug，但存在指向该文件名的 `chore | rename` 记录（即该词条由旧 slug 重命名而来），视为合法，不报警；两种情况均不满足才报"日志覆盖缺失"
- **断链检查**：`[[双链]]` 指向不存在页面的情况
- **Assets 断链检查**：Wiki 词条中引用的图片路径在磁盘上不存在的情况
- **Raw 目录合规**：`Raw/` 下是否存在预设子目录以外的其他子目录或文件。**豁免规则**：名称以 `.` 开头的文件/目录（如 `.DS_Store`）及 `Thumbs.db` 视为系统临时文件，跳过不报警；仅对其他不在允许列表中的条目发出警告
- **哈希一致性检查**：**仅扫描操作类型为 `ingest` 且含 `sha256:` 字段的记录**（`chore`/`query`/`ERROR` 等操作类型的记录不含该字段，跳过），对每条记录执行以下分支判断，输出**不同类型**的警告，确保研究者能区分两类本质不同的情况：
  - 对应路径的文件**不存在**于磁盘 → 输出 `⚠️ [路径不存在] <路径>：文件可能已被移动或删除，如已移动请执行 chore: move 更新路径记录，如已删除请执行 chore: delete 清理日志悬空记录`
  - 文件存在但**哈希不匹配** → 输出 `⚠️ [内容已修改] <路径>：当前哈希与摄入时记录不一致，请确认是否需要重新摄入`
  - 两项均正常 → 通过，不输出
- **pending_review 扫描**：列出所有 `pending_review: true` 的词条，提示研究者裁决

`--save` 参数将报告写入 `Wiki/health-report.md`。若需纳入版本控制，研究者手动 `git add -f Wiki/health-report.md && git commit`。

---

**【common.py 最低规格】**（任何工具工作流首次触发时优先生成）：

- **路径常量**：`REPO_ROOT`（基于 `pathlib.Path(__file__).resolve().parent.parent` 推算，确保无论从哪个工作目录调用脚本均能正确定位仓库根目录）、`WIKI_DIR`、`RAW_DIR`、`GRAPH_DIR`、`LOG_FILE`、`INDEX_FILE`、`OVERVIEW_FILE`
- **解释器常量**：`PYTHON_BIN` — 在 `REPO_ROOT` 定义之后，基于 `REPO_ROOT` 探测虚拟环境路径，按平台分支检查，取第一个可用路径；其他脚本 subprocess 调用 Python 时统一使用此常量：

  ```python
  import sys, os
  from pathlib import Path

  REPO_ROOT = Path(__file__).resolve().parent.parent

  def _detect_python():
      if sys.platform == "win32":
          candidates = [
              str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
              str(REPO_ROOT / "venv" / "Scripts" / "python.exe"),
              "python",
          ]
      else:
          candidates = [
              str(REPO_ROOT / ".venv" / "bin" / "python"),
              str(REPO_ROOT / "venv" / "bin" / "python"),
              "python3",
              "python",
          ]
      for c in candidates:
          if os.path.isfile(c) or c in ("python3", "python"):
              return c
      return "python"

  PYTHON_BIN = _detect_python()
  ```

- **qmd 可用性缓存**：`QMD_AVAILABLE` — 模块级常量，在模块导入时执行一次检测（`subprocess.run(["qmd", "--version"], ...)` 成功则为 `True`），后续所有调用直接引用此常量，避免每次调用重复 subprocess 开销；所有工作流脚本统一引用 `common.QMD_AVAILABLE`，**禁止各脚本自行重复检测**：

  ```python
  import subprocess as _sp

  def _check_qmd():
      try:
          _sp.run(["qmd", "--version"], capture_output=True, timeout=5, check=True)
          return True
      except Exception:
          return False

  QMD_AVAILABLE: bool = _check_qmd()
  ```

- **I/O 工具**：`read_file(path)` / `write_file(path, content)`（原子写入：先写同目录临时文件，`os.replace()` 重命名，自动创建父目录）/ `ensure_utf8()`
- **内容工具**：`extract_wikilinks(text)` / `all_wiki_pages()` / `append_log(entry)` / `resolve_wikilink(name)` / `load_allowed_raw_dirs()` — 读取 `.llm-wiki/raw-mapping.json`，返回所有目录条目列表；`ingest: true` 的目录可摄入，`ingest: false` 的目录（如 `Assets/`）不摄入但视为合法目录，health 合规检查以此为准
- **哈希工具**：`sha256_short(content)` → 返回 sha256 前 32 位十六进制字符串；`sha256_full(content)` → 返回完整 64 位十六进制字符串。**log.md 始终存储 `sha256_short`（前 32 位），所有去重校验与哈希一致性检查统一使用 `sha256_short`。**
- **LLM 调用**：`call_llm(prompt, ...)` — 依次尝试 `opencode` / `claude` CLI；支持 `LLM_BACKEND` 环境变量覆盖；`exit_on_error=False` 时返回占位符而非抛异常
- **Slug 冲突工具**：`check_slug_conflict(slug, target_dir, operation_type)` → 扫描 `target_dir` 磁盘文件及 `log.md` 中对应 `operation_type`（如 `ingest`、`query-synthesis`）的 `slug:` 记录，返回 `(conflict: bool, existing_source: str | None)`；冲突时由调用方决定输出 `[NEEDS_REVIEW]` 并 exit 2，不在此函数内部 exit
- **pending_review 工具**：`list_pending_review()` → 返回所有 `pending_review: true` 词条的路径列表，供 `health.py` 调用

**【health.py 最低规格】**（首次触发 health 时生成）：

- 入参：`[--json] [--save]`
- 退出码：`0` = 全部通过，`1` = 发现问题
- 检查项：空文件/存根页、索引同步、**日志覆盖**（兼容 rename 追踪链：直接 slug 匹配或存在指向该文件名的 `chore | rename` 记录，均视为合法；两者均不满足才报警）、断链、Assets 断链、**Raw 目录合规**（调用 `common.load_allowed_raw_dirs()` 读取 `.llm-wiki/raw-mapping.json`，允许列表中所有目录均合法；`Raw/` 下出现不在列表中的条目时报警，但**豁免**名称以 `.` 开头的文件/目录及 `Thumbs.db`）、**哈希一致性**（使用 `common.sha256_short`，**仅扫描操作类型为 `ingest` 且含 `sha256:` 字段的记录**；路径不存在时输出 `⚠️ [路径不存在]` 警告并提示执行 `chore: move` 或 `chore: delete`；路径存在但哈希不匹配时输出 `⚠️ [内容已修改]` 警告，提示确认是否重新摄入；两类警告须在报告中明确区分）、**pending_review 扫描**（调用 `common.list_pending_review()`，在报告中列出所有待裁决词条）
- `--save` 将报告写入 `Wiki/health-report.md`

---

## 八、质量审计工作流（Lint Workflow）

**触发**：`lint` | **频率**：每 10–15 次摄入后执行一次 | **前提**：必须在 health 通过后运行

> **"health 通过"最低门槛**：无断链、无空文件/存根页即可放行 lint。`pending_review` 待裁决词条、哈希不匹配警告、Assets 断链警告不阻塞 lint 运行；但若 health 报告存在断链（`[[双链]]` 指向不存在页面），必须先修复再运行 lint，避免孤儿页检查结果失真。

**【脚本检查】**：若 `Tools/lint.py` 不存在，先生成它（规格见本节末尾），验证通过后执行。

直接运行（内联步骤推进，不创建追踪清单）：`python Tools/lint.py [--save]`

**检查项**：
- **孤儿页**：无任何入站 `[[链接]]` 的 Wiki 页面
- **内容矛盾**：跨页面存在相互冲突的断言
- **过时综述**：有更新源笔记摄入后，相关词条未同步更新
- **缺失实体页**：在 3 个及以上页面中以 `[[wikilink]]` 形式被提及但没有独立词条的实体。**注意**：本检查仅统计 `[[双链]]` 形式的提及，不执行命名实体识别；建立双链是本仓库的核心实践，纯文本提及不计入
- **稀疏页**：出站 `[[双链]]` 少于 2 条的页面
- **加注缺失**：词条正文中来自 `Sources/` 的内容未加 `（据文献）`，来自 `Thoughts/` 的内容未加 `（个人思考）`，来自 `Records/` 的内容未加 `（个人经验）`
- **slug 冲突检测**：扫描 log.md 中所有 `slug:` 记录，检查是否存在相同 slug 对应不同来源文件的情况
- **语义近似词条检测**（LLM 辅助，可选）：识别标题或核心定义高度相似、可能需要合并或消歧的词条对，输出建议列表供研究者判断——不自动合并，仅建议
- **知识盲区与主动推荐**：识别 Wiki 无法回答的常见问题类型，列出具体的知识缺口描述，**并对每个盲区建议 1–3 条 web 搜索查询词**，便于研究者直接搜索后将结果放入 `Raw/Sources/` 补充知识库；还可根据当前知识结构推荐下一步值得深入研究的方向

> **断链检查归属 health**：`lint.py` 不重复执行断链检查，该项由 `health.py` 负责（结构完整性属于 health 职责范围）。

图谱感知检查（**可选**，需先运行 `build graph`，仅当 `Graph/graph.json` 存在时执行）：
- **枢纽存根（Hub Stubs）**：度数 > μ+2σ 但内容少于 500 字的节点
- **脆桥（Fragile Bridges）**：两个社区之间仅由 1 条边连接的情况
- **孤立社区**：与其他社区零外部连接的知识孤岛
- **冲突边密度**：`relation: contradicts` 的边占总边数的比例

输出审计报告，询问用户是否保存至 `Wiki/lint-report.md`。保存后 Git 提交。运行结束后自动追加日志记录。

**【Schema 演化提示】**：运行结束后，若审计发现了**反复出现的模式偏差**（如某类加注规则频繁缺失、词条分类边界产生歧义等），在报告末尾附加提示：

> 🔧 **AGENTS.md 演化建议**：本次审计发现以下模式可能需要修订规则——[具体描述]。建议与研究者讨论是否修订 AGENTS.md 中的对应条款，以避免同类问题在后续摄入中反复出现。

### Health vs Lint 边界

> 完整对比见本文件顶部【Health vs Lint 边界】速查表（§健康检查工作流 §七 与 §质量审计工作流 §八 各自的触发器、成本与检查项说明已完整列出，此处不重复）。一句话区分：**health 管结构完整性，零 LLM 调用，每次会话必跑；lint 管内容质量，消耗 token，每 10–15 次摄入跑一次，且须在 health 断链与空文件检查通过后才运行。**

---

**【lint.py 最低规格】**（首次触发 lint 时生成）：

- 入参：`[--save]`
- 退出码：`0` = 无严重问题，`1` = 发现严重问题
- 前提：必须在 health 通过后运行（最低门槛：无断链、无空文件/存根页；`pending_review` 和哈希警告不阻塞）
- 检查项：孤儿页、内容矛盾、过时综述、**缺失实体页**（仅统计 `[[wikilink]]` 形式的提及，不执行命名实体识别）、稀疏页、加注缺失、slug 冲突、**语义近似词条检测**（LLM 辅助，可选；输出建议列表，不自动合并）、知识盲区推荐（含 web 搜索建议）
- **不执行断链检查**（该项归属 `health.py`，避免重复）
- 图谱感知检查（可选，仅当 `Graph/graph.json` 存在时执行）：枢纽存根、脆桥、孤立社区、冲突边密度
- LLM 不可用时：将分析上下文 dump 至 `Wiki/_semantic_lint_context.md`，由 Agent 手动完成语义分析
- 运行后追加日志（复用 `common.append_log()`）
- 报告末尾包含 AGENTS.md 演化建议段落（若发现反复出现的模式偏差）

---

## 九、知识图谱工作流（Graph Workflow）【可选扩展】

> **适用时机**：知识库积累到一定规模（建议 50+ 词条）后再考虑启用。初期无需使用。

**触发**：`build graph`

**【脚本检查】**：若 `Tools/build_graph.py` 不存在，先生成它（规格见本节末尾），验证通过后执行。

直接运行（内联步骤推进）：`python Tools/build_graph.py [--open] [--report] [--save] [--no-infer]`

**LLM 调用说明**：
- **Pass 1（默认）**：扫描所有 Wiki 页面，提取显式 `[[双链]]` 构建基础图谱，**零 LLM 调用**
- **Pass 2（可选）**：语义推断隐性关联边，**消耗 token**。需设置环境变量 `LLM_MODEL_FAST` 启用；未设置时自动跳过

**输出**（直接写入 `Graph/` 根目录，**无子目录**）：
- `Graph/graph.json`：节点与边的结构化数据
- `Graph/graph.html`：基于 vis.js 的自包含可视化页面（`contradicts` 边红色高亮）
- `Graph/graph-report.md`：图谱健康报告（`--report --save` 时生成）

```json
{
  "nodes": [{"id": "concepts/X", "label": "X", "degree": 5}],
  "edges": [
    {"from": "concepts/A", "to": "concepts/B", "type": "EXTRACTED", "relation": "supports"}
  ],
  "inferred_edges": [
    {"from": "concepts/E", "to": "concepts/F", "confidence": 0.7, "type": "INFERRED"}
  ],
  "built": "YYYY-MM-DD"
}
```

Git 提交：

```bash
git add Graph/
git commit -m "graph: rebuild graph data"
```

**图谱健康报告指标**：
- **健康摘要**：边/节点比、孤儿占比、社区数量、链接密度
- **上帝节点（God Nodes）**：度数 > μ+2σ 的枢纽页面
- **枢纽存根（Hub Stubs）**：被大量链接但自身内容少于 500 字的空壳
- **脆桥（Fragile Bridges）**：两个大社区间仅 1 条边连接的脆弱地带
- **幽灵枢纽（Phantom Hubs）**：被 2 个及以上页面引用但本身不存在的页面
- **冲突边密度**：`relation: contradicts` 的边占总边数的比例

**硬性规则**：图谱层禁止从断链自动创建页面，只报告；隐性关联（`INFERRED`）仅存入 `graph.json`，不自动写入页面正文，由研究者决定是否手动添加双链。

---

**【build_graph.py 最低规格】**（首次触发 build graph 时生成）：

- 入参：`[--open] [--report] [--save] [--no-infer]`
- 退出码：`0` = 成功，`1` = 硬错误（如无法读取 Wiki 目录）
- Pass 1（默认）：提取显式 `[[双链]]` 及 `related:` 字段的语义边类型注释，零 LLM 调用
- Pass 2（可选）：设置环境变量 `LLM_MODEL_FAST` 启用语义推断边；未设置时静默跳过；**执行期间每处理 10 个节点向终端输出一条进度（如 `[Pass 2] 语义推断中 (10/50)...`），避免 Agent 或用户误判进程已死**
- 输出：`Graph/graph.json` 和 `Graph/graph.html`（vis.js 自包含可视化，`contradicts` 边红色高亮）
- `--report --save` 将图谱健康报告保存至 `Graph/graph-report.md`（**直接在 `Graph/` 下，不是 `Graph/reports/`**）
- 运行后追加日志（复用 `common.append_log()`）

---

## 十、命名规范与索引格式

> 命名规范的唯一权威来源见 §三【命名规范】表格，本节仅补充索引与日志格式。

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

> **日期时区说明**：所有日志日期统一使用 Agent 运行环境的系统本地日期（`date +%Y-%m-%d`），不强制 UTC。跨时区协作时，研究者可在 AGENTS.md 顶部注释中指定时区偏好，Agent 按该设置生成日期。

- **正常摄入记录**：`## [YYYY-MM-DD] ingest | <标题> | [[Raw/<子目录>/<路径>/<文件名>]] | sha256:<前32位十六进制> | slug:<slug>`
- **query-synthesis 记录**：`## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<slug>`
- **其他正常记录**：`## [YYYY-MM-DD] <操作> | <标题>`
- **失败记录**：`## [YYYY-MM-DD] ERROR | <操作> | <原因>`

操作类型：`bootstrap` / `ingest` / `query` / `query-synthesis` / `health` / `lint` / `graph` / `chore` / `ERROR`

**`chore: move` 协议**：当研究者重命名或移动 `Raw/` 中已摄入的文件时，说 `chore: move <旧路径> → <新路径>`，Agent 执行：
1. 在 `Wiki/log.md` 中找到对应旧路径的 `ingest` 记录，在其下方追加一条 `chore` 记录说明路径变更（原记录不可修改，保持 `log.md` 只增不改原则）
2. 扫描所有 Wiki 词条，将 `[[Raw/<旧路径>]]` 形式的双链更新为新路径
3. 追加日志：`## [YYYY-MM-DD] chore | move: [[Raw/<旧路径>]] → [[Raw/<新路径>]]`
4. Git 提交：`git add Wiki/ && git commit -m "chore: update raw path <旧文件名> → <新文件名>"`

> **注意**：`health.py` 的哈希一致性检查通过路径查找文件；文件移动后路径变更，health 会报 `⚠️ [路径不存在]` 警告（区别于文件修改时的 `⚠️ [内容已修改]` 警告），此时执行上述 `chore: move` 协议即可消除警告。执行 `chore: move` 后若 health 仍报 `[路径不存在]`，说明 move 记录中的新路径有误，请核查。

**`chore: rename Wiki/` 协议**：当研究者需要重命名 `Wiki/` 下某个词条（纠正错别字、合并同义词、调整分类）时，说 `chore: rename Wiki/<旧路径> → Wiki/<新路径>`，Agent 执行（**不重新摄入内容**，仅做路径更新）：
1. 将词条文件从旧路径重命名为新路径（使用操作系统 `mv` 或等效操作）
2. 扫描所有 Wiki 词条，将所有 `[[Wiki/<旧路径>]]` 形式的双链更新为新路径
3. 更新 `Wiki/index.md` 中对应的条目链接与标题
4. 追加日志：`## [YYYY-MM-DD] chore | rename: [[Wiki/<旧路径>]] → [[Wiki/<新路径>]] | slug:<新文件名去后缀>`
5. Git 提交：`git add Wiki/ && git commit -m "chore: rename wiki entry <旧文件名> → <新文件名>"`

> **注意**：仅重命名路径，不触发任何摄入或重新摘要流程。若新名称与已有词条冲突，输出警告并挂起，等待研究者确认。

**`chore: delete` 协议**：当研究者已从 `Raw/` 中删除某个已摄入的文件，或确认某条 `[路径不存在]` 警告对应的文件确实应当从知识库中移除时，说 `chore: delete <Raw路径>`，Agent 执行：
1. 在 `Wiki/log.md` 中找到对应路径的 `ingest` 记录，在其下方追加一条删除记录（原记录不可修改，保持 `log.md` 只增不改原则）
2. 检查 Wiki 词条中是否存在指向该路径的 `[[双链]]`；若存在，扫描并标注为 `（来源已删除，原路径：<路径>）`，提示研究者决定是否同步删除对应词条
3. 追加日志：`## [YYYY-MM-DD] chore | delete: [[Raw/<子目录>/<文件名>]]`
4. Git 提交：`git add Wiki/ && git commit -m "chore: mark raw source deleted <文件名>"`

> **注意**：`chore: delete` 不自动删除 Wiki 词条，仅标注悬空引用，最终删除决策由研究者做出。执行完毕后再次运行 `health`，`[路径不存在]` 警告应消失（health 将识别 delete 记录并视为合法）。

> **日志覆盖检查兼容性**：`health.py` 的"日志覆盖"检查须兼容 rename 追踪链。对 `Wiki/` 下每个词条文件，判断其是否有对应日志记录时，**同时接受**以下两种合法情况：
> - `ingest` 记录的 slug 与该文件名匹配（直接摄入，未重命名）
> - `ingest` 记录的 slug 与某旧文件名匹配，**且**后续存在 `chore | rename: [[Wiki/<旧路径>]] → [[Wiki/<新路径>]]` 记录，新路径与该文件名匹配（经过重命名的词条）
>
> 不满足上述任一情况的词条，才报"日志覆盖缺失"警告。

> **失败可追溯原则**：ERROR 记录与正常记录**同构**。Agent 遇到不可恢复失败时，必须：
> 1. 立即写入 ERROR 记录到 `Wiki/log.md`
> 2. 继续执行后续独立步骤，不因单点失败阻塞整个工作流
> 3. 在工作流结尾输出"⚠️ 本次执行产生了 N 条 ERROR 记录，见 log.md"汇总

> **Log 优先原则**：正常摄入时，步骤 11（追加日志）必须在步骤 8（写入词条）完成后**立即**执行，不得推迟到步骤 12（git 提交）之后。这样 health 的"日志覆盖"检查可以发现词条已写入但日志缺失的半更新状态，避免静默数据不一致。所有词条文件写入使用 `common.write_file()`（原子写入：先写临时文件再 `os.replace()` 重命名），确保单文件写入的完整性。

---

## 十一、临时文件处理规范

**硬性原则**：所有临时生成、与知识库无直接关系的辅助文件，直接删除，绝不进入 Git 跟踪。

| 类型 | 典型示例 | 默认行为 |
|------|----------|----------|
| Lint 上下文 dump | `Wiki/_semantic_lint_context.md` | 删除 |
| 摄入状态文件 | `.ingest-state.json` | 脚本执行完毕后自动删除；`.gitignore` 屏蔽 |
| 图谱缓存 | `Graph/.cache.json` | `.gitignore` 屏蔽 |
| 工具中间输出 | `Tools/__pycache__/`、`*.pyc` | `.gitignore` 屏蔽 |
| 检索索引目录 | `.qmd/` | `.gitignore` 屏蔽 |
| Obsidian 配置 | `.obsidian/`、`workspace.json` | `.gitignore` 屏蔽 |
| 工具运行报告 | `Wiki/health-report.md`、`Wiki/lint-report.md` | `.gitignore` 屏蔽（用户确认保存后手动 `git add -f`） |

**执行纪律**：Agent 在执行 `git add` 前，必须先清理工作目录中的临时文件。

---

## 3. 使用方法

```bash
# 1. 复制本文件到目标目录
cp LLM_Wiki_Bootstrap_v1.0.md /path/to/new-vault/

# 2. 切换到目标目录
cd /path/to/new-vault

# 3. 在 AI 助手（Claude Code / Cursor 等）会话中说：
#    "请阅读 LLM_Wiki_Bootstrap_v1.0.md 并严格执行其中的 bootstrap 工作流"
```

bootstrap 完成后，Agent 会打印完整目录树与下一步操作提示（见 §1.12）。

---

## 4. 设计哲学

这套系统的本质是**隔离与编译**，加上**最小摩擦**。

人与 Agent 的分工是这个系统能长期运转的根本：人掌管 Raw 层（策源、策略、目录结构），Agent 掌管 Wiki 层（整理、交叉引用、维护一致性）。这个边界不可模糊——Agent 不干涉 Raw 层的任何决策；人不需要亲自做 Wiki 层的维护工作。

**反幻觉的十个机制**：
1. 目录决定加注类型 → 消除 Agent 对归属的主观猜测
2. 冲突处理协议（§五）→ 矛盾不掩盖，挂起等待人工裁决，裁决后有明确闭环流程
3. 禁止自我引用（§二）→ 防止 AI 把自己的总结当事实循环论证
4. 禁止推断型事实填补（§二）→ 缺失即缺失，不以"合理推断"代替实际来源
5. 查询合成强制加注（§六）→ 跨词条推论永远标注"未经来源验证"，可追溯且不污染一手事实层
6. Lint 加注缺失检查（§八）→ 定期审计加注执行情况
7. 哈希一致性检查（§七）→ 区分"路径移动"与"文件修改"两类警告，防止静默数据脱节
8. Log 优先原则（§十）→ 词条写入后立即记录日志，health 可检测半更新状态
9. raw-mapping.json 持久化目录映射（§.llm-wiki）→ 避免运行时解析 Markdown 表格产生歧义
10. chore: delete 协议（§十）→ 为已删除 Raw 文件提供明确的清理路径，消除持续的悬空警告

**默认自动执行，例外才挂起**：知识库只有在维护成本足够低时才能长期运转。查询归档、冲突裁决是例外：写入 Wiki 的重要决策由研究者确认，不由 Agent 代劳。

**脚本按需生成**：工具脚本在首次需要时生成，而非预先批量产出。这确保每个脚本生成时上下文充分、token 预算充足，且只生成真正用到的脚本，避免维护从未运行过的代码。

**Schema 共同演化**：AGENTS.md 不是一份一劳永逸的宪法，而是随使用习惯不断精化的活文档。研究者与 Agent 在协作中发现规则偏差时，应主动讨论并修订，让规则与实际使用场景保持一致。
