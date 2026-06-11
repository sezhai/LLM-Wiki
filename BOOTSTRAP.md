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
├── .env.example               # 环境变量模板（复制为 .env 后填入实际值）
├── .llm-wiki/                 # 机器可读配置（纳入 git 跟踪）
│   ├── raw-mapping.json       # Raw 子目录→加注类型映射（§1.4 末尾生成）
│   └── config.json            # 摄入风格等运行时配置（§1.4 末尾生成）
├── Raw/                       # 只读事实池（Agent 严禁除读取之外的任何操作）
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
└── Tools/                     # 工具脚本（按需生成，纳入 git 跟踪）
    ├── __init__.py            # 空文件，使 Tools/ 成为 Python 包（bootstrap 时创建）
    └── requirements.txt       # Python 依赖（§1.6b 生成）
```

> **脚本生成原则（唯一权威位置：AGENTS.md §"脚本生成原则"一节）**：Tools/ 脚本**不在 bootstrap 阶段预生成**。`common.py` 在首次触发任何工具工作流时生成（作为共享依赖先行），其余脚本在首次触发对应工作流时按需生成。生成后立即运行验证，修复通过后才 git 提交。

---

## 1. 执行工作流（严格按序）

### 1.0 创建步骤追踪清单

**首先**通过 Agent 可用的任务追踪机制（`todowrite` / `TodoWrite` / 内联 Markdown 清单，视 Agent 环境自动选择）创建追踪清单，步骤 0 本身立即标记完成，其余初始为待处理。每完成一步立即更新状态，最终输出前确认清单全部完成：

- [x] 0. 创建步骤追踪清单
- [ ] 1. 向用户询问关键配置
- [ ] 2. 验证并清理目标目录
- [ ] 3. 创建物理目录结构
- [ ] 4. 写入 `AGENTS.md`（含步骤 4 末尾立即写入 `.llm-wiki/raw-mapping.json` 和 `.llm-wiki/config.json`）
- [ ] 5. 写入 `README.md`
- [ ] 6. 写入 `.gitignore`
- [ ] 6b. 写入 `Tools/requirements.txt` 和 `.env.example`
- [ ] 7. 写入 `Wiki/` 初始核心文件
- [ ] 8. 初始化 Git 仓库（含用户配置兜底）
- [ ] 9. 追加 bootstrap 记录到 `log.md`
- [ ] 10. 清理临时文件（如有）
- [ ] 11. 首次 Git 提交（含完整 `git add`）
- [ ] 12. 最终验证与报告

### 1.1 向用户询问关键配置

**在写入任何文件之前**，通过一次对话确认以下四项。若用户拒绝回答或说"用默认"，使用括号内的默认值：

1. **Raw 层目录**：使用默认四类目录（`Sources / Thoughts / Records / Assets`），还是自定义？（默认：使用四类默认目录。若自定义，请用户列出目录名及各自的加注类型，后续所有涉及 Raw 子目录的规则均以用户提供的映射为准）

2. **Git 远程**：是否配置 `origin`？若是，提供 URL。（默认：暂不配置）

3. **摄入风格偏好**：
   - **A（批量自动）**：说 `ingest` 时自动处理所有未摄入文件，结尾汇总新建词条供复盘（默认）
   - **B（单次参与）**：每次只处理一个文件，词条草稿写入后与研究者讨论关键要点，确认后再继续下一个

   用户的偏好将被写入 AGENTS.md §四摄入工作流首部，**同时写入 `.llm-wiki/config.json` 的 `ingest_style` 字段**，作为后续每次触发 `ingest` 的默认行为。

4. **Raw/ 版本控制策略**：Raw 层原始文件是否纳入 git 跟踪？（默认：**不纳入**，研究者自行管理。选择"纳入"时，bootstrap 在首次提交中执行 `git add Raw/`，并在 `README.md` 及 AGENTS.md §四摄入工作流步骤 14 中将"手动执行"改为"自动执行"。此策略写入 `.llm-wiki/config.json` 的 `track_raw` 字段，所有后续章节通过读取该字段确定行为，不在多处重复描述。）

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
- `.llm-wiki/` 目录在此步骤创建；`raw-mapping.json` 和 `config.json` 在 §1.4 写入 AGENTS.md 后立即生成（见 §1.4 末尾说明）
- `Graph/` 初始仅预建根目录；`graph.json` / `graph.html` / `graph-report.md` 由脚本运行时自动生成，**无需预建**
- `Tools/` 初始预建根目录，并**立即创建空文件 `Tools/__init__.py`**（使 Tools/ 成为 Python 包，确保 `python -c "import Tools.common"` 等验证命令正常工作）

**Python 版本要求**：Python 3.9+（所有工具脚本均基于此版本开发；`match` 语句等 3.10+ 特性不使用，确保广泛兼容）。

### 1.4 写入 `AGENTS.md`

使用本文档 §2 的完整模板，按以下规则替换所有占位符：

| 占位符 | 替换为 |
|--------|--------|
| `<YYYY-MM-DD>` | 今日日期（ISO 8601） |
| `<raw-dir-table>` | 用户在 §1.1 确认的 Raw 子目录映射表（**含完整 Markdown 表格**，默认如下）；替换时将占位符行与其下方的 HTML 注释行一并删除，仅保留实际表格内容 |
| `<ingest-style>` | 用户在 §1.1 确认的摄入风格偏好（A 或 B，附简短说明）；替换时将整行 HTML 注释替换为实际风格文字 |

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

用户自定义目录时，按相同结构生成对应条目。`ingest: false` 的目录在"Raw 目录合规"检查中视为合法目录，不触发警告。

**写入 `.llm-wiki/config.json`**（与 `raw-mapping.json` 同步生成）：

```json
{
  "version": 1,
  "ingest_style": "A",
  "track_raw": false
}
```

用户选择风格 B 时，将 `"ingest_style"` 改为 `"B"`。用户选择纳入 Raw/ 版本控制时，将 `"track_raw"` 改为 `true`。`common.load_config()` 函数读取此文件；`ingest.py` 通过 `common.load_config()` 获取两个字段。

### 1.5 写入 `README.md`

内容要点（用第二人称，5 分钟内可读懂）：

- 一句话定位：这是个人 LLM 知识库，`Raw/` 放原始材料，`Wiki/` 是结构化沉淀
- **Raw 层目录说明**（按用户在 §1.1 确认的目录列出，默认为四类）：
  - `Sources/`：放他人文档（论文、剪藏、书籍）→ Agent 摄入时加注 `（据文献）`
  - `Thoughts/`：放自己写的研究笔记与思辨 → Agent 摄入时加注 `（个人思考）`
  - `Records/`：放个人记录（交易日志、聊天记录、日记）→ Agent 摄入时加注 `（个人经验）`
  - `Assets/`：图片与 PDF 附件（仅作为其他文件的附件被引用，不独立摄入）
- **Wiki 层用户可见分类**（`sources/` 与 `syntheses/` 标注为自动生成，研究者无需手动管理）：
  - `concepts/`：概念词条（可以查询和浏览）
  - `entities/`：人物、机构、著作、事件
  - `sources/`（自动生成）：长文摘要，由摄入工作流自动维护
  - `syntheses/`（自动生成）：查询答案沉淀，由查询工作流自动归档
- **依赖安装提示**（高亮显示，三步上手之前）：
  > 首次使用前请先安装 Python 依赖：`pip install -r Tools/requirements.txt`
  > 这将安装 `markitdown`（非 Markdown 文件转换）和 `python-dotenv`（环境变量加载）。
- **三步上手**：
  1. 把文件放进 `Raw/` 对应子目录
  2. 在 AI 会话中说 `ingest` 触发摄入
  3. 说 `query: <问题>` 触发查询
- **Obsidian 设置提示**（高亮显示）：`Settings → Files and links` 中将 Attachment 路径设为 `Raw/Assets`，将 **New link format** 设置为 **Absolute path in vault**（绝对路径模式），确保 Obsidian 生成的链接与本仓库 `[[Wiki/concepts/xxx.md]]` 格式一致
- **工具脚本按需生成**：`Tools/` 下脚本并非预装。需要在对话中直接说 `health` 或 `ingest` 等触发词，Agent 将自动查阅 `AGENTS.md` 契约生成对应脚本并验证。脚本报错时直接在当前会话让 Agent 修复，不要新开会话。
- **Raw/ 版本控制**：按 bootstrap 时的配置说明当前策略（自动纳入 / 手动管理）。
- **overview 更新阈值调整**：若初期摄入阶段 `Wiki/overview.md` 更新过于频繁（通常因词条 `domain` 字段均为 `__unset`），可在 `AGENTS.md` 末尾添加注释 `# overview-update-threshold: 3`，Agent 读取后将触发条件调整为"3 个及以上不同领域词条"。
- **Graph 层说明**（标注为可选）：说 `build graph` 可生成知识图谱，是可选的进阶功能，前 50 次摄入无需使用。

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
.ingest-state.json

# 工具运行时生成的报告（需用户显式确认保存后才写入，此处仍屏蔽以防误提交）
Wiki/health-report.md
Wiki/lint-report.md
# Graph/graph-report.md 不屏蔽：由 build_graph.py --report --save 生成后通过
# git add Graph/ 自动入库，策略与 health/lint 报告不同（见 §九）

# OS 文件
.DS_Store
Thumbs.db

# 注意：.llm-wiki/ 目录（含 raw-mapping.json 和 config.json）需纳入 git 跟踪，此处不屏蔽
# 注意：Tools/__init__.py 需纳入 git 跟踪，此处不屏蔽
```

### 1.6b 写入 `Tools/requirements.txt` 和 `.env.example`

**`Tools/requirements.txt`**（最小依赖集，按需扩充）：

```
markitdown>=0.1.0
python-dotenv>=1.0.0
```

**`.env.example`**（环境变量模板，复制为 `.env` 后填入实际值）：

```dotenv
# LLM 后端选择（可选值：openai-compatible；默认使用 OpenAI 兼容格式）
# LLM_BACKEND=openai-compatible
# OPENAI_API_BASE=http://localhost:8080/v1
# OPENAI_API_KEY=sk-xxxx

# 可选：默认模型名称（call_llm model=None 时使用此值；不设置则使用后端默认模型）
# LLM_MODEL=gpt-4o

# 可选：LLM 超时秒数（默认 300）
# LLM_TIMEOUT=300

# 可选：Pass 2 语义推断用的快速模型（不设置则跳过 Pass 2）
# LLM_MODEL_FAST=gpt-4o-mini
```

> **注意**：`call_llm()` 须原生支持读取 `OPENAI_API_BASE` 与 `OPENAI_API_KEY`，并使用标准的 OpenAI API 格式进行网络请求，确保可直接挂载任何本地或云端大模型推断服务。
>
> 研究者首次部署时：`cp .env.example .env`，按需填入实际值。`.env` 已由 `.gitignore` 屏蔽，不会入库。

### 1.7 写入 Wiki 初始核心文件

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
> **"不同领域"判断规则**：比较本次摄入词条的 frontmatter `domain` 字段值；两个词条的 `domain` 字段字符串不相同即视为"不同领域"，但须排除以下情况：两个词条的 `domain` 均为 `__unset` 或空值时，仍视为各自独立领域（相互之间触发 overview 更新），而非同一领域。`Wiki/sources/` 和 `Wiki/syntheses/` 类型词条的 `domain` 字段不参与本判断。
> **更新阈值调整**：若 overview 更新过于频繁（初期词条 `domain` 均为 `__unset` 时常见），可在 `AGENTS.md` 末尾添加注释 `# overview-update-threshold: 3`，Agent 读取后将阈值调整为 3 个及以上不同领域词条才更新。

```

**`Wiki/log.md`**（bootstrap 记录在 §1.9 写入）：

```markdown
# Wiki 操作日志

```

### 1.8 初始化 Git 仓库

```bash
git init
git branch -M main
```

### 1.9 追加 bootstrap 记录到 `log.md`

`Wiki/log.md` 末尾追加（将 `<YYYY-MM-DD>` 替换为当天日期；日期使用 Agent 运行环境的系统本地日期 `date +%Y-%m-%d`）：

```
## [<YYYY-MM-DD>] bootstrap | LLM Wiki OS v1.0 骨架建立
```

### 1.10 清理临时文件（如有）

在执行 `git add` 之前，检查并清理工作目录中的临时文件（`__pycache__/`、`*.pyc`、`*.tmp` 等）。Bootstrap 阶段通常不产生临时文件，本步骤作为防御性检查，确保 `git add` 前工作目录干净。

### 1.11 首次 Git 提交

```bash
git add AGENTS.md README.md .gitignore .env.example .llm-wiki/ Wiki/ Graph/ Tools/
git -c user.name="LLM Wiki Agent" -c user.email="agent@local" commit -m "chore: bootstrap LLM Wiki OS v1.0"
```

若用户在 §1.1 **选择纳入 Raw/ 版本控制**，在上述提交后追加：

```bash
git add Raw/
git -c user.name="LLM Wiki Agent" -c user.email="agent@local" commit -m "raw: add initial source materials"
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
  > 1. 先安装依赖：`pip install -r Tools/requirements.txt`
  > 2. 把他人文档放进 `Raw/Sources/`，自己的笔记放进 `Raw/Thoughts/`，个人记录放进 `Raw/Records/`
  > 3. 在 AI 会话中说 `ingest` 触发摄入（首次会先自动生成所需工具脚本）
  > 4. 说 `query: <问题>` 触发查询
  > 5. 说 `health` 检查仓库健康状态

---

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
| v1.0 | `<YYYY-MM-DD>` | 初始版本建立 | — |

> 当研究者与 Agent 发现某条规则反复产生不符合预期的结果时，应讨论是否修订本文件。修订后更新上表，并在 `log.md` 追加 `chore | AGENTS.md 修订 vX.X`。
>
> **overview 更新阈值**：若早期摄入阶段 `Wiki/overview.md` 更新过于频繁，可在本文件末尾添加注释 `# overview-update-threshold: 3`，Agent 读取后将触发条件调整为"3 个及以上不同领域词条才更新"。

---

## 会话启动规程（每次新会话必须首先执行）

```
1. 检查 Tools/common.py 是否存在
   ├── 不存在 → 先检查 .llm-wiki/ 目录及 JSON 配置是否完整
   │   ├── 配置缺失 → 提示研究者仓库可能损坏，建议 git checkout HEAD .llm-wiki/ 恢复后重试
   │   └── 配置完整 → 生成 common.py（见§七【common.py 最低规格】），验证通过后继续
   └── 存在 → 继续下一步
2. 运行 health 检查（说 health，见§七）
   └── 若 Tools/health.py 不存在：先生成它（见§七【health.py 最低规格】），验证通过后执行
3. 读取 Wiki/log.md 最近 10 条记录，了解上次会话的操作上下文
   ├── 若为全新仓库（log.md 仅含 bootstrap 记录），跳过"上次会话摘要"，直接进入步骤 4
   └── 统计上次 lint 之后新增的 ingest 记录条数；若达到 10 条及以上，主动提示：
       "⚡ 检测到上次 lint 后已新增 N 次摄入，建议在本次会话结束前运行 lint 进行质量审计。"
4. 读取 Wiki/index.md，获取当前知识库词条全貌
5. 报告：健康状态摘要 + 上次会话摘要（全新仓库则省略）+ 当前词条数 + lint 提示（如有）
6. 等待研究者指令
```

> **为什么**：Agent 没有跨会话记忆，上述步骤是建立上下文的最低成本方式。上下文窗口趋于饱和时（长会话后期），Agent 应主动提示研究者开启新会话。
>
> **lint 触发阈值说明**：默认阈值为 10 次 ingest。若研究者希望调整，可在本文件末尾添加注释 `# lint-trigger-threshold: 15`，Agent 读取后使用该值。

---

## 脚本生成原则（唯一权威位置）

**Tools/ 脚本按需生成，不在 bootstrap 阶段预生成。**

**全局脚本前置检查**：Agent 在执行任何工作流（如 ingest、query、lint 等）前，必须先物理检查对应的 `Tools/<script_name>.py` 是否存在。若不存在，立即查阅下文对应章节的"最低规格"进行生成，验证通过后方可执行业务逻辑。

生成顺序约束：
1. `common.py` 必须最先生成，在首次触发任何工具工作流时优先生成（其他所有脚本从此导入，禁止各自实现重复逻辑）
2. 其他脚本在首次触发对应工作流时生成
3. 生成任何脚本前，先检查 `common.py` 是否存在；不存在则先生成它

生成后立即验证（将 `<script_name>` 替换为实际脚本文件名）：

```bash
python Tools/<script_name>.py --help
```

> **依赖自修复机制**：若终端抛出 `ModuleNotFoundError`，Agent 须立即且静默地执行 `pip install -r Tools/requirements.txt`，随后再次运行验证，**严禁**因为缺少外部依赖而修改原本正确的 Python 源代码。

**例外**：`common.py` 是纯函数库，不含 CLI 入口，验证方式为：

```bash
python -c "import Tools.common; print('common.py OK')"
```

若报错，在同一会话内修复；验证通过后执行 `git add Tools/<script_name>.py && git commit -m "feat: add <script_name>"`。

> **`Tools/__init__.py` 说明**：bootstrap 阶段已创建此空文件。若因故缺失，重新创建：`touch Tools/__init__.py`。
> **Python 导包路径铁律**：由于所有工具脚本均通过 `python Tools/<script_name>.py` 运行，Python 默认会将 `Tools/` 作为工作目录，导致 `import Tools.common` 报错。因此，**所有生成的 Python 脚本（除 common.py 以外）顶部，在导入任何本地或第三方包之前，必须强制写入以下两行路径注入代码**：
`import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))`

---

## 快速触发指令

| 指令 | 触发工作流 | 说明 |
|------|-----------|------|
| `ingest` | 摄入工作流 | 扫描 `Raw/`，处理所有未摄入文件 |
| `ingest <file>` | 摄入特定文件 | 接受相对于仓库根目录或当前工作目录的路径，内部统一转为绝对路径后与 log.md 比对 |
| `ingest --continue` | 恢复风格 B 暂停 | 读取 `.ingest-state.json` 恢复中断的摄入（仅适用于 `[DISCUSS]` 暂停） |
| `ingest --resume-step9 <slug>` | 恢复步骤 9 | 仅适用于 `[NEEDS_REVIEW_WRITTEN]` 裁决完成后；Agent 同时负责继续处理剩余队列（见 §四） |
| `ingest --discard` | 清除状态文件 | 删除 `.ingest-state.json` 后重新开始，不执行摄入 |
| `query: <问题>` | 查询工作流 | 先查 Wiki，盲区回退至 Raw，新洞见自动织网 |
| `health` | 健康检查 | 结构完整性检查（零 LLM 调用，每次会话必跑） |
| `lint` | 质量审计 | 孤儿页、矛盾、盲区检查（每 10 次摄入后建议运行，见会话启动规程自动提示） |
| `build graph` | 图谱分析 | 【可选扩展】生成上帝节点、脆桥报告 |
| `chore: move <旧路径> → <新路径>` | Raw 文件迁移归档 | 见下方维护协议细则 |
| `chore: rename Wiki/<旧路径> → Wiki/<新路径>` | Wiki 词条重命名 | 见下方维护协议细则 |
| `chore: delete Raw/<路径>` | Raw 文件删除归档 | 见下方维护协议细则 |
| `chore: delete Wiki/<路径>` | Wiki 词条删除 | 见下方维护协议细则 |

或用自然语言描述，Agent 自行映射到对应工作流。

### 维护协议（chore）细则

当研究者触发上述 `chore:` 指令时，Agent 必须执行完整的引用更新与日志闭环：

- **路径重命名/移动（`move` / `rename`）**：1. 执行物理文件移动；2. 扫描并更新所有 Wiki 词条中的 `[[旧路径]]` 为 `[[新路径]]`；3. 更新 `index.md` 和 `overview.md` 中的链接；4. 在 `log.md` 追加 `chore | move` 或 `chore | rename` 记录；5. 执行 git 提交。对于 Raw 文件的 move，**不重新摄入内容**。
- **文件删除归档（`delete`）**：1. 追加 `chore | delete` 日志；2. 若删除 Wiki 词条，执行物理删除并清理 `index.md`；若删除 Raw 文件，仅清理日志悬空状态，不物理删除 Wiki 词条；3. 扫描全库，将所有指向已删除路径的双链替换为 `（来源已删除，原路径：<路径>）`；4. 执行 git 提交。消歧词条删除时亦走此流程，`log.md` 追加 `chore | delete Wiki/disambiguations/<词条名>`。

**执行纪律**：

- **ingest**：通过当前 Agent 环境可用的任务追踪机制创建该工作流各步骤的追踪清单，每完成一步更新一次状态
- **query / health / lint / graph**：使用内联步骤标注推进，不强制创建任务追踪条目
- **Python 解释器探测**：执行任何 `python` 命令前，按平台分支探测（见 §七 `PYTHON_BIN` 规格）；其他脚本通过 `subprocess` 调用时统一使用 `common.PYTHON_BIN`
- **Git 子进程容错**：所有 `git commit` 操作必须针对"无文件变更"的情况做防崩处理（Shell 命令追加 `|| true`，或在 Python 中屏蔽 Exit Code 1）
- **跨平台路径传参铁律**：Python 脚本内调用 `subprocess` **必须**使用列表传参，严禁拼接纯字符串；所有写入 Markdown 的路径（`[[双链]]`、`log.md` 记录）必须调用 `pathlib.Path(path).as_posix()` 强制转为正斜杠；`subprocess.run` 捕获输出时必须显式指定 `encoding="utf-8"`

---

## 一、路径规范

**【根目录定义】**：本契约所有路径及 Obsidian `[[双链]]` 均以 Vault 根目录（即包含 `AGENTS.md`、`Raw/`、`Wiki/`、`Graph/`、`Tools/` 的那一层）为唯一基准面。

**【双链绝对化】**：所有指向 Raw 层或 Wiki 层的链接，必须使用基于 Vault 根目录的绝对路径，严禁使用 `../` 等相对路径，确保 Obsidian Graph View 完整织网。链接**必须包含文件扩展名**（`.md`）。

示例：`[[Wiki/concepts/复杂系统.md]]`、`[[Raw/Sources/某论文.md]]`

**【index.md 例外】**：`index.md` 中的条目链接使用相对路径（如 `[概念名](concepts/概念名.md)`），因为 Obsidian 会将其渲染为同目录下的相对导航；其他所有 Wiki 内容（词条正文、frontmatter、log.md 引用）一律使用含扩展名的绝对双链格式。

---

## 二、Raw 层目录与加注规则

Raw 层由研究者完全掌管，Agent 只读取，不做任何修改或移动。Raw 层子目录在 bootstrap 时由研究者确认，Agent 根据文件所在目录**自动确定加注类型**（通过 `common.load_allowed_raw_dirs()` 读取 `.llm-wiki/raw-mapping.json`），无需猜测。

<raw-dir-table>

**【加注执行规则】**：

- `Sources/` 文件摄入时：他人文章中的推论、观点、概括写入 Wiki 时强制加注 `（据文献）`。示例：`某理论认为 X 是 Y 的充分条件（据文献）。`
- `Thoughts/` 文件摄入时：研究者自己的思考、判断、逻辑推演写入 Wiki 时强制加注 `（个人思考）`。示例：`休谟的同一性论证在数量与统一性边界处存在逻辑断层（个人思考）。`
- `Records/` 文件摄入时：所有主观内容、决策记录、经验总结写入 Wiki 时强制加注 `（个人经验）`。示例：`动量策略在高隐含波动率环境下失效概率显著上升（个人经验）。`

**【Sources 文件的双产物规则】**：摄入 `Raw/Sources/` 文件时，同时产生两类词条：
- `Wiki/sources/<slug>.md`（长文摘要页，不含 `domain` 字段，不参与 overview 更新判断）
- 关联的 `Wiki/concepts/<概念名>.md` 或 `Wiki/entities/<实体名>.md`（含 `domain` 字段，**必须填写**，参与 overview 更新判断）

若 `domain` 无法从文件内容判断，填 `__unset`，待后续 lint 或研究者手动补全。

**【Assets 定位与图片读取规则】**：`Assets/` 目录不独立摄入——图片本身不产生 Wiki 词条。当摄入含图片引用的 Markdown 文件时，图片处理方式取决于执行者：

**Agent 手动执行时**（`ingest.py` 尚未生成）：Agent 在该次摄入流程内读取被引用图片作为补充上下文。先完整读取文本，识别 `![[Raw/Assets/...]]` 或 `![](...)` 引用的图片路径，逐一尝试读取；图片不可读时按以下顺序降级：
- Agent 具备多模态能力但文件损坏/格式不支持 → 输出 `⚠️ 图片不可读: <路径>（原因：格式不支持或文件损坏）`，跳过
- Agent 本身不具备图像识别能力 → 输出 `⚠️ 图片不可读: <路径>（原因：当前 Agent 无多模态能力）`，跳过；在对应词条章节记录 `（图片引用：<路径>，内容待人工补充）`

两种情况均不阻塞摄入流程。可读图片信息补充进对应词条章节，标注 `（图示补充）`。

**脚本执行时**（`ingest.py` 已生成）：脚本识别文中图片路径后，在对应词条章节记录 `（图片引用：<路径>，内容待人工补充）`，并输出 `⚠️ 图片引用已标注（脚本模式无法读取内容）: <路径>`，不阻塞摄入流程。

**【禁止主观裁判】**：Agent 仅作为"知识整合编译器"，不得独立判断哪种研究观点或诠释"更正确"。

**【禁止自我引用】**：严禁将 Agent 自己之前在 Wiki 词条里写就的总结性言论，作为推导或佐证新事实的"客观证据"。禁止将查询合成内容作为后续推理的"客观依据"。

**【禁止推断型事实填补】**：当来源文件中某项信息缺失时，Agent **严禁**根据上下文合理性进行推断补全。缺失即缺失：标注为空白或写入 `（来源缺失，待补充）`，绝不以"看似合理"替代实际证据。

**【查询合成加注】**：由查询工作流跨词条合成产生的新推论，必须加注 `（据查询合成，未经来源验证）`，与直接来源于 Raw 层的事实明确区分。

**【Raw/ 版本控制策略】**：读取 `.llm-wiki/config.json` 中的 `track_raw` 字段确定当前策略。`true` 时，每次摄入的步骤 14 结尾自动执行 `git add Raw/ && git commit -m "raw: add source materials"`；`false` 时，步骤 14 仅输出提示，由研究者手动决定是否追踪。

---

## 三、词条元数据与排版规范

> **词条类型说明**：研究者需要关注和浏览的词条是 **concepts** 和 **entities** 两类。`sources/` 和 `syntheses/` 由 Agent 自动生成和维护，研究者无需手动管理。`disambiguations/` 在遇到歧义词时按需生成。

### 命名规范

| 词条类型 | 命名规范 | 示例 |
|----------|----------|------|
| 概念词条（`concepts/`） | 中文概念名（首选）或 `TitleCase.md`（仅当概念本身是英文专有名词或无通行中文译名时） | `纯粹理性批判.md`、`BullPutSpread.md` |
| 实体词条（`entities/`） | `TitleCase.md` | `ImmanuelKant.md` |
| 长文摘要（`sources/`） | `kebab-case.md`（英文语义词组，2–4 词） | `thinking-fast-and-slow.md` |
| 消歧词条（`disambiguations/`） | `概念（流派）.md` | `空（佛教）.md` |
| 综述页（`syntheses/`） | `kebab-case.md`（英文语义词组，2–4 词） | `karma-across-traditions.md` |

**【kebab-case 中文文件名规则】**：`Wiki/sources/` 和 `Wiki/syntheses/` 的文件名须为简短英文语义词组，严禁使用汉语拼音，严禁保留中文字符。中文源文件须先翻译为英文语义词组再生成文件名。示例：《人性论》→ `treatise-human-nature.md`；《非备兑期权平仓规则》→ `naked-option-exit-rules.md`。

**【slug 一致性原则】**：同一来源文件在不同会话中必须生成相同的 slug。生成 slug 后立即记录至 `log.md` 的 `slug:` 字段。若检测到 slug 冲突（相同 slug 对应不同来源文件），输出警告，等待研究者手动确认重命名，不自动覆盖。

**【跨语言同义词注意事项】**：`concepts/` 目录中可能同时存在中文词条（如 `涅槃.md`）和英文词条（如 `Nirvana.md`）指向同一概念。lint 工作流的"语义近似词条检测"应将跨语言同义对纳入检测范围，建议在两个词条之间添加相互的 `related` 引用，或将其中一个升级为消歧导航页。

### 3.1 标准概念词条（`Wiki/concepts/`）

```markdown
---
title: ""
type: concept
aliases: ["", "", ""]
domain: "<摄入时必填：根据文件所在 Raw/ 子目录或内容判断，建议值：哲学 / 经济学 / 技术 / 历史 / 心理学 / 社会学 / 自然科学 / 其他；无法判断时填 __unset>"
subdomain: ""
era: "<可选：历史时代 / 年份 / 无>"
tags: []
sources: ["[[Raw///...]]"]
related: ["[[Wiki/concepts/相关概念A.md]]"]
event_date:                    # 可选：知识内容指向的业务/历史时间（格式 YYYY-MM-DD），供研究者阅读参考，工具链不读取此字段
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

- **归入 Concept**：抽象的策略、定理、机制、算法、方法论、思想体系。判断标准：可复现、可泛化、不绑定唯一历史实例。
- **归入 Entity**：具有唯一历史身份的具体对象。判断标准：存在唯一时空坐标，无法被泛化复现。
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

> **关于 domain 字段**：`sources/` 词条不含 `domain` 字段，不参与 `Wiki/overview.md` 的跨领域更新条件判断。

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

> ⚠️ 若原始笔记未明确指明流派或语境，默认不写入任何消歧专页，输出警告，挂起等待研究者人工确认后分配。
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
event_date:                        # 可选：综述内容指向的业务/历史时间（格式 YYYY-MM-DD），供研究者参考
last_updated: YYYY-MM-DD
---

## 结论

## 论据与引用
- [[Wiki/concepts/概念A.md]]：……（据查询合成，未经来源验证）
```

---

## 四、摄入工作流（Ingest Workflow）

**触发**：`ingest` 或 `ingest <file>`

**当前摄入风格**：<ingest-style>（A = 批量自动，B = 单次参与；详见 §1.1 配置）

**【路径规范化】**：`ingest <file>` 接收的路径（绝对路径、相对于仓库根目录、相对于当前工作目录均可），在脚本入口处统一转为绝对路径（`pathlib.Path(arg).resolve()`），转换后再与 `log.md` 中记录的路径做 POSIX 格式比对。所有写入 `log.md` 的路径均存储为相对于仓库根目录的 POSIX 格式（如 `Raw/Sources/foo.md`）。

**【裸摄入默认行为】**：当用户发出 `ingest` 指令但未指定具体文件时，读取 `.llm-wiki/raw-mapping.json` 中 `ingest: true` 的所有目录，处理其中尚未被摄入的文件（`ingest: false` 的目录如 `Assets/` 跳过）。

**【超大文件处理】**：在读取源文件（步骤 5）前，检查文件字符数：若单文件超过 **200,000 字符**（约 100,000 汉字），输出警告并挂起，建议研究者手动拆分后重新摄入。若研究者确认 `--all-at-once`，照常执行但追加警告至日志。

**【批量摄入上限提示】**：扫描完成后，若待摄入队列超过 **5 个文件**，Agent 须暂停并提示：

> ⚠️ 检测到 N 个待摄入文件，超出单次处理建议上限（5 个）。
> - 输入 `ingest 5` 处理前 5 个（Agent 转换为 `python Tools/ingest.py --num 5`；**风格 B 模式下禁用此选项**）
> - 输入 `ingest all` 确认本次全量处理（Agent 转换为 `python Tools/ingest.py --all`）

> **风格 B 与超限提示**：风格 B 模式下，超限提示中**不显示** `ingest 5` 选项（因风格 B 禁用 `--num` 参数），仅显示 `ingest all`（逐个暂停机制不受影响）。

**【去重判断依据】**：扫描 `Wiki/log.md`，以文件**相对于仓库根目录的 POSIX 路径**与 SHA-256 前 32 位哈希双重匹配作为去重主键：
- 路径存在于 log.md 且当前文件哈希与 log.md 中记录的哈希一致 → 已摄入，跳过
- 路径存在于 log.md 但当前哈希不匹配 → 文件已被修改，执行 **ingest-fix vs ingest-update 双轨询问协议**（见下方）
- 路径不在 log.md，但存在以该路径为终点的 `chore | move` 记录 → 检查原 `ingest` 记录的哈希与当前文件哈希：一致则跳过，不一致则按"文件已修改"处理
- 路径既不在 log.md 也无对应的 `chore | move` 记录 → 未摄入，加入队列

**【ingest-fix vs ingest-update 双轨询问协议】**：当检测到已摄入文件的哈希与当前文件哈希不一致时，**在正式摄入之前**，强制输出以下询问：

> ⚠️ 文件内容已变化：`<路径>`
> 上次摄入哈希：`<旧哈希前8位>`，当前哈希：`<新哈希前8位>`
>
> 请选择处理方式：
> - **A（ingest-fix）**：原文件存在笔误/格式错误，本次是修正。重新摄入并**覆盖**原词条，日志追加 `chore | ingest-fix: <标题>`。
> - **B（ingest-update）**：原文件有实质性更新。重新摄入并走**增量合并流程**（§五 5.1）；若存在冲突信号则走冲突处理协议（§五 5.2）。日志追加 `ingest | <标题>（update）`。
> - **C（跳过）**：暂不处理此文件，保留现有词条不变。

**ingest-fix 完整闭环**：选择 A 后，Agent 以 `--fix <file_path>` 重跑 `ingest.py`。覆盖词条后，步骤 9 更新 `index.md` 中对应条目的简述（不新增条目，不删除条目）；若步骤 9 同时触发了 overview 更新条件，同步更新 `Wiki/overview.md`。步骤 11 在 `log.md` 已有 `ingest` 记录下方追加 `chore | ingest-fix: <标题>` 记录（两条记录均保留，便于 health 的日志覆盖检查通过）。步骤 12 精准 `git add` 被覆盖的词条路径、`Wiki/log.md`、`Wiki/index.md`、`Wiki/overview.md`（无变更时 `git add` 该文件不报错，容错处理）。

**【新摄入前残留清理】**：在扫描待摄入队列（步骤 1）开始前，检查仓库根目录是否存在 `.ingest-state.json`：
- **存在**：输出警告，挂起等待研究者确认（`ingest --continue` 恢复 / `ingest --discard` 删除），不自动删除。
- **不存在**：直接继续。

**前提原则**：凡研究者放入 `Raw/` 的文件，均视为已确认需要摄入，Agent 不做二次价值判断。

**支持格式**：`.md` 直接摄入；`.pdf`、`.docx`、`.pptx`、`.xlsx`、`.html`、`.txt`、`.epub` 等通过 [markitdown](https://github.com/microsoft/markitdown) 自动转换后摄入（通过 `common.MARKITDOWN_AVAILABLE` 判断可用性）；不可用则输出警告并跳过该文件（写入 ERROR 日志），不阻塞其余文件的摄入。`Raw/Assets/` 下的附件不摄入。

**执行步骤（严格按序）**：

> **步骤序列的双重身份**：以下步骤同时服务于两个目的：① 当 `Tools/ingest.py` 已存在时，这是 **ingest.py 的实现规格**——脚本按此逻辑运行，Agent 只需运行脚本并按退出码行事；② 当脚本**尚未生成**时，这是 Agent 的手动兜底操作路径。

**【ingest.py 存在时的 Agent 操作】**：
1. 创建追踪清单（仅含"运行脚本 → 按退出码处理"两步）
2. 运行：`python Tools/ingest.py [file_path ...]`
3. 按退出码行事：
   - exit 0 → 执行步骤 13（qmd 更新）和步骤 14（汇总）
   - exit 1 → 读取 log.md 中的 ERROR 记录，向用户汇报，继续下一文件
   - exit 2 → 将脚本打印的前缀标识内容转发至对话界面，等待研究者指令（见【exit 2 四种子情况的恢复路径】）

创建追踪清单并实时更新（脚本不存在时执行以下手动步骤）。

**步骤 1. 去重扫描**：读取 `Wiki/log.md`，扫描全部 `ingest` 记录，建立路径→哈希映射表，判断哪些文件需要处理。

**步骤 2. 计算文件哈希**（对进入队列的文件逐一执行）：使用 `common.sha256_short(file_path)` 计算，以二进制流（`rb`）模式读取源文件。取哈希前 32 位十六进制字符，用于步骤 11 的日志写入与后续去重校验。

**步骤 3. 确定加注类型**：调用 `common.load_allowed_raw_dirs()` 读取 `.llm-wiki/raw-mapping.json`，根据文件所在目录查找对应的 `annotation` 字段，确定本文件的加注类型。

**步骤 4. 检索预扫描**：摄入前，优先使用 qmd（通过 `common.QMD_AVAILABLE` 判断）；否则调用 `common.search_wiki(keyword, collection="wiki")` 获取可能相关的已有词条路径列表。命中相关词条则进入增量合并流程，无命中则判定为新建词条。本步骤**不涉及语义增强推断**——语义推断（Pass 2）仅属于图谱工作流（§九），摄入检索保持轻量。

**步骤 5. 读取源文件**：完整读取（非 Markdown 先自动转换）。读取前执行超大文件检查。含图片的 Markdown 文件按 §二【Assets 定位与图片读取规则】步骤处理。

**步骤 6. 读取 Wiki 上下文**：读取 `Wiki/index.md` 和 `Wiki/overview.md` 获取当前全貌。

**步骤 7. 执行摄入**：默认全自动执行，仅以下情况挂起（**冲突判断的完整权威定义见 §五 5.2**）：

- **情况 A — 检测到冲突信号**：见 §五 5.2，此处不重复条件描述。挂起并呈现冲突详情。
- **情况 B — 技术性失败**：文件损坏或编码异常，或文件转换失败。写入 ERROR 日志，跳过该文件继续处理队列。

> **新建词条无需确认**：直接写入，工作流结尾输出新建词条汇总供研究者复盘。

**步骤 7.5（Slug 冲突预检，内嵌于步骤 7 执行顺序中）**：在确定拟写入词条的文件名（slug）后、执行写入之前，调用 `common.check_slug_conflict(slug, target_dir, operation_type, is_update)` 执行冲突检查。

- **增量更新豁免机制**：若当前执行流是由"双轨询问协议"触发的 `ingest-update`，且拟写入的 slug 路径与步骤 4 检索到的**第一个命中词条**路径完全一致，则传 `is_update=True`，函数返回 `(False, None)` 直接跳过冲突检查，继续执行步骤 8。其他所有情况（新建词条、ingest-fix、非增量更新路径）传 `is_update=False`。步骤 4 返回多个命中词条时，仅以相关性最高（列表第一个）的词条路径做比对。
- 无冲突或触发豁免 → 继续执行步骤 8
- 发现实质冲突 → **挂起**，输出：
  > ⚠️ Slug 冲突：拟生成文件 `<slug>.md` 已存在，对应来源为 `[[Raw/.../<已有文件>]]`。请指定新的 slug，或确认覆盖（若两篇文件属同一主题的不同版本）。

**【exit 2 四种子情况的恢复路径】**：exit 2 有四种子情况，Agent 必须根据打印前缀区分：

- **`[HASH_CHANGED]`**（哈希变化待询问，词条未写入，状态文件未写入）：转发双轨询问至对话，等待选择；选 A 则以 `--fix <file_path>` 重跑，选 B 则以 `<file_path>` 重跑，选 C 则跳过。
- **`[NEEDS_REVIEW]`**（步骤 7/7.5 冲突，词条未写入，状态文件未写入）：转发至对话等待研究者指令；裁决后以 `python Tools/ingest.py <file_path>` 重新运行，仅处理该文件。若该文件原属批量队列，裁决完成后继续处理批量队列中的下一个文件（脚本在 exit 2 前已将剩余文件列表打印到 stderr，Agent 记录后逐个调用）。
- **`[NEEDS_REVIEW_WRITTEN]`**（步骤 8 中途冲突，词条已写入争议格式，状态文件未写入）：词条已写入含 `⚠️ 争议` 块的格式，`pending_review: true`。脚本在 exit 2 前同样须在 stderr 打印 `REMAINING_QUEUE: path1|path2|...`（与 `[NEEDS_REVIEW]` 一致）。研究者裁决完成、Agent 更新词条后，以 `--resume-step9 <slug>` 重新运行脚本，脚本接收 slug 参数后直接执行步骤 9–12。`--resume-step9` 完成后，Agent 从 stderr 捕获的 `REMAINING_QUEUE` 继续调用剩余文件，与 `[NEEDS_REVIEW]` 的处理方式完全对称。
- **`[DISCUSS]`**（风格 B 讨论暂停，词条已正常写入，状态文件已写入）：研究者确认后，Agent 以 `--continue` 恢复，脚本读取状态文件直接从步骤 9 继续。

**批量队列的 exit 2 通用原则**：`[NEEDS_REVIEW]` 和 `[NEEDS_REVIEW_WRITTEN]` 情况下，脚本在 exit 2 前须将**剩余未处理文件路径列表**打印到 stderr（格式：`REMAINING_QUEUE: path1|path2|...`），Agent 捕获后记录，裁决完成后按序继续调用，不终止整个摄入队列。

**【摄入风格 B 专项说明】**：当配置的摄入风格为 B 时，`ingest.py` 在每个文件的词条写入完成后（步骤 8 结束、步骤 9 执行前）将当前文件路径、slug、标题及剩余队列写入 `.ingest-state.json`，打印 `[DISCUSS] <词条名>` 并以 exit 2 退出。Agent 捕获后将词条草稿摘要转发至对话界面，研究者确认后，Agent 以 `--continue` 重新调用脚本，脚本读取状态文件从步骤 9 继续执行，**完毕后删除 `.ingest-state.json`**（删除时机：步骤 12 完成后，确保队列信息安全），然后继续队列中的下一个文件（完整执行步骤 2–12）。脚本**严禁**在步骤 8 之前 exit 2。

**`.ingest-state.json` 结构规格**（风格 B 暂停时写入，`--continue` 时读取，全队列处理完毕后删除）：

```json
{
  "version": 1,
  "file_path": "Raw/Sources/当前处理文章.md",
  "slug": "current-article",
  "title": "当前文章标题",
  "target_wiki_path": "Wiki/sources/current-article.md",
  "paused_at_step": 9,
  "created_at": "YYYY-MM-DDTHH:MM:SS",
  "remaining_queue": [
    "Raw/Thoughts/排队中的笔记1.md",
    "Raw/Records/排队中的日志2.md"
  ]
}
```

**`--continue` 恢复逻辑约束**：

1. 脚本读取状态文件，对当前挂起文件直接从步骤 9 恢复，完成步骤 9–12
2. **步骤 12 完成后**，删除 `.ingest-state.json`（此时当前文件已完整提交，删除安全）
3. 从 `remaining_queue` 出队下一个文件，检查其是否仍存在于磁盘：不存在则输出警告 `⚠️ 队列中文件已不存在，跳过: <路径>`，继续处理下一个；存在则对其执行**完整**的步骤 2–12 循环
4. 若 `remaining_queue` 已为空，优雅退出

> **队列全部失效时**：若 `remaining_queue` 中所有文件均不存在，输出警告 `⚠️ 恢复队列中的所有文件均已不存在，摄入完成`，以 exit 0 退出。

**步骤 8. 新建或增量合并词条**：在 `Wiki/` 对应子目录下创建或更新词条，严格执行 §二 加注规则及【Sources 文件的双产物规则】。

**【ingest LLM 不可用时的降级行为】**：LLM 不可用时，执行降级策略：
1. 将源文件关键段落（原文提取，不加工）写入词条草稿，标注 `（LLM 不可用，内容待补充）`
2. 填充 frontmatter 中可由路径/文件名确定的字段（title、type、sources、last_updated）
3. 输出警告 `⚠️ LLM 不可用，词条 <slug> 已生成占位草稿，请在 LLM 可用时重新运行 ingest <路径> 补全内容`
4. 继续执行步骤 9–12，确保占位草稿纳入版本控制
5. 在日志中以 `ingest | <标题>（draft-only）` 格式记录

**步骤 9. 更新索引与综述**：

- 更新 `Wiki/index.md`，在对应分类下添加或更新条目
- **ingest-fix 时**：更新已有条目的简述，不新增、不删除条目
- 若本次摄入触发了 overview 更新条件（见 §七 `domains_differ()` 说明），更新 `Wiki/overview.md`

**步骤 10. 摄入后验证**：检查新词条中所有 `[[双链]]` 是否指向已存在页面；若存在断链，输出警告并记录。

**步骤 11. 追加日志**：

```
## [YYYY-MM-DD] ingest | <标题> | [[Raw/<子目录>/<路径>/<文件名>]] | sha256:<前32位十六进制> | slug:<生成的文件名>
```

> **slug 字段填写规则**：一次摄入产生多个词条时，以首个新建词条的文件名为准，其余附加说明：`slug:<主slug> (+<次级词条1>, +<次级词条2>)`

**步骤 12. Git 提交**（**脚本必须在运行期间维护内存列表，记录本次摄入新建或修改的所有词条路径**，提交时精准追踪）：

```bash
# 伪代码：subprocess.run(["git", "add", "Wiki/log.md", "Wiki/index.md", "Wiki/overview.md", "Tools/"] + modified_files_list)
git commit -m "ingest: <标题>"
```

**步骤 13. 更新检索索引**（qmd 可用时执行，通过 `common.QMD_AVAILABLE` 判断）：

```bash
qmd embed --collection wiki
```

**步骤 14. 工作流结尾汇总**：输出本次摄入的新建词条列表与 ERROR 记录数量（若有）。

按 `.llm-wiki/config.json` 中的 `track_raw` 字段（见 §二【Raw/ 版本控制策略】）决定 Raw/ 跟踪行为。

---

**【ingest.py 最低规格】**（首次触发 ingest 时生成）：

- 入参：
  - `[file_path ...]`：指定文件路径（绝对或相对均可，入口处统一 `resolve()` 转为绝对路径）
  - `[--num <N>]`：仅处理队列前 N 个文件（**风格 B 模式下禁用**，若传入则输出错误并以 exit 1 退出）
  - `[--all]`：忽略批量上限，全量处理；风格 B 下兼容，逐个暂停机制不受影响
  - `[--validate-only]`：仅验证环境（Python 版本、markitdown 可用性、`.llm-wiki/raw-mapping.json` 可读性），打印验证结果后退出
  - `[--continue]`：**仅适用于风格 B `[DISCUSS]` 暂停后恢复**。若 `.ingest-state.json` 不存在，输出错误并以 exit 1 退出
  - `[--resume-step9 <slug>]`：**仅适用于 `[NEEDS_REVIEW_WRITTEN]` 裁决完成后恢复**。脚本接收 slug 参数，直接从步骤 9 执行，完成步骤 9–12 后正常退出；完成后 Agent 负责继续处理从 stderr 捕获的剩余队列
  - `[--discard]`：删除残留的 `.ingest-state.json` 并退出，不执行摄入
  - `[--fix <file_path>]`：配合 ingest-fix 路径使用，重新摄入并**覆盖**原词条（不走增量合并，直接替换）

- **退出码语义**（四值协议，见【exit 2 四种子情况的恢复路径】获取完整恢复路径说明）：
  - `exit 0` = 全部成功
  - `exit 1` = 硬错误（文件损坏、转换失败、非法参数等），ERROR 已记录至 log.md
  - `exit 2` = 需人工介入，含四种子情况（`[HASH_CHANGED]`、`[NEEDS_REVIEW]`、`[NEEDS_REVIEW_WRITTEN]`、`[DISCUSS]`）；`[NEEDS_REVIEW]` 和 `[NEEDS_REVIEW_WRITTEN]` 情况下，须在 stderr 打印 `REMAINING_QUEUE: path1|path2|...`

- **核心逻辑**：
  1. 入口路径规范化（`pathlib.Path(arg).resolve()` → POSIX 格式存储）
  2. 步骤 1：扫描 log.md 去重，建立路径→哈希映射表
  3. 步骤 2：计算 sha256 前 32 位
  4. 哈希变化检测 → 若变化，打印 `[HASH_CHANGED]` 并以 exit 2 退出（词条不写入，状态文件不写入）
  5. 步骤 7.5：Slug 冲突预检。**`is_update` 传参规则**：仅当当前执行流由 `ingest-update` 路径触发（即研究者在双轨询问协议中选择 B），且拟写入 slug 与步骤 4 第一个命中词条路径一致时，传 `is_update=True`；所有其他情况（新建词条、`--fix`、`--resume-step9`）均传 `is_update=False`
  6. 步骤 8：写入/合并词条（冲突时根据冲突发生时机选择 `[NEEDS_REVIEW]` 或 `[NEEDS_REVIEW_WRITTEN]`，均须在 stderr 打印 `REMAINING_QUEUE`, 脚本必须通过代码物理创建抽取出的 concepts/entities 独立文件，严禁只在 sources 文本中留下未实例化的悬空双链）
  7. 风格 B 暂停检查（写入 `.ingest-state.json` 含完整 `remaining_queue`，然后打印 `[DISCUSS]` 退出）
  8. 步骤 9–12：更新索引、验证、追加日志、git 提交

- **脚本严禁使用 `input()` 等阻塞式等待**

---

## 五、增量合并与冲突处理协议

### 5.1 增量合并

新笔记摄入时，先检索 `Wiki/` 是否已有对应词条：
- **无**：根据对应模板新建词条
- **有**：对比 Diff，将新物料细节无缝缝合进对应章节，严禁粗暴覆盖旧词条
- **注意**：若新词条仅是已有词条的参数化变体、局部实现或狭窄场景特例，优先合并进已有词条。

### 5.2 冲突处理协议（唯一权威判断来源）

**【冲突权威定义】**：以下任一情况视为冲突，禁止 Agent 自行裁判，强制挂起：
1. **命题直接否定**：新料与已有词条对同一命题给出相反断言（如"X 导致 Y" vs "X 不导致 Y"）
2. **数值/时序不一致**：数值、年份、因果方向明确不一致
3. **词义歧义冲突**：同一词汇在新料与已有词条中指向完全不同的对象
4. **核心定义结构性重构**：新料对词条的核心定义不是"增补细节"，而是"重构组成要素或要素关系"——判断标准：若按新料改写后，原有的定义将完全无法成立（而非仅被补充或细化）

> **注意**：第 1 条（命题直接否定）与第 4 条（结构性重构）存在交叉——遇到边界情况时，任一条件满足即触发冲突挂起。

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
5. Git 提交：精准追踪该词条路径，`git add <词条路径> Wiki/log.md && git commit -m "chore: resolve pending_review <词条名>"`

> `health.py` 检查项中包含 `pending_review: true` 词条扫描，运行 `health` 时会列出所有待裁决词条，提示研究者处理。

### 5.3 消歧触发规则

一旦发现同一词汇在不同传统或领域下存在实质性定义撕裂：
1. 将原词条升级为消歧导航页（套用 §3.4 模板）
2. 为每个独立含义创建独立词条（文件名：`概念（流派）.md`）
3. 若原始笔记未明确指明流派，输出警告，挂起等待人工确认，不强行分配
4. 追加日志（**三条记录**，分别对应三类写入操作）：
   ```
   ## [YYYY-MM-DD] disambiguation | <词条名> | 消歧导航页升级 | 来源: [[Raw/.../原始文件.md]]
   ## [YYYY-MM-DD] disambiguation | <词条名>（流派A）| 新建专用词条
   ## [YYYY-MM-DD] disambiguation | <词条名>（流派B）| 新建专用词条
   ```
5. health 的日志覆盖检查对 `disambiguations/` 目录的豁免，基于上述 `disambiguation |` 日志记录的存在（而非静默跳过）；lint 的"孤儿页"检查同样豁免通过消歧流程创建的专用词条（通过识别 `disambiguation |` 日志记录判断）

---

## 六、查询工作流（Query Workflow）

**触发**：`query: <问题>` 或自然语言提问

查询工作流不只是被动回答，而是知识库生长的主动驱动器。每次查询可能触发三个层次的生长机制。

**执行步骤**（内联推进，不创建追踪清单）：

**步骤 1. 开放问题预读**：检索前，先扫描 `Wiki/syntheses/` 中 `status: open` 的词条，作为"已知开放问题"的上下文背景，避免重复推导已知盲区。

**步骤 2. 语义主检索**：

优先使用 qmd（通过 `common.QMD_AVAILABLE` 判断）；否则调用 `common.search_wiki(keyword, collection="wiki")` 获取命中页面。读取命中词条，综合答案，使用 `[[词条名.md]]` 内联引用标注来源。

**【富格式输出契约】**：根据问题特质主动丰富输出形式：
- **结构化对比** → 提供 Markdown 对比表格
- **数值序列/趋势** → 附带 Python matplotlib 绘图代码或 ASCII 趋势图
- **汇报演示** → 使用 Marp Markdown 幻灯片格式输出

**步骤 3. 盲区回退**：若 Wiki 集合无命中，降级检索 Raw 集合：

```bash
# 优先路径
qmd query "<问题关键词>" --collection raw --format json -n 8

# 降级路径
grep -r "<问题关键词>" Raw/ --include="*.md" -l
```

- Raw 命中 → 基于原始笔记作答，末尾附注警告，同时触发生长层次二（见下）
- Raw 仍无命中 → 告知研究者该主题存在知识盲区，建议补充原始笔记

**步骤 4. 生长机制触发**：

**【生长层次一：综述归档】**：查询完成后，询问研究者是否归档本次答案：

> 📌 是否将本次答案归档为 `Wiki/syntheses/<slug>.md`？（Y/N，或指定路径）

slug 生成规则：将问题关键词翻译为 2–4 词英文语义词组（kebab-case）。具体实现：发起一次**独立的、轻量级的** `common.call_llm()` 调用，仅提供问题关键词，要求模型**仅输出** 2–4 个英文单词构成的 kebab-case 字符串，不含任何其他文本。生成后记录至 `log.md` 的 `slug:` 字段以确保跨会话一致性。

**归档前执行 slug 冲突检查**：调用 `common.check_slug_conflict(slug, 'Wiki/syntheses/', 'query-synthesis', is_update=False)`——若冲突，询问研究者是否指定新 slug 或确认覆盖，不自动覆盖。

无冲突时归档，更新 `Wiki/index.md` 的 `## Syntheses` 分类（新增条目：`[分析标题](syntheses/<slug>.md) — 回答的问题`），并执行：

```bash
git add Wiki/log.md Wiki/index.md <本次新建或被回哺的具体词条路径...>
git commit -m "query-synthesis: <问题关键词>"
```

若 qmd 可用：`qmd embed --collection wiki`

**【生长层次二：盲区驱动摄入】**：当 Raw 命中时，强制询问是否立即 ingest 以填补盲区。用户确认后，直接触发摄入工作流（§四）。

**【生长层次三：跨词条合成回哺】**：当答案综合了 **3 个及以上**不同 Wiki 词条时，自动提示归档选项（须用户显式确认后执行）；用户未确认或明确拒绝时，跳过回哺，继续对话，不挂起，不写入任何词条：
- 将跨词条洞见以 `（据查询合成，未经来源验证）` 加注，缝合进相关词条的 `🎯 核心论点` 章节，但不得加入 `📌 核心定义` 章节
- 在这些词条的 `related` 字段中补入新发现的关联词条双链
- 更新 `last_updated` 为当日日期
- 追加日志：`## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<slug>`
- Git 提交：精准追踪被回哺词条路径

**回哺硬性约束**：
- 回哺内容必须加注 `（据查询合成，未经来源验证）`，严禁伪装成一手事实
- 若回哺内容与词条既有内容存在矛盾，强制走冲突处理协议（§五 5.2），不得静默覆盖

---

**【query.py 最低规格】**（首次需要命令行查询时生成）：

- 入参：`"<问题>"` / `[--save]` / `[--save <path>]`
- 退出码：`0` = 成功，`2` = slug 冲突（打印 `[NEEDS_REVIEW] slug 冲突：<slug>.md 已存在` 后 exit 2）
- 核心逻辑：
  1. 调用 `common.search_wiki(keyword, collection="wiki")` 获取命中页面。若 `Graph/graph.json` 存在，对命中页面进行图谱邻居扩展，截断至总数不超过 8 个。
  2. **上下文瘦身**：剥离 YAML Frontmatter 和末尾无关双链引用区，仅保留 Markdown 核心正文。
  3. 发起**第一次** `common.call_llm()` 调用，生成 Markdown 格式的完整答案正文（含 `[[wikilink.md]]` 引用）。
  4. **slug 生成**：发起**第二次独立的、轻量级的** `common.call_llm()` 调用，仅提供问题关键词，严格要求模型**仅输出** 2–4 个英文单词构成的 kebab-case 字符串，禁止任何其他文本。
  5. `--save` 或 `--save <path>`：写入前调用 `common.check_slug_conflict(slug, 'Wiki/syntheses/', 'query-synthesis', is_update=False)`——若 slug 已存在，打印 `[NEEDS_REVIEW]` 并以 exit 2 退出；无冲突则写入，**同步更新 `Wiki/index.md` 的 `## Syntheses` 分类**（新增条目：`[标题](syntheses/<slug>.md) — 回答的问题`），追加日志（含 `slug:<slug>` 字段）
- **LLM 不可用时**：返回占位答案（包含命中的相关词条路径列表）并提示用户，不抛出未捕获异常

---

## 七、健康检查与质量审计工作流

### 健康检查（Health Workflow）

**触发**：`health` | **频率**：每次会话启动规程中必跑 | **成本**：零 LLM 调用

直接运行（内联步骤推进，不创建追踪清单）：`python Tools/health.py [--json] [--save]`

**检查项**：

- **空文件 / 存根页**：仅有 frontmatter、无正文内容的页面
- **索引同步**：`Wiki/index.md` 条目与磁盘实际文件是否一致
- **日志覆盖**：有词条页面但 `Wiki/log.md` 中缺少对应记录的情况。
  - **豁免文件**：`overview.md`、`index.md`、`log.md` 本身
  - **消歧词条豁免**：`disambiguations/` 目录下通过消歧流程生成的词条，以存在对应的 `disambiguation |` 日志记录为豁免依据（不静默跳过，而是验证日志存在）
  - **Rename 追踪链兼容**：若词条文件名无直接对应的 `ingest` slug，但存在指向该文件名的 `chore | rename` 记录，视为合法，不报警
  - **ingest-fix 兼容**：原始 `ingest` 记录加上 `chore | ingest-fix` 记录合计视为一份合法覆盖记录，不触发"日志覆盖缺失"警告
- **断链检查**：`[[双链]]` 指向不存在页面的情况
- **Assets 断链检查**：Wiki 词条中引用的图片路径在磁盘上不存在的情况
- **Raw 目录合规**：`Raw/` 下是否存在预设子目录以外的其他子目录或文件（调用 `common.load_allowed_raw_dirs()` 读取允许列表）。**豁免规则**：名称以 `.` 开头的文件/目录及 `Thumbs.db` 视为系统临时文件，跳过不报警。
- **哈希一致性检查**：**仅扫描操作类型为 `ingest` 且含 `sha256:` 字段的记录**，对每条记录执行以下分支判断：
  - 对应路径的文件**不存在**于磁盘，且无对应的 `chore | move` 或 `chore | delete` 记录 → 输出 `⚠️ [路径不存在] <路径>：文件可能已被移动或删除，如已移动请执行 chore: move 更新路径记录，如已删除请执行 chore: delete Raw/<路径> 清理日志悬空记录`
  - 对应路径的文件不存在，但**存在** `chore | move` 或 `chore | delete` 记录 → 视为合法已处理，不输出警告
  - 文件存在但**哈希不匹配** → 输出 `⚠️ [内容已修改] <路径>：当前哈希与摄入时记录不一致，请确认是否需要重新摄入（说 ingest <路径> 触发双轨询问）`
  - 两项均正常 → 通过，不输出
- **pending_review 扫描**：列出所有 `pending_review: true` 的词条，提示研究者裁决

`--save` 参数将报告写入 `Wiki/health-report.md`。若需纳入版本控制，研究者手动 `git add -f Wiki/health-report.md && git commit`。

---

### 质量审计工作流（Lint Workflow）

**触发**：`lint` | **频率**：每 10 次摄入后建议运行（会话启动规程自动计数提示，阈值可配置） | **前提**：必须在 health 通过后运行

> **"health 通过"最低门槛**：无断链、无空文件/存根页即可放行 lint。`pending_review` 待裁决词条、哈希不匹配警告、Assets 断链警告不阻塞 lint 运行；但若 health 报告存在断链，必须先修复再运行 lint。

直接运行（内联步骤推进，不创建追踪清单）：`python Tools/lint.py [--save]`

**检查项**：
- **孤儿页**：无任何入站 `[[链接]]` 的 Wiki 页面（**豁免**：通过消歧流程创建的专用词条，通过识别 `disambiguation |` 日志记录判断）
- **内容矛盾**：跨页面存在相互冲突的断言
- **过时综述**：有更新源笔记摄入后，相关词条未同步更新。判断标准：扫描 `log.md`，若某个 `sources/` 词条对应的原始 Raw 文件在 `Wiki/sources/<slug>.md` 的 `last_updated` 之后出现了新的 `ingest | ... | sha256:<不同哈希>` 记录（即原始文件已被修改并重新摄入），则视为"源笔记已更新"；若对应的 `sources/` 词条的 `last_updated` 日期早于该次重新摄入日期，则标记为过时综述。
- **缺失实体页**：在 3 个及以上页面中以 `[[wikilink]]` 形式被提及但没有独立词条的实体（**仅统计 `[[双链]]` 形式的提及，不执行命名实体识别**）
- **稀疏页**：出站 `[[双链]]` 少于 2 条的页面
- **加注缺失**：词条正文中来自 `Sources/` 的内容未加 `（据文献）`，来自 `Thoughts/` 的内容未加 `（个人思考）`，来自 `Records/` 的内容未加 `（个人经验）`
- **slug 冲突检测**：扫描 `log.md` 中所有 `slug:` 记录，检查是否存在相同 slug 对应不同来源文件的情况
- **语义近似词条检测**（LLM 辅助，可选）：识别标题或核心定义高度相似、可能需要合并或消歧的词条对，包括**跨语言同义对**；输出建议列表供研究者判断——不自动合并，仅建议
- **知识盲区与主动推荐**：识别 Wiki 无法回答的常见问题类型，列出具体的知识缺口描述，**并对每个盲区建议 1–3 条 web 搜索查询词**

> **断链检查归属 health**：`lint.py` 不重复执行断链检查，该项由 `health.py` 负责。

图谱感知检查（**可选**，需先运行 `build graph`，仅当 `Graph/graph.json` 存在时执行）：
- **枢纽存根（Hub Stubs）**：度数 > μ+2σ 但内容少于 500 字的节点
- **脆桥（Fragile Bridges）**：两个社区之间仅由 1 条边连接的情况
- **孤立社区**：与其他社区零外部连接的知识孤岛
- **冲突边密度**：`relation: contradicts` 的边占总边数的比例

输出审计报告，询问用户是否保存至 `Wiki/lint-report.md`。保存后 Git 提交。运行结束后自动追加日志记录。

**【Schema 演化提示】**：运行结束后，若审计发现了**反复出现的模式偏差**，在报告末尾附加提示：
> 💡 Schema 演化建议：检测到以下反复出现的偏差，建议讨论是否修订 AGENTS.md……

---

**【common.py 最低规格】**（任何工具工作流首次触发时优先生成）：

- **路径常量**：`REPO_ROOT`（基于 `pathlib.Path(__file__).resolve().parent.parent` 推算）、`WIKI_DIR`、`RAW_DIR`、`GRAPH_DIR`、`LOG_FILE`、`INDEX_FILE`、`OVERVIEW_FILE`
- **环境加载**：模块导入时立即调用 `load_dotenv(REPO_ROOT / ".env", override=False)`，并加异常兜底（`ImportError` 时静默跳过，不阻断模块导入）
- **终端 I/O 免疫机制**：模块导入时必须立即执行系统标准输出流的 UTF-8 重配置，以彻底防止 Windows 终端在打印含有 Emoji（如 📌、⚠️、🏷️）的日志时抛出 GBK 编码崩溃。强制要求包含以下代码：

  ```python
  import sys
  if sys.stdout.encoding.lower() != 'utf-8':
      sys.stdout.reconfigure(encoding='utf-8')
  if sys.stderr.encoding.lower() != 'utf-8':
      sys.stderr.reconfigure(encoding='utf-8')
  ```

- **解释器常量**：`PYTHON_BIN` — 使用 `shutil.which` 实现跨平台虚拟环境探测：

  ```python
  import sys, shutil
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
          if shutil.which(c) is not None:
              return c
      return "python"

  PYTHON_BIN = _detect_python()
  ```

- **qmd 可用性缓存**：`QMD_AVAILABLE` — 模块级常量，模块导入时执行一次检测：

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

- **markitdown 可用性缓存**：`MARKITDOWN_AVAILABLE` — 同样在模块导入时执行一次检测，检测方式与 `QMD_AVAILABLE` 一致。
- **I/O 工具**：`read_file(path)` / `write_file(path, content)`（原子写入：先写同目录临时文件，`os.replace()` 重命名，自动创建父目录，强制 `encoding='utf-8'`）/ `ensure_utf8()`。所有返回给 Markdown 文本的路径及写入 `log.md` 的路径变量，在格式化输出前必须调用 `pathlib.Path(path).as_posix()`。
- **检索适配工具**：`search_wiki(keyword, collection="wiki", max_results=8)` → 提供统一的知识库检索入口，内部首选调用 `qmd query`，不可用则自动降级为 `grep -r -l` 全文检索或解析 `index.md`。无论底层走哪条降级路径，该函数统一返回 `List[pathlib.Path]`（格式化的磁盘绝对路径列表），严禁向外抛出未清洗的原始文本。
- **配置工具**：`load_config()` → 读取 `.llm-wiki/config.json`，返回配置字典；文件不存在时返回默认值 `{"version": 1, "ingest_style": "A", "track_raw": false}`
- **内容工具**：`extract_wikilinks(text)` / `all_wiki_pages()` / `append_log(entry)` / `resolve_wikilink(name)` / `load_allowed_raw_dirs()` — 读取 `.llm-wiki/raw-mapping.json`，返回所有目录条目列表；`ingest: true` 的目录可摄入，`ingest: false` 的目录不摄入但视为合法目录
- **哈希工具**：`sha256_short(file_path)` → 以 `rb` 模式读取文件，返回 sha256 前 32 位十六进制字符串；`sha256_full(file_path)` → 返回完整 64 位。**log.md 始终存储 `sha256_short`，去重与一致性检查统一使用此短哈希。**
- **LLM 调用**：`call_llm(prompt, model=None, timeout=None, exit_on_error=True)` — 读取 `LLM_BACKEND` 决定后端；`model` 参数优先级：① 函数入参（非 None）→ ② 环境变量 `LLM_MODEL`（默认模型）→ ③ 后端自身的默认模型。`timeout` 参数优先读取函数入参，若为 None 则读取环境变量 `LLM_TIMEOUT`（默认 300 秒）。`exit_on_error=False` 时超时或报错均返回占位符字符串而非抛异常。
- **Slug 冲突工具**：`check_slug_conflict(slug, target_dir, operation_type, is_update=False)` → 若 `is_update=True` 且目标路径文件存在但属于增量合并对象，返回 `(False, None)`；否则正常扫描 `target_dir` 磁盘文件及 `log.md` 记录，返回 `(conflict: bool, existing_source: str | None)`。**四参数签名为唯一权威签名**，所有调用方均使用此签名。
- **domain 比较工具**：`domains_differ(a, b)` → 比较两个 `domain` 字段值：若 `a == b` 且两者均**非** `__unset` 且均**非**空值，返回 `False`（同一领域）；其余所有情况（包括两者均为 `__unset`、均为空、或任一为 `__unset`）返回 `True`（视为不同领域）。运行时读取 `AGENTS.md` 末尾的 `# overview-update-threshold: N` 注释（若存在）作为 overview 更新的最小不同领域词条数阈值（默认 2）。
- **pending_review 工具**：`list_pending_review()` → 遍历 `all_wiki_pages()` 返回的所有词条，通过解析每个文件的 YAML frontmatter（使用 `yaml.safe_load` 解析 `---` 块）读取 `pending_review` 字段，收集值为 `true` 的词条路径，返回 `List[pathlib.Path]`，供 `health.py` 调用

---

**【health.py 最低规格】**（首次触发 health 时生成）：

- 入参：`[--json] [--save]`
- 退出码：`0` = 全部通过，`1` = 发现问题
- 检查项（见本节【健康检查（Health Workflow）】完整列表）：空文件/存根页、索引同步、**日志覆盖**（兼容豁免文件列表、消歧词条的 `disambiguation |` 日志验证、rename 追踪链、ingest-fix 双记录）、断链、Assets 断链、**Raw 目录合规**（调用 `common.load_allowed_raw_dirs()`）、**哈希一致性**（使用 `common.sha256_short`，仅扫描 `ingest` 操作类型且含 `sha256:` 字段的记录）、**pending_review 扫描**（调用 `common.list_pending_review()`）
- **全部通过时**：输出 `✅ Health check passed — N 项检查全部通过`
- `--save` 将报告写入 `Wiki/health-report.md`（`.gitignore` 屏蔽，需手动 `git add -f` 入库）

---

**【lint.py 最低规格】**（首次触发 lint 时生成）：

- 入参：`[--save]`
- 退出码：`0` = 无严重问题，`1` = 发现严重问题
- 前提：必须在 health 通过后运行（最低门槛：无断链、无空文件/存根页）
- 检查项：见本节【质量审计工作流（Lint Workflow）】完整列表（不执行断链检查，该项归属 `health.py`）。"过时综述"检查依据见【检查项】中的判断标准定义（基于 `log.md` 哈希记录比对，不依赖文件系统 mtime）。**"孤儿页"检查豁免**通过消歧流程创建的专用词条（识别 `disambiguation |` 日志记录）。
- **语义分析的批处理策略**：在执行"内容矛盾"、"缺失实体页"和"语义近似检测"等需要大模型参与的语义比对时，**严禁向大模型一次性全量喂入所有 Wiki 文件**。脚本必须采用局部滑动窗口策略：每次仅抽取最近更新的 3–5 个词条，并仅拉取它们在图谱中的直接一跳邻居（或 `index.md` 中的同类相邻词条）构建局部上下文交给 LLM 审计。
- 图谱感知检查（可选，仅当 `Graph/graph.json` 存在时执行）
- LLM 不可用时：将分析上下文 dump 至 `Wiki/_semantic_lint_context.md`，由 Agent 手动完成语义分析
- 运行后追加日志（复用 `common.append_log()`）
- 报告末尾包含 Schema 演化建议段落

---

## 八、知识图谱工作流（Graph Workflow）【可选扩展】

> **适用时机**：知识库积累到一定规模（建议 50+ 词条）后再考虑启用。初期无需使用。

**触发**：`build graph`

直接运行（内联步骤推进）：`python Tools/build_graph.py [--open] [--report] [--save] [--no-infer]`

**LLM 调用说明**：
- **Pass 1（默认）**：扫描所有 Wiki 页面，提取显式 `[[双链]]` 构建基础图谱，**零 LLM 调用**
- **Pass 2（可选）**：语义推断隐性关联边，**消耗 token**。需设置环境变量 `LLM_MODEL_FAST` 启用；未设置时自动跳过。**Pass 2 必须通过 `common.call_llm(prompt, model=os.environ.get("LLM_MODEL_FAST"))` 实现**，禁止在 `build_graph.py` 内自行实现 LLM 调用逻辑。`model` 参数非 None，将按 `call_llm` 的优先级规则使用该指定模型（见 §七 common.py LLM 调用规格）。

**【Pass 2 增量缓存机制】**：Pass 2 的语义推断结果持久化至 `Graph/.cache.json`（由 `.gitignore` 屏蔽，不入库），避免每次运行时对已处理节点重复推断：
- 缓存键：节点文件路径 + 文件内容的 `sha256_short`
- 命中缓存（路径存在且哈希一致）：直接复用已推断的边，跳过 LLM 调用
- 未命中（新词条或内容已修改）：调用 `common.call_llm()` 推断，结果写入缓存
- `--no-infer` 参数：跳过 Pass 2，同时不读写缓存

**输出**（直接写入 `Graph/` 根目录，**无子目录**）：
- `Graph/graph.json`：节点与边的结构化数据
- `Graph/graph.html`：基于 vis.js 的自包含可视化页面（`contradicts` 边红色高亮）
- `Graph/graph-report.md`：图谱健康报告（`--report --save` 时生成，通过 `git add Graph/` 自动入库，**与 health/lint 报告的入库策略不同**：图谱报告在构建时即视为交付物，不需要手动 `git add -f`）

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

**硬性规则**：图谱层禁止从断链自动创建页面，只报告；隐性关联（`INFERRED`）仅存入 `graph.json`，不自动写入页面正文。

---

**【build_graph.py 最低规格】**（首次触发 build graph 时生成）：

- 入参：`[--open] [--report] [--save] [--no-infer]`
- 退出码：`0` = 成功，`1` = 硬错误
- Pass 1（默认）：提取显式 `[[双链]]` 及 `related:` 字段的语义边类型注释，零 LLM 调用
- Pass 2（可选）：设置环境变量 `LLM_MODEL_FAST` 启用；**必须通过 `common.call_llm(prompt, model=os.environ.get("LLM_MODEL_FAST"))` 调用**；每处理 10 个节点向终端输出一条进度；**启用增量缓存**（`--no-infer` 时跳过 Pass 2 且不读写缓存）
- **`graph.html` 离线可用性**：`graph.html` 内部**必须**以内联 JavaScript 变量（如 `const graphData = <JSON文本>;`）形式将图谱数据硬编码写入 HTML，**严禁**在前端 JS 中使用 `fetch()` 或 `XMLHttpRequest` 动态请求 `graph.json`（确保在 `file://` 协议下直接双击可打开）。vis.js 库代码必须内联写入 HTML 文件中，不依赖外部 CDN，保证离线可用。脚本内部预置完整的 vis.js 内联 HTML 模板字符串，仅在运行时用 f-string 将 `graph.json` 数据注入模板。
- `--report --save` 将图谱健康报告保存至 `Graph/graph-report.md`（入库策略见上方【输出】说明）
- 运行后追加日志（复用 `common.append_log()`）

---

## 九、命名规范与日志格式

> 命名规范的唯一权威来源见 §三【命名规范】表格，本节仅补充日志格式。

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

> **日期时区说明**：所有日志日期统一使用 Agent 运行环境的系统本地日期（`date +%Y-%m-%d`），不强制 UTC。

- **正常摄入记录**：`## [YYYY-MM-DD] ingest | <标题> | [[Raw/<子目录>/<路径>/<文件名>]] | sha256:<前32位十六进制> | slug:<slug>`
- **草稿摄入记录**（LLM 不可用时）：`## [YYYY-MM-DD] ingest | <标题>（draft-only） | [[Raw/...]] | sha256:<前32位十六进制> | slug:<slug>`
- **ingest-fix 记录**：`## [YYYY-MM-DD] chore | ingest-fix: <标题>`（紧跟在原始 `ingest` 记录之后，原始记录保留）
- **query-synthesis 记录**：`## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<slug>`
- **消歧记录**：`## [YYYY-MM-DD] disambiguation | <词条名> | <操作说明> | 来源: [[Raw/.../原始文件.md]]`（三条格式见 §五 5.3）
- **其他正常记录**：`## [YYYY-MM-DD] <操作> | <标题>`
- **失败记录**：`## [YYYY-MM-DD] ERROR | <操作> | <原因>`

操作类型：`bootstrap` / `ingest` / `query` / `query-synthesis` / `health` / `lint` / `graph` / `chore` / `disambiguation` / `ERROR`

> **Log 优先原则**：正常摄入时，步骤 11（追加日志）必须在步骤 8（写入词条）完成后**立即**执行，不得推迟到步骤 12（git 提交）之后。所有词条文件写入使用 `common.write_file()`（原子写入），确保单文件写入的完整性。

> **失败可追溯原则**：Agent 遇到不可恢复失败时，必须立即写入 ERROR 记录到 `Wiki/log.md`，继续执行后续独立步骤，不因单点失败阻塞整个工作流，在工作流结尾输出 ERROR 汇总。

---

## 十、临时文件处理规范

**硬性原则**：所有临时生成、与知识库无直接关系的辅助文件，直接删除，绝不进入 Git 跟踪。

| 类型 | 典型示例 | 默认行为 |
|------|----------|----------|
| Lint 上下文 dump | `Wiki/_semantic_lint_context.md` | 删除 |
| 摄入状态文件 | `.ingest-state.json` | 脚本执行完毕后自动删除；`.gitignore` 屏蔽 |
| 图谱缓存 | `Graph/.cache.json` | `.gitignore` 屏蔽 |
| 工具中间输出 | `Tools/__pycache__/`、`*.pyc` | `.gitignore` 屏蔽 |
| 检索索引目录 | `.qmd/` | `.gitignore` 屏蔽 |
| Obsidian 配置 | `.obsidian/`、`workspace.json` | `.gitignore` 屏蔽 |
| 工具运行报告（health/lint） | `Wiki/health-report.md`、`Wiki/lint-report.md` | `.gitignore` 屏蔽（用户确认保存后手动 `git add -f`） |
| 图谱报告 | `Graph/graph-report.md` | **不屏蔽**，通过 `git add Graph/` 自动入库（见 §八） |

**执行纪律**：Agent 在执行 `git add` 前，必须先清理工作目录中的临时文件。

---

## 十一、反幻觉机制总览

本系统共设 **16 道**防幻觉机制，按功能分组：

**来源隔离与加注（防止事实污染）**
1. 目录决定加注类型（通过 `raw-mapping.json` 持久化） → 消除 Agent 对归属的主观猜测
2. 禁止自我引用（§二） → 防止 AI 把自己的总结当事实循环论证
3. 禁止推断型事实填补（§二） → 缺失即缺失，不以"合理推断"代替实际来源
4. 查询合成强制加注（§六） → 跨词条推论永远标注"未经来源验证"
5. Lint 加注缺失检查（§七质量审计） → 定期审计加注执行情况

**冲突识别与人工裁决（防止矛盾掩盖）**
6. 冲突处理协议（§五 5.2，唯一权威定义） → 矛盾不掩盖，挂起等待人工裁决，裁决后有明确闭环
7. ingest-fix vs ingest-update 双轨协议（§四） → 文件内容变化时前置询问，防止意外覆盖已有词条

**结构完整性（防止静默数据脱节）**
8. 哈希一致性检查（§七健康检查） → 区分"路径移动"与"文件修改"两类警告
9. Log 优先原则（§九） → 词条写入后立即记录日志，health 可检测半更新状态
10. `raw-mapping.json` 持久化目录映射 → 避免运行时解析 Markdown 表格产生歧义
11. ingest-fix 双记录兼容（§七 health.py） → 原始 `ingest` + `chore | ingest-fix` 合计视为合法覆盖，不误报

**路径与状态管理（防止恢复路径崩溃）**
12. `[NEEDS_REVIEW_WRITTEN]` 与 `[NEEDS_REVIEW]` 对称的 `REMAINING_QUEUE` 输出（§四） → 两种 exit 2 子情况均在 stderr 打印剩余队列，确保批量摄入不因裁决中断而丢失
13. 批量队列 exit 2 的 `REMAINING_QUEUE` 输出（§四） → 确保两种冲突子情况下剩余队列不丢失
14. `--continue` 删除时机明确（步骤 12 完成后才删除状态文件） → 防止中途崩溃导致队列信息丢失
15. `check_slug_conflict` 豁免条件明确（仅 `ingest-update` 路径传 `is_update=True`，比对首个命中词条） → 防止多命中时豁免判断歧义，防止其他路径误触发豁免

**系统健壮性**
16. `domains_differ()` 统一处理 `__unset`（§七 common.py）+ 可配置 overview 更新阈值（AGENTS.md 末尾注释 + README 说明）+ lint 触发阈值可配置（会话启动规程 + AGENTS.md 末尾注释）→ 确保未分类词条不静默跳过综述，同时提供双重阈值调整机制减少早期噪声提交

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

bootstrap 完成后，先安装依赖（`pip install -r Tools/requirements.txt`），然后 Agent 会打印完整目录树与下一步操作提示（见 §1.12）。

---

## 4. 设计哲学

这套系统的本质是**隔离与编译**，加上**最小摩擦**。

人与 Agent 的分工是这个系统能长期运转的根本：人掌管 Raw 层（策源、策略、目录结构），Agent 掌管 Wiki 层（整理、交叉引用、维护一致性）。这个边界不可模糊——Agent 不干涉 Raw 层的任何决策；人不需要亲自做 Wiki 层的维护工作。

**默认自动执行，例外才挂起**：知识库只有在维护成本足够低时才能长期运转。查询归档、冲突裁决是例外：写入 Wiki 的重要决策由研究者确认，不由 Agent 代劳。

**脚本按需生成**：工具脚本在首次需要时生成，而非预先批量产出。这确保每个脚本生成时上下文充分、token 预算充足，且只生成真正用到的脚本，避免维护从未运行过的代码。

**Schema 共同演化**：AGENTS.md 不是一份一劳永逸的宪法，而是随使用习惯不断精化的活文档。研究者与 Agent 在协作中发现规则偏差时，应主动讨论并修订，让规则与实际使用场景保持一致。
