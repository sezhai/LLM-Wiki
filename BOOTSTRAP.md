# LLM Wiki 仓库创建提示词

**本文件用途**：将本文件复制到任意空白目录，交给一个具备文件系统与 Shell 工具的 AI Agent（如 Claude Code、Cursor、OpenCode 等）。  

Agent 阅读本文件后，将在该目录中完整创建一个符合 LLM Wiki 规范的知识操作系统骨架，所有工具脚本在 bootstrap 阶段一次性写入。  

**当前版本**：v1.0（已整合 2026-06-19 修复 + 跨平台优化）

**核心理念**：Raw 层（研究者完全掌管的只读事实池）/ Wiki 层（Agent 完全拥有的结构化知识编译层）/ Graph 层（结构健康层，可选扩展）。

---

## 你（Agent）的任务总览

你即将在当前工作目录（即本文件所在目录，以下简称 `.`）中产出一个可直接使用的 LLM Wiki 仓库骨架。执行前无需设置任何变量，所有命令直接在当前目录运行（`.`）。完成时，目录结构必须严格如下：

```
./
├── AGENTS.md              # 最高操作契约（按本文档 §2 写入）
├── README.md              # 仓库使用说明（研究者视角，仅此一份）
├── .gitignore             # 排除索引、缓存与编辑器配置
├── .llm-wiki/             # 机器可读配置（纳入 git 跟踪；ingest-queue.json 不入库）
│   ├── raw-mapping.json   # Raw 子目录→加注类型映射（单一事实源）
│   └── domain-enum.json   # 合法 domain 枚举
├── Raw/                   # 只读事实池（Agent 严禁除读取之外的任何操作）
│   ├── Sources/           # 他人文档：论文、剪藏、技术规范、书籍
│   ├── Thoughts/          # 自己写的研究笔记、思辨、逻辑推演
│   ├── Records/           # 个人记录：交易日志、聊天记录、复盘日记
│   └── Assets/            # 图片 / PDF 附件（Obsidian 附件库路径）
├── Wiki/                  # 知识编译层（Agent 完全拥有并动态维护）
│   ├── index.md           # 词条目录
│   ├── log.md             # 操作日志（只增不改）
│   ├── overview.md        # 跨领域活体综述
│   ├── concepts/          # 概念词条（绝对平铺，禁止子文件夹）
│   ├── entities/          # 实体词条（人物 / 机构 / 著作 / 事件）
│   ├── sources/           # 长文 / 原著的 AI 摘要映射（自动生成）
│   ├── syntheses/         # 综述归档（查询答案沉淀，自动生成）
│   └── disambiguations/   # 消歧义专页
├── Graph/                 # 【可选扩展】结构健康层（工具生成，勿手动修改）
└── Tools/                 # 工具脚本（bootstrap 时全部写入）
    ├── __init__.py        # 空文件，使 Tools/ 成为 Python 包
    ├── common.py          # 共享依赖库
    ├── health.py          # 健康检查脚本
    ├── ingest.py          # 摄入脚本
    ├── lint.py            # 质量审计脚本
    ├── query.py           # 查询脚本
    ├── build_graph.py     # 图谱生成脚本（可选扩展）
    └── requirements.txt   # Python 依赖
```

Python 版本要求：Python 3.9+（所有工具脚本均基于此版本；match 语句等 3.10+ 特性不使用）。  

重要：除仓库根目录的 README.md 外，任何子目录下均不放置额外的 README 文件，保持目录结构极致精简。

---

## 执行工作流（严格按序）

### 1.0 创建步骤追踪清单

通过 Agent 可用的任务追踪机制（todowrite / TodoWrite / 内联 Markdown 清单，视环境自动选择）创建一份 13 步（§1.0–§1.13）的清单，仅用于追踪 bootstrap 自身进度，内容不重复各步骤细节。步骤 0 立刻标记完成，其余初始为待处理；每完成一步立即更新状态。最终输出前确认全部完成。

注意：本清单仅供 bootstrap 使用，与运行时 ingest 工作流中为每批次文件创建的追踪清单是两套独立机制。

### 1.1 向用户询问关键配置

在写入任何文件之前，通过一次对话确认以下三项。若用户拒绝回答或说“用默认”，使用括号内的默认值。

| 配置项 | 默认值 | 自定义说明 |
|--------|--------|-----------|
| **Raw 层目录** | 四类默认目录（Sources / Thoughts / Records / Assets） | 若自定义，请列出目录名、各自的加注类型以及是否参与摄入；若未说明“是否摄入”则默认为 `true`。自定义后将完全不使用默认目录。 |
| **Git 远程** | 暂不配置 | 若配置 origin，请提供远程 URL。 |
| **知识领域（domain）枚举** | 哲学、历史、宗教、文学、自然科学、技术、经济、其他 | 使用顿号分隔的列表，如需增删请说明。Agent 将据此生成 `.llm-wiki/domain-enum.json`，并将枚举列表写入 AGENTS.md §3.1 的说明中，同时将枚举中的第一项写入 frontmatter 示例的 domain 字段注释里。 |

### 1.2 验证目标目录

目标目录为当前工作目录（`.`）——即本 bootstrap 文件所在的目录，所有后续步骤直接在 `.` 下操作。

```bash
Get-ChildItem -LiteralPath "."
```

- 目录为空（仅含本 bootstrap 文件）→ 直接继续
- 目录非空（含其他文件）→ 警告用户，要求显式确认是否在此目录继续

### 1.3 创建物理目录结构

用 `mkdir -p` 一次性创建所有目录。关键约束：
- `Wiki/` 下必须创建五个平铺子目录（禁止再建子文件夹）：`concepts/`、`entities/`、`sources/`、`syntheses/`、`disambiguations/`
- `Raw/` 仅预建 §1.1 确认的子目录；加注映射以 Raw 根下第一级子目录为准
- `.llm-wiki/` 在此创建，JSON 配置文件在 §1.4 写入
- `Graph/` 仅预建根目录，其余文件由工具运行时生成
- 创建 `New-Item -ItemType File -Path Tools/__init__.py`
- 任何子目录下均不创建 README.md

### 1.4 写入 AGENTS.md 及机器可读配置

使用本文档 **§2** 的完整模板，按以下规则替换所有占位符：

| 占位符 | 替换为 |
|--------|--------|
| `<YYYY-MM-DD>` | 今日日期（ISO 8601） |
| `<DOMAIN_ENUM>` | 用户在 §1.1 确认的 domain 枚举列表，顿号分隔（如 `哲学、历史、宗教、文学、自然科学、技术、经济、其他`） |
| `<DOMAIN_FIRST>` | 枚举列表中的第一项（用于 frontmatter 示例） |

**关于 Raw 子目录加注规则**：AGENTS.md §二 的加注规则段落不内嵌目录表格，而是写为：

> “Raw 层各子目录的名称、加注类型、是否参与摄入，以 `.llm-wiki/raw-mapping.json` 为单一权威来源。Agent 每次加注前读取该文件，依据文件所在 Raw 根下第一级子目录名查找对应条目。”

**写入 `.llm-wiki/raw-mapping.json`**（AGENTS.md 写入完成后立即执行）。规则的详细描述统一指向 AGENTS.md §二，此处仅给出 JSON 结构示例：

默认版本（用户未自定义时）：

```json
{
  "version": 1,
  "dirs": [
    {"name": "Sources", "annotation": "据文献", "ingest": true, "description": "他人文档：论文、网页剪藏、技术规范、书籍"},
    {"name": "Thoughts", "annotation": "个人思考", "ingest": true, "description": "自己写的研究笔记、思辨、逻辑推演"},
    {"name": "Records", "annotation": "个人经验", "ingest": true, "description": "个人记录：交易日志、聊天记录、复盘日记"},
    {"name": "Assets", "annotation": null, "ingest": false, "description": "图片、PDF 附件，不独立摄入"}
  ]
}
```

若用户自定义了目录，按用户提供的目录名、加注文字、是否摄入生成对应 JSON，不保留任何默认目录项。若用户未提供某个目录的 `ingest` 字段，默认设为 `true`。

**写入 `.llm-wiki/domain-enum.json`**（同样立即执行）：

```json
{
  "version": 1,
  "domains": ["哲学","历史","宗教","文学","自然科学","技术","经济","其他"]
}
```

若用户增删了枚举值，以最终确认的列表为准，保留 JSON 数组格式。

### 1.5 写入 README.md

内容要点（用第二人称，5 分钟内可读懂）：

- 一句话定位：这是个人 LLM 知识库，`Raw/` 放原始材料，`Wiki/` 是结构化沉淀
- 详细结构及加注规则见 `.llm-wiki/raw-mapping.json`；`sources/` 和 `syntheses/` 由 Agent 自动维护，研究者无需手动管理
- 快速上手三步：放文件进 `Raw/` → AI 会话说 `ingest <路径>` → 说 `query: <问题>`
- 完整操作规程见 **AGENTS.md**；qmd 初始化及 Obsidian 配置提示见 health 报告
- Graph 层为可选扩展，前 50 次摄入无需使用

### 1.6 写入 .gitignore

```
# 检索索引（本地自动生成）
.qmd/
.rag/
.vsearch/
# qmd 查询临时命中文件
.qmd-hits.json
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
Graph/.infer-context.json
Graph/.infer-results.json
# 临时诊断文件
Wiki/_semantic_lint_context.md
Wiki/_annotation_check_result.md
Wiki/_blind_spot_result.md
*.tmp
# 工具运行时生成的报告（需用户显式确认保存后才写入）
Wiki/health-report.md
Wiki/lint-report.md
# 查询 pending 临时文件
.qmd-pending-query.json
# 摄入批次清单（运行时临时状态，不入库）
.llm-wiki/ingest-queue.json
# OS 文件
.DS_Store
Thumbs.db
```

### 1.7 写入 Tools/requirements.txt 并安装依赖

`Tools/requirements.txt`：

```
markitdown>=0.1.0
pyyaml>=6.0
networkx>=3.0
```

版本下界保证 CLI 位置参数（`markitdown <file>`）可用；不设上界，由用户的 lock 文件（pip freeze / poetry.lock）负责版本锁定。若升级后 CLI 接口变动导致转换失败，ingest.py 会输出 WARN 并跳过，不阻断 bootstrap。

安装依赖：

```bash
pip install -r Tools/requirements.txt
```

若安装失败，将错误信息输出给用户，**标记此步骤为阻塞状态**，并停止 bootstrap 流程。告知用户手动解决 pip 依赖问题后，重新执行本步骤及后续步骤即可继续（清单机制会记住未完成项）。

### 1.8 写入 Wiki 初始核心文件

**Wiki/index.md**：

```markdown
# Wiki Index
## Overview
[[Overview]] — 跨领域活体综述
<!-- 以下五个标题为机器可读锚点，请勿修改文字 -->
## Concepts
## Entities
## Sources
## Syntheses
## Disambiguations
```

**Wiki/overview.md**（写入时将 `<YYYY-MM-DD>` 替换为当日日期；触发条件写在 AGENTS.md §四，此处只放结构模板）：

```markdown
---
last_updated: <YYYY-MM-DD>
---
# 跨领域活体综述
## 当前研究焦点
<!-- 用 2–4 句话描述知识库目前积累最多的主题领域。首次摄入完成后必须替换此注释。 -->
## 跨领域关键联系
<!-- 列出不同 domain 词条之间已发现的重要关联，每条附 [[wikilink]]。 -->
## 开放问题与知识边界
<!-- 列出尚未被现有词条覆盖、但已多次出现的主题。 -->
## 近期重要更新
<!-- 最近 5 次摄入中最显著的知识新增或修订。 -->
```

**Wiki/log.md**（bootstrap 记录在 §1.11 写入）：

```markdown
# Wiki 操作日志
```

### 1.9 写入所有 Tools/ 脚本

按顺序写入以下脚本文件，写入完成后逐一验证。验证顺序：`python -m Tools.health --help` 通过即视为全部脚本可用。

验证失败时，在同一步骤内修复，通过后继续。

**注意**：由于 Python 脚本代码量较大，如果你的输出被截断，请自动使用继续生成（Continue）功能，或者分批次向我确认后再写入下一个文件。

---

#### Tools/common.py

```python
import hashlib
import json
import os
import re
import shutil
import subprocess as _sp
import sys
import tempfile
import unicodedata
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml

if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "Wiki"
RAW_DIR = REPO_ROOT / "Raw"
GRAPH_DIR = REPO_ROOT / "Graph"
TOOLS_DIR = REPO_ROOT / "Tools"

LOG_FILE = WIKI_DIR / "log.md"
INDEX_FILE = WIKI_DIR / "index.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"

RAW_MAPPING = REPO_ROOT / ".llm-wiki" / "raw-mapping.json"
DOMAIN_ENUM_FILE = REPO_ROOT / ".llm-wiki" / "domain-enum.json"
PENDING_QUERY = REPO_ROOT / ".qmd-pending-query.json"
INGEST_QUEUE_FILE = REPO_ROOT / ".llm-wiki" / "ingest-queue.json"
SOURCE_INDEX_CACHE = REPO_ROOT / ".llm-wiki" / "source-index-cache.json"
ENV_FILE = REPO_ROOT / ".env"

# ── 统一锚点常量（index.md 中各分类标题，字典形式，键为子目录名，值为完整标题行）──
WIKI_SECTION_HEADERS = {
    "concepts": "## Concepts",
    "entities": "## Entities",
    "sources": "## Sources",
    "syntheses": "## Syntheses",
    "disambiguations": "## Disambiguations",
}

if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

PYTHON_BIN: str = sys.executable

# ── 全局退出码常量 ──
EXIT_OK = 0
EXIT_BLOCKED = 1       # 结构性问题，需要人工/Agent 修复后重跑
EXIT_LLM_PENDING = 2   # 依赖 agent_llm 异步推理结果，需回传后重跑
EXIT_NEEDS_REVIEW = 2  # ingest.py 专用：slug 冲突或 concept/entity 覆盖验证失败，需人工处理后重跑

# ── 优化：使用 shutil.which 进行轻量级跨平台 CLI 探测 ──
def _check_cli(cmd: str) -> bool:
    """探测 CLI 是否可用。"""
    return shutil.which(cmd) is not None

QMD_AVAILABLE: bool = _check_cli("qmd")
MARKITDOWN_AVAILABLE: bool = _check_cli("markitdown")

def _run_qmd(args: List[str], **kwargs):
    """运行 qmd 命令，自动处理 Windows 包装脚本（.cmd/.ps1）的兼容性。"""
    use_shell = sys.platform == "win32"
    return _sp.run(["qmd"] + args, shell=use_shell, **kwargs)

def normalize_path_str(s: str) -> str:
    return unicodedata.normalize("NFC", Path(s).as_posix())

def is_raw_path(p: str) -> bool:
    return normalize_path_str(p).lower().startswith("raw/")

def read_file(path: Path) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

def write_file(path: Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

def append_log(entry: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry.rstrip("\n") + "\n")

def sha256_file(path, truncate=32):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    full = h.hexdigest()
    return full[:truncate] if truncate else full

WIKI_SYSTEM_FILES: Set[str] = {
    "index.md", "log.md", "overview.md",
    "health-report.md", "lint-report.md",
    "_semantic_lint_context.md",
    "_annotation_check_result.md",
    "_blind_spot_result.md",
}

def all_wiki_pages() -> List[Path]:
    if not WIKI_DIR.exists():
        return []
    return sorted(
        p for p in WIKI_DIR.rglob("*.md")
        if not (p.parent == WIKI_DIR and p.name in WIKI_SYSTEM_FILES)
    )

def extract_wikilinks(text: str) -> List[str]:
    raw = re.findall(r"\[\[([^\]]+)\]\]", text)
    targets = [item.split("|")[0].strip() for item in raw]
    return list(dict.fromkeys(targets))

def resolve_wikilink(name: str) -> Optional[Path]:
    clean = unicodedata.normalize("NFC", name.rstrip("/"))
    if clean.lower().endswith(".md"):
        clean = clean[:-3]
    candidates = [
        REPO_ROOT / f"{clean}.md",
        WIKI_DIR / f"{clean}.md",
    ]
    for subdir in ("concepts", "entities", "sources", "syntheses", "disambiguations"):
        stem = Path(clean).name
        candidates.append(WIKI_DIR / subdir / f"{stem}.md")
    for c in candidates:
        normalized = Path(unicodedata.normalize("NFC", str(c)))
        if normalized.exists():
            return normalized.resolve()
    return None

def load_allowed_raw_dirs() -> List[Dict]:
    if not RAW_MAPPING.exists():
        raise FileNotFoundError(
            f"配置文件缺失：{RAW_MAPPING}\n"
            "请确认 bootstrap 已正常完成，或重新运行 bootstrap 流程。"
        )
    data = json.loads(RAW_MAPPING.read_text(encoding="utf-8"))
    dirs = data.get("dirs", [])
    if not dirs:
        raise ValueError(
            f"配置文件 {RAW_MAPPING} 中 'dirs' 为空，请检查 bootstrap 输出。"
        )
    return dirs

def load_domain_enum() -> List[str]:
    if not DOMAIN_ENUM_FILE.exists():
        return []
    try:
        data = json.loads(DOMAIN_ENUM_FILE.read_text(encoding="utf-8"))
        return data.get("domains", [])
    except Exception:
        return []

def init_env() -> None:
    """Initialize environment for graph building (no-op in current setup)."""
    pass

def ensure_utf8() -> None:
    """Ensure stdout uses UTF-8 encoding."""
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

def parse_ingest_records(log_text: str) -> List[Tuple[str, str, str, str]]:
    pattern = re.compile(
        r"^## \[(\d{4}-\d{2}-\d{2})\] ingest \| .+? \| \[\[(.+?)\]\] "
        r"\| sha256:([0-9a-f]{32}) \| slug:(\S+)",
        re.MULTILINE
    )
    return [(m.group(1), m.group(2), m.group(3), m.group(4)) for m in pattern.finditer(log_text)]

def parse_frontmatter(content: str) -> dict:
    m = re.match(r"^\s*---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}

def _clean_wikilink_str(raw: str) -> str:
    """
    安全剥离 [[...]] 包裹，仅匹配开头/结尾的双方括号。
    """
    if not isinstance(raw, str):
        return ""
    s = raw.strip().strip('"').strip("'").strip()
    m = re.match(r"^\[\[(.+)\]\]$", s)
    return m.group(1).strip() if m else s

def _extract_raw_sources_from_frontmatter(fm: dict) -> Set[str]:
    """
    从 frontmatter 的 sources 字段中提取所有 Raw 路径。
    支持 sources 为列表、JSON 字符串或纯文本含 [[...]] 的情况，并扁平化 YAML 误解的嵌套列表。
    """
    raw_paths: Set[str] = set()
    sources_val = fm.get("sources")
    if not sources_val:
        return raw_paths

    if isinstance(sources_val, list):
        for item in sources_val:
            if isinstance(item, str):
                for link in extract_wikilinks(item):
                    raw_paths.add(normalize_path_str(link))
            elif isinstance(item, list):
                # 处理嵌套列表：扁平化
                flat = item
                while isinstance(flat, list) and len(flat) == 1:
                    flat = flat[0]
                if isinstance(flat, str):
                    for link in extract_wikilinks(flat) or [flat]:
                        raw_paths.add(normalize_path_str(_clean_wikilink_str(link) or link))
        return raw_paths

    if isinstance(sources_val, str):
        try:
            parsed = json.loads(sources_val)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, str):
                        for link in extract_wikilinks(item):
                            raw_paths.add(normalize_path_str(link))
                return raw_paths
        except Exception:
            pass
        for link in extract_wikilinks(sources_val):
            raw_paths.add(normalize_path_str(link))
        return raw_paths

    return raw_paths

def check_slug_conflict(
    slug: str,
    raw_rel: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    检查 slug 冲突，合并磁盘与日志来源，一次性构建完整映射。
    """
    log_text = read_file(LOG_FILE) if LOG_FILE.exists() else ""
    slug_map: Dict[str, Tuple[Path, Optional[str], Set[str]]] = {}

    for subdir in ("concepts", "entities", "sources", "syntheses", "disambiguations"):
        target_path = WIKI_DIR / subdir / f"{slug}.md"
        if target_path.exists():
            content = read_file(target_path)
            fm = parse_frontmatter(content)
            raw_link_val = fm.get("raw_link", "")

            existing_raw: Optional[str] = None
            if isinstance(raw_link_val, str):
                existing_raw = _clean_wikilink_str(raw_link_val) or None
            elif isinstance(raw_link_val, list):
                flat = raw_link_val
                while isinstance(flat, list) and len(flat) == 1:
                    flat = flat[0]
                if isinstance(flat, str):
                    existing_raw = _clean_wikilink_str(flat) or flat.strip() or None
                if existing_raw:
                    print(f"WARN: {target_path.relative_to(REPO_ROOT)} 的 raw_link 字段格式异常"
                          f"（被 YAML 解析为嵌套列表，已尽力恢复为: {existing_raw}）。"
                          f"建议修正为单行字符串: raw_link: \"[[{existing_raw}]]\"")

            raw_sources = _extract_raw_sources_from_frontmatter(fm)
            if not existing_raw and raw_sources:
                existing_raw = next(iter(raw_sources))

            slug_map[slug] = (target_path, existing_raw, raw_sources)

    if log_text:
        for _, log_raw, _, log_slug in parse_ingest_records(log_text):
            if log_slug == slug and slug not in slug_map:
                slug_map[slug] = (LOG_FILE, log_raw, set())

    if slug not in slug_map:
        return False, None

    existing_path, existing_raw, existing_sources = slug_map[slug]

    if raw_rel is None:
        return True, str(existing_path.relative_to(REPO_ROOT))

    normalized_input = normalize_path_str(raw_rel)
    if existing_raw and normalize_path_str(existing_raw) == normalized_input:
        return False, None
    if any(normalize_path_str(s) == normalized_input for s in existing_sources):
        return False, None

    if log_text:
        moved = parse_moved_paths(log_text)
        seen_raws: Set[str] = set()
        for _, rec_raw, _, rec_slug in parse_ingest_records(log_text):
            if rec_slug == slug:
                current_raw = moved.get(normalize_path_str(rec_raw), normalize_path_str(rec_raw))
                seen_raws.add(current_raw)
        if normalized_input not in seen_raws and seen_raws:
            return True, f"log.md: slug '{slug}' 已被不同源文件使用: {seen_raws}"

    return False, None

def parse_log_slugs(log_text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for _, _, _, slug in parse_ingest_records(log_text):
        result[slug] = "ingest"
    qs_pattern = re.compile(r"^## .+? query-synthesis(?:-update)? \|.+\| slug:(\S+)", re.MULTILINE)
    for m in qs_pattern.finditer(log_text):
        result[m.group(1).strip()] = "query-synthesis"
    return result

def list_pending_review() -> List[Path]:
    result = []
    for page in all_wiki_pages():
        content = read_file(page)
        if re.search(r"^pending_review:\s*true\s*$", content, re.MULTILINE):
            result.append(page)
    return result

def find_pages_by_raw_source(raw_rel: str) -> List[Path]:
    """返回所有 frontmatter 中引用指定 raw_rel 的 wiki 页面。"""
    result = []
    target = normalize_path_str(raw_rel)
    for page in all_wiki_pages():
        content = read_file(page)
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        links = extract_wikilinks(fm_match.group(1))
        if target in {normalize_path_str(l) for l in links}:
            result.append(page)
    return result

# ── 优化：基于文件 mtime 的增量反向索引缓存机制 ──
def build_raw_source_index() -> Dict[str, List[Path]]:
    """
    构建 raw_rel -> [引用该 raw 文件的页面] 的反向索引。
    采用基于文件 mtime 的增量缓存机制，避免大规模知识库下 O(N) 的反复解析延迟。
    """
    cache_file = SOURCE_INDEX_CACHE
    cache_data = {}
    if cache_file.exists():
        try:
            cache_data = json.loads(read_file(cache_file))
        except Exception:
            pass

    index: Dict[str, List[Path]] = {}
    needs_save = False
    valid_pages = set()

    for page in all_wiki_pages():
        page_str = page.as_posix()
        valid_pages.add(page_str)
        try:
            mtime = page.stat().st_mtime
        except Exception:
            continue

        # 命中缓存且文件未修改
        if page_str in cache_data and cache_data[page_str].get("mtime") == mtime:
            links = cache_data[page_str].get("links", [])
        else:
            # 未命中或已修改，重新解析 frontmatter
            content = read_file(page)
            fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            links = []
            if fm_match:
                links = extract_wikilinks(fm_match.group(1))
            cache_data[page_str] = {"mtime": mtime, "links": links}
            needs_save = True

        for link in links:
            norm = normalize_path_str(link)
            index.setdefault(norm, []).append(page)

    # 清理已删除文件的缓存条目
    stale_keys = [k for k in cache_data if k not in valid_pages]
    if stale_keys:
        for k in stale_keys:
            del cache_data[k]
        needs_save = True

    if needs_save:
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            write_file(cache_file, json.dumps(cache_data, ensure_ascii=False))
        except Exception as e:
            print(f"WARN: 无法写入索引缓存 {cache_file.name}: {e}")

    return index

def find_pages_by_raw_source_indexed(raw_rel: str, index: Dict[str, List[Path]]) -> List[Path]:
    """使用预构建索引的查询版本。"""
    return index.get(normalize_path_str(raw_rel), [])

def parse_moved_paths(log_text: str) -> Dict[str, str]:
    """解析 move 记录，直接按日志追加的自然顺序处理。"""
    move_pattern = re.compile(
        r"^## (\d{4}-\d{2}-\d{2}) chore \| move: (.+?) -> (.+)$",
        re.MULTILINE
    )
    matches = list(move_pattern.finditer(log_text))
    origin_of: Dict[str, str] = {}
    moves: Dict[str, str] = {}
    for m in matches:
        old_path, new_path = m.group(2), m.group(3)
        origin = origin_of.get(old_path, old_path)
        moves[origin] = new_path
        origin_of[new_path] = origin
    return moves

def load_graph_json() -> Optional[dict]:
    graph_file = GRAPH_DIR / "graph.json"
    if not graph_file.exists():
        return None
    try:
        return json.loads(graph_file.read_text(encoding="utf-8"))
    except Exception:
        return None

def agent_llm(prompt: str, output_var: str = "LLM_OUTPUT") -> str:
    request_id = str(uuid.uuid4())[:8]
    print(f"\n[AGENT_LLM_REQUEST:{request_id}] output_var={output_var}")
    print("-" * 60)
    print(prompt)
    print("-" * 60)
    print(f"[/AGENT_LLM_REQUEST:{request_id}]")
    print(f"请基于上述提示完成推理，并将结果作为 {output_var} 变量输出。\n")
    return "[AGENT_PENDING]"

def qmd_embed_wiki() -> None:
    if QMD_AVAILABLE:
        try:
            _run_qmd(
                ["embed", "--collection", "wiki"],
                cwd=REPO_ROOT, capture_output=True, timeout=60
            )
        except Exception:
            pass

def git_add_commit(files: List[Path], message: str) -> None:
    rel_paths = [str(f.relative_to(REPO_ROOT)) for f in files]
    try:
        _sp.run(["git", "add"] + rel_paths, cwd=REPO_ROOT, check=True, capture_output=True)
        _sp.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True, capture_output=True)
    except _sp.CalledProcessError as e:
        print(f"WARN: Git 操作失败: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        print(f"WARN: Git 异常: {e}")
```

---

#### Tools/health.py

```python
#!/usr/bin/env python3
import argparse
import json
import re
import subprocess as _sp
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple
from Tools.common import (
    REPO_ROOT, WIKI_DIR, RAW_DIR, LOG_FILE, INDEX_FILE, OVERVIEW_FILE,
    INGEST_QUEUE_FILE,
    read_file, write_file, append_log,
    extract_wikilinks, all_wiki_pages, resolve_wikilink,
    load_allowed_raw_dirs, load_domain_enum,
    sha256_file, list_pending_review, find_pages_by_raw_source,
    git_add_commit, parse_log_slugs, parse_moved_paths,
    parse_ingest_records, parse_frontmatter, QMD_AVAILABLE, _run_qmd,
    EXIT_OK, EXIT_BLOCKED,  # Bug 3 修复：导入退出码常量
)
def _all_wiki_pages_relative() -> Dict[str, Path]:
    return {
        p.relative_to(REPO_ROOT).as_posix(): p
        for p in all_wiki_pages()
    }
def check_empty_pages(pages: Dict[str, Path]) -> List[str]:
    issues = []
    for rel, p in pages.items():
        content = read_file(p)
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).strip()
        if not body:
            issues.append(f"空文件/存根页: {rel}")
    return issues
def check_index_sync(pages: Dict[str, Path]) -> List[str]:
    issues = []
    if not INDEX_FILE.exists():
        return ["index.md 不存在"]
    index_text = read_file(INDEX_FILE)
    linked = re.findall(r"\[([^\]]*)\]\(([^)]+\.md)\)", index_text)
    index_paths: set = set()
    for _, lnk_path in linked:
        abs_p = WIKI_DIR / lnk_path
        if abs_p.exists():
            index_paths.add(abs_p.relative_to(REPO_ROOT).as_posix())
    excluded = {
        (WIKI_DIR / "index.md").relative_to(REPO_ROOT).as_posix(),
        (WIKI_DIR / "log.md").relative_to(REPO_ROOT).as_posix(),
        (WIKI_DIR / "overview.md").relative_to(REPO_ROOT).as_posix(),
    }
    disk_pages = set(pages.keys()) - excluded
    index_pages = index_paths - excluded
    for rel in disk_pages - index_pages:
        issues.append(f"磁盘有但 index.md 未收录: {rel}")
    for rel in index_pages - disk_pages:
        issues.append(f"index.md 收录但磁盘不存在: {rel}")
    return issues
def check_log_coverage(pages: Dict[str, Path]) -> List[str]:
    issues = []
    if not LOG_FILE.exists():
        return ["log.md 不存在"]
    log_text = read_file(LOG_FILE)
    slug_map = parse_log_slugs(log_text)
    excluded_names = {"index", "log", "overview"}
    for rel, p in pages.items():
        stem = p.stem
        if stem in excluded_names:
            continue
        subdir = Path(rel).parts[1] if len(Path(rel).parts) > 1 else ""
        if stem not in slug_map:
            issues.append(f"日志覆盖缺失: {rel}")
        elif subdir == "syntheses" and not slug_map[stem].startswith("query-synthesis"):
            issues.append(f"综述页未经正规 query-synthesis 流程登记（当前类型: {slug_map[stem]}）: {rel}")
    return issues
def check_overview_placeholder() -> List[str]:
    issues = []
    if not OVERVIEW_FILE.exists():
        return ["overview.md 不存在"]
    content = read_file(OVERVIEW_FILE)
    sections = [
        "当前研究焦点",
        "跨领域关键联系",
        "开放问题与知识边界",
        "近期重要更新",
    ]
    for sec_title in sections:
        pattern = rf"## {re.escape(sec_title)}\n(.*?)(?=\n## |\Z)"
        m = re.search(pattern, content, re.DOTALL)
        if not m:
            issues.append(f'overview.md 缺少 section: "{sec_title}"')
            continue
        body = m.group(1).strip()
        body_clean = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
        if not body_clean:
            issues.append(f'overview.md 的"{sec_title}"节仍为占位内容，请 Agent 更新')
    return issues
def check_broken_links(pages: Dict[str, Path]) -> List[str]:
    issues = []
    for rel, p in pages.items():
        content = read_file(p)
        links = extract_wikilinks(content)
        for link in links:
            if link.startswith("Raw/"):
                raw_path = REPO_ROOT / link
                if not raw_path.exists():
                    issues.append(f"Raw 断链: {rel} -> [[{link}]]")
                continue
            resolved = resolve_wikilink(link)
            if resolved is None:
                issues.append(f"断链: {rel} -> [[{link}]]")
    return issues
def check_assets_links(pages: Dict[str, Path]) -> List[str]:
    issues = []
    for rel, p in pages.items():
        content = read_file(p)
        asset_refs = re.findall(
            r"!\[[^\]]*\]\((Raw/Assets/[^\)]+)\)|!\[\[([^\]]*Raw/Assets/[^\]]*)\]\]",
            content
        )
        for g1, g2 in asset_refs:
            ref = g1 or g2
            asset_path = REPO_ROOT / ref
            if not asset_path.exists():
                issues.append(f"Assets 断链: {rel} -> {ref}")
    return issues
def check_raw_dir_compliance() -> List[str]:
    issues = []
    if not RAW_DIR.exists():
        return ["Raw/ 目录不存在"]
    try:
        allowed = {d["name"] for d in load_allowed_raw_dirs()}
    except (FileNotFoundError, ValueError) as e:
        return [f"配置文件错误: {e}"]
    exempt = {"Thumbs.db"}
    for item in RAW_DIR.iterdir():
        if item.name.startswith(".") or item.name in exempt:
            continue
        if item.name not in allowed:
            issues.append(f"Raw 目录合规警告: Raw/{item.name} 不在允许列表中")
    return issues
def check_hash_consistency() -> List[str]:
    issues = []
    if not LOG_FILE.exists():
        return []
    log_text = read_file(LOG_FILE)
    moved_paths = parse_moved_paths(log_text)
    delete_pattern = re.compile(
        r"^## .+? chore \| delete: (.+)$",
        re.MULTILINE
    )
    deleted_paths = {m.group(1) for m in delete_pattern.finditer(log_text)}
    ingest_by_path: Dict[str, str] = {}
    for _, raw_rel, recorded_hash, _ in parse_ingest_records(log_text):
        ingest_by_path[raw_rel] = recorded_hash
    for raw_rel, recorded_hash in ingest_by_path.items():
        if raw_rel in deleted_paths:
            continue
        effective_path = moved_paths.get(raw_rel, raw_rel)
        file_path = REPO_ROOT / effective_path
        if not file_path.exists():
            if effective_path != raw_rel:
                issues.append(
                    f"WARN: [move后路径不存在] 原路径: {raw_rel} -> 当前路径: {effective_path}\n"
                    f"  文件可能已再次移动或删除，请执行 chore: move 或 chore: delete 更新记录"
                )
            else:
                issues.append(
                    f"WARN: [路径不存在] {raw_rel}：文件可能已被移动或删除，"
                    f"如已移动请执行 chore: move，如已删除请执行 chore: delete"
                )
        else:
            current_hash = sha256_file(file_path)
            if current_hash != recorded_hash:
                related = find_pages_by_raw_source(raw_rel)
                if related and all(
                    re.search(r"^pending_review:\s*true\s*$", read_file(p), re.MULTILINE)
                    for p in related
                ):
                    continue
                issues.append(
                    f"WARN: [内容已修改] {effective_path}：当前哈希与摄入记录不一致，"
                    f"请确认是否需要重新摄入（若为手动编辑后的文件，重新执行 ingest 即可更新哈希基准）"
                )
    return issues
def check_pending_review() -> List[str]:
    pending = list_pending_review()
    return [f"待裁决: {p.relative_to(REPO_ROOT).as_posix()}" for p in pending]
def check_domain_compliance(pages: Dict[str, Path]) -> List[str]:
    issues = []
    allowed = load_domain_enum()
    if not allowed:
        issues.append("domain 枚举配置文件缺失或为空（.llm-wiki/domain-enum.json），请检查 bootstrap 完整性")
        return issues
    excluded_names = {"index", "log", "overview"}
    for rel, p in pages.items():
        if p.stem in excluded_names:
            continue
        content = read_file(p)
        fm = parse_frontmatter(content)
        domain_val = fm.get("domain")
        if domain_val is None:
            continue
        if isinstance(domain_val, str) and domain_val not in allowed:
            issues.append(f"domain 值非法: {rel}（值：{domain_val}，合法枚举：{', '.join(allowed)}）")
    return issues
def check_frontmatter_parse(pages: Dict[str, Path]) -> List[str]:
    """检查所有页面是否包含可解析的 frontmatter 块，若存在但解析失败则报 WARN。"""
    issues = []
    for rel, p in pages.items():
        content = read_file(p)
        if re.match(r"^---\n", content):
            fm = parse_frontmatter(content)
            if not fm:
                issues.append(f"frontmatter 解析失败: {rel}（可能包含无效 YAML，请检查引号、冒号等）")
                continue
            # ── Bug 2 配套检查：raw_link / sources 误写成裸双方括号导致 YAML 嵌套 list ──
            raw_link_val = fm.get("raw_link")
            if isinstance(raw_link_val, list):
                issues.append(
                    f"raw_link 字段格式异常: {rel}（疑似漏写引号，"
                    f"应写为 raw_link: \"[[Raw/...]]\" 而非裸 [[...]]）"
                )
            sources_val = fm.get("sources")
            if isinstance(sources_val, list) and any(isinstance(it, list) for it in sources_val):
                issues.append(
                    f"sources 字段格式异常: {rel}（列表元素中存在嵌套列表，"
                    f"疑似某项漏写引号，应为 [\"[[Raw/...]]\"]）"
                )
    return issues
def check_qmd_collections() -> List[str]:
    issues = []
    if not QMD_AVAILABLE:
        return issues
    try:
        result = _run_qmd(["collection", "list"], capture_output=True, timeout=5)
        if result.returncode != 0:
            issues.append("qmd collection list 执行失败，无法检查集合状态")
            return issues
        stdout = result.stdout.decode("utf-8", errors="replace")
        collections = set()
        for line in stdout.splitlines():
            m = re.match(r"^(\w+)\s+qmd://", line)
            if m:
                collections.add(m.group(1))
        if "wiki" not in collections:
            issues.append("qmd wiki 集合未初始化，请运行: qmd init --collection wiki Wiki/")
        if "raw" not in collections:
            issues.append("qmd raw 集合未初始化，请运行: qmd init --collection raw Raw/")
    except Exception as e:
        issues.append(f"qmd 集合检查异常: {e}")
    return issues
def check_ingest_queue_residual() -> List[str]:
    issues = []
    if INGEST_QUEUE_FILE.exists():
        try:
            data = json.loads(read_file(INGEST_QUEUE_FILE))
            pending_count = len(data.get("pending", []))
            if pending_count > 0:
                issues.append(
                    f"存在未完成的摄入批次（剩余 {pending_count} 个文件），"
                    "建议执行 ingest 继续或手动删除 .llm-wiki/ingest-queue.json 重置。"
                )
        except Exception:
            issues.append("ingest-queue.json 文件损坏，建议手动删除 .llm-wiki/ingest-queue.json 重置。")
    return issues
def run_health(save: bool = False, as_json: bool = False) -> int:
    pages = _all_wiki_pages_relative()
    results = {
        "空文件/存根页": check_empty_pages(pages),
        "索引同步": check_index_sync(pages),
        "日志覆盖": check_log_coverage(pages),
        "Overview占位": check_overview_placeholder(),
        "断链": check_broken_links(pages),
        "Assets断链": check_assets_links(pages),
        "Raw目录合规": check_raw_dir_compliance(),
        "哈希一致性": check_hash_consistency(),
        "pending_review": check_pending_review(),
        "Domain合规": check_domain_compliance(pages),
        "Frontmatter解析": check_frontmatter_parse(pages),
        "qmd集合状态": check_qmd_collections(),
        "摄入批次残留": check_ingest_queue_residual(),
    }
    # Domain 合规及 Frontmatter 解析属于质量建议，非阻塞
    NON_BLOCKING = {"日志覆盖", "Overview占位", "摄入批次残留", "Domain合规", "Frontmatter解析"}
    severe_issues = [item for cat, issues in results.items() if cat not in NON_BLOCKING for item in issues]
    all_issues = [item for issues in results.values() for item in issues]
    passed = len(severe_issues) == 0
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("LLM Wiki 健康检查报告")
        print("=" * 60)
        for category, issues in results.items():
            if category in NON_BLOCKING:
                severity = "INFO"
                level = "（质量建议，非阻塞）"
            else:
                severity = "WARN"
                level = "（结构错误，需修复）"
            status = "PASS" if not issues else f"{severity}: {len(issues)} 项{level}"
            print(f"\n[{category}] {status}")
            for issue in issues:
                print(f"  - {issue}")
        print("\n" + "=" * 60)
        if passed:
            print("[PASS] 全部通过，知识库结构健康。")
        else:
            print(f"[WARN] 共发现 {len(severe_issues)} 项阻塞问题，请处理后重新检查。（另有 {len(all_issues) - len(severe_issues)} 项非阻塞提示）")
        print("=" * 60)
    summary = "通过" if passed else f"{len(severe_issues)}项阻塞问题"
    today = date.today().isoformat()
    append_log(f"## [{today}] health | {summary}")
    if save:
        report_path = WIKI_DIR / "health-report.md"
        lines = [f"# 健康检查报告 {today}\n"]
        for category, issues in results.items():
            lines.append(f"\n## {category}\n")
            if not issues:
                lines.append("[PASS]\n")
            else:
                for issue in issues:
                    lines.append(f"- {issue}\n")
        write_file(report_path, "".join(lines))
        print(f"\n报告已保存至 Wiki/health-report.md")
    return EXIT_OK if passed else EXIT_BLOCKED  # Bug 3 修复：使用常量
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Wiki 健康检查 v1.0")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--save", action="store_true", help="将报告保存至 Wiki/health-report.md")
    args = parser.parse_args()
    sys.exit(run_health(save=args.save, as_json=args.json))
```

---

#### Tools/ingest.py

```python
#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from Tools.common import (
    REPO_ROOT, WIKI_DIR, RAW_DIR, LOG_FILE, INDEX_FILE, OVERVIEW_FILE,
    TOOLS_DIR, PYTHON_BIN, QMD_AVAILABLE, MARKITDOWN_AVAILABLE, INGEST_QUEUE_FILE,
    WIKI_SECTION_HEADERS,
    read_file, write_file, append_log,
    extract_wikilinks, all_wiki_pages, resolve_wikilink,
    load_allowed_raw_dirs, sha256_file, normalize_path_str,
    check_slug_conflict, git_add_commit,
    find_pages_by_raw_source, parse_ingest_records, parse_log_slugs, qmd_embed_wiki,
    parse_frontmatter,
    build_raw_source_index, find_pages_by_raw_source_indexed,  # Bug 5 修复
    EXIT_OK, EXIT_BLOCKED, EXIT_NEEDS_REVIEW,
)
CONTENT_PREVIEW_CHARS = 4000
MAX_BYTES = 500_000
DEFAULT_BATCH_SIZE = 5   # 可在 Tools/ingest.py 中手动调整批处理大小
SUPPORTED_EXTS = {".md", ".txt", ".pdf", ".docx", ".pptx", ".xlsx", ".html", ".epub"}
# ──────────────────────────────────────────────
# 自然排序工具（替代中文卷号排序）
# ──────────────────────────────────────────────
def _natural_key(s: str) -> tuple:
    """将字符串拆分为数字与非数字部分，数字转为 int，用于自然排序。"""
    def convert(chunk: str):
        return int(chunk) if chunk.isdigit() else chunk.lower()
    return tuple(convert(chunk) for chunk in re.split(r'(\d+)', s))
# ──────────────────────────────────────────────
# 日志索引（哈希去重基础）
# ──────────────────────────────────────────────
def _load_log_index() -> Dict[str, str]:
    result: Dict[str, str] = {}
    if not LOG_FILE.exists():
        return result
    for _, raw_rel, recorded_hash, _ in parse_ingest_records(read_file(LOG_FILE)):
        result[normalize_path_str(raw_rel)] = recorded_hash
    return result
# ──────────────────────────────────────────────
# 候选文件收集
# ──────────────────────────────────────────────
def _has_source_map_for_raw(raw_rel: str) -> bool:
    """检查是否有 source_map 的 raw_link 指向该 Raw 文件（比 log_index SHA 更可靠）。"""
    return len(find_pages_by_raw_source(raw_rel)) > 0
# ── Bug 5 修复：_collect_candidates_from_args 使用预构建索引 ──
def _collect_candidates_from_args(targets: List[str]) -> List[str]:
    log_index = _load_log_index()
    allowed_dirs = load_allowed_raw_dirs()
    ingest_map = {d["name"]: d.get("ingest", True) for d in allowed_dirs}
    seen = set()
    result = []
    # 一次性建立反向索引
    raw_source_index = build_raw_source_index()
    for t in targets:
        p = Path(t)
        if not p.is_absolute():
            if (REPO_ROOT / p).exists():
                p = REPO_ROOT / p
            elif (RAW_DIR / p).exists():
                p = RAW_DIR / p
            else:
                print(f"WARN: 路径不存在，跳过: {t}")
                continue
        if p.is_dir():
            files = sorted((f for f in p.rglob("*")
                            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS),
                           key=lambda f: _natural_key(f.stem))
        elif p.is_file():
            files = [p]
        else:
            print(f"WARN: 路径不存在，跳过: {t}")
            continue
        for f in files:
            # 硬性前置条件：候选文件必须位于 Raw/ 下
            if not f.is_relative_to(RAW_DIR):
                print(f"WARN: {f} 不在 Raw/ 目录下，跳过（仅支持 Raw/ 下的文件）。")
                continue
            try:
                rel = normalize_path_str(f.relative_to(REPO_ROOT).as_posix())
            except ValueError:
                print(f"WARN: 路径不在仓库范围内，跳过: {f}")
                continue
            # 检查所属 Raw 子目录的 ingest 标志
            parts = f.relative_to(RAW_DIR).parts
            if parts and parts[0] in ingest_map and not ingest_map[parts[0]]:
                print(f"WARN: {rel} 所在目录 '{parts[0]}' 的 ingest=false，跳过。")
                continue
            if rel in seen:
                continue
            seen.add(rel)
            # 使用索引查询，O(1) 替代原先的 O(页面数) 扫描
            if find_pages_by_raw_source_indexed(rel, raw_source_index):
                continue
            if rel in log_index and sha256_file(f) == log_index[rel]:
                continue
            result.append(rel)
    result.sort(key=lambda rel: _natural_key(Path(rel).stem))
    return result
# ── Bug 5 修复：_collect_all_pending 使用预构建索引 ──
def _collect_all_pending() -> List[str]:
    log_index = _load_log_index()
    try:
        allowed = load_allowed_raw_dirs()
    except (FileNotFoundError, ValueError) as e:
        print(f"WARN: 无法加载目录配置：{e}")
        return []
    ingest_dirs = [d["name"] for d in allowed if d.get("ingest", True)]
    result = []
    # 一次性建立反向索引
    raw_source_index = build_raw_source_index()
    for dir_name in ingest_dirs:
        dir_path = RAW_DIR / dir_name
        if not dir_path.exists():
            continue
        for f in sorted(dir_path.rglob("*"), key=lambda f: _natural_key(f.stem)):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED_EXTS:
                continue
            rel = normalize_path_str(f.relative_to(REPO_ROOT).as_posix())
            if find_pages_by_raw_source_indexed(rel, raw_source_index):
                continue
            if rel not in log_index or sha256_file(f) != log_index[rel]:
                result.append(rel)
    return result
# ──────────────────────────────────────────────
# 队列管理
# ──────────────────────────────────────────────
def _read_queue() -> Optional[dict]:
    if not INGEST_QUEUE_FILE.exists():
        return None
    try:
        return json.loads(read_file(INGEST_QUEUE_FILE))
    except Exception:
        return None
def _write_queue(data: dict) -> None:
    write_file(INGEST_QUEUE_FILE, json.dumps(data, ensure_ascii=False, indent=2))
def _queue_has_pending() -> bool:
    q = _read_queue()
    return bool(q and q.get("pending"))
def scan_and_build_queue(candidates: List[str], mode: str = "normal") -> Optional[str]:
    """
    建立或恢复批次队列。mode 参数记录触发模式（"normal" 或 "discuss"），
    用于后续 _advance_queue 输出正确的流控信号。
    若已有残留批次：模式不同时仅警告，不修改队列 mode，保持原批次模式完成。
    """
    existing = _read_queue()
    if existing and existing.get("pending"):
        pending_count = len(existing.get("pending", []))
        existing_mode = existing.get("mode", "normal")
        if existing_mode != mode:
            print(f"WARN: 残留批次模式为 {existing_mode}，当前触发模式为 {mode}。将先以 {existing_mode} 模式完成当前批次。")
            # 不修改队列 mode，避免模式切换导致信号混乱
        if candidates:
            print(f"INFO: 当前批次剩余 {pending_count} 个文件未完成，先完成当前批次。")
        else:
            print(f"INFO: 当前批次剩余 {pending_count} 个文件，继续处理。")
        # discuss 模式下若残留批次是普通批次，给出额外提示
        if mode == "discuss" and existing_mode != "discuss":
            print(f"WARN: 检测到残留的普通批次（{pending_count} 个文件），"
                  f"discuss 模式将在完成当前批次后才能触发新的讨论批次。"
                  f"若要直接进入讨论模式，请先手动删除 .llm-wiki/ingest-queue.json。")
        # 确保旧版队列文件也拥有 no_concept_slugs 字段（向后兼容）
        if "no_concept_slugs" not in existing:
            existing["no_concept_slugs"] = []
        return existing["pending"][0]
    if not candidates:
        print("OK: 暂无需要摄入或更新的文件。")
        if INGEST_QUEUE_FILE.exists():
            INGEST_QUEUE_FILE.unlink()
        return None
    total_candidates = len(candidates)
    # ── 按自然排序取前 DEFAULT_BATCH_SIZE 个 ──
    candidates.sort(key=lambda rel: _natural_key(Path(rel).stem))
    batch = candidates[:DEFAULT_BATCH_SIZE]
    batch_set = set(batch)
    candidates_norm = [normalize_path_str(c) for c in candidates]
    remaining_candidates = [c for c in candidates_norm if c not in batch_set]
    queue_data = {
        "created": date.today().isoformat(),
        "total_candidates": total_candidates,
        "total": len(batch),
        "pending": batch,
        "done": [],
        "skipped": [],
        "remaining_candidates": remaining_candidates,
        "mode": mode,  # 记录触发模式，供 _advance_queue 使用
        "no_concept_slugs": [],
    }
    _write_queue(queue_data)
    print(f"INFO: 发现 {total_candidates} 个待摄入/已修改文件，本批次处理其中 {len(batch)} 个：")
    for i, p in enumerate(batch, 1):
        print(f"  {i}. {p}")
    if remaining_candidates:
        print(f"\n提示：本批次（{len(batch)} 个）处理完后将自动继续下一批。剩余 {len(remaining_candidates)} 个文件。")
    return batch[0]
def _run_batch_end_validation(queue_data: dict, force: bool = False) -> Tuple[bool, List[str], List[str]]:
    """返回 (是否阻断, 人类可读报告, 缺失覆盖的 raw_rel 列表)"""
    if force:
        return False, [], []
    done = queue_data.get("done", [])
    no_concept_slugs = queue_data.get("no_concept_slugs", [])
    return _check_concept_coverage(done, no_concept_slugs)
def _print_queue_status(remaining: int, queue_mode: str) -> None:
    """输出队列状态信号（避免 _advance_queue 和 _skip_and_advance 重复代码）。"""
    if remaining == 0:
        print("[STOP] 批次已全部完成。")
    else:
        if queue_mode == "discuss":
            print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
        else:
            print(f"[CONTINUE] 立即执行：python -m Tools.ingest")
# ── Bug 1 修复：重写 _advance_queue，在函数顶部统一处理 no_concept 写入 ──
def _requeue_missing_raws(queue_data: dict, pending: list, done: list, missing_raws: list) -> None:
    """将批次末尾验证失败的源文件从 done 移回 pending 队首，并持久化队列。"""
    for mr in missing_raws:
        if mr in done:
            done.remove(mr)
            pending.insert(0, mr)
    if missing_raws:
        queue_data["pending"] = pending
        queue_data["done"] = done
        _write_queue(queue_data)
def _advance_queue(raw_rel: str, subdir: str = "", slug: str = "",
                   title: str = "", force: bool = False,
                   no_concept: bool = False) -> int:
    queue_data = _read_queue()
    if queue_data is None:
        print("[STOP] 无批次清单。")
        return 0
    pending = queue_data.get("pending", [])
    done = queue_data.get("done", [])
    skipped = queue_data.get("skipped", [])
    no_concept_slugs = queue_data.get("no_concept_slugs", [])
    queue_mode = queue_data.get("mode", "normal")
    # ── Bug 1 修复：no_concept 标记的写入与去重，统一提到所有分支之前处理 ──
    # 原代码只在 `raw_rel in done`（重复调用）分支里写 no_concept_slugs，
    # 导致首次正常调用（raw_rel in pending）时该标记从未被记录，
    # 批次末尾验证因此无法豁免该文件。
    if no_concept and subdir == "sources" and slug and slug not in no_concept_slugs:
        no_concept_slugs.append(slug)
        queue_data["no_concept_slugs"] = no_concept_slugs
    if raw_rel in done:
        remaining = len(pending)
        _write_queue(queue_data)
        _print_queue_status(remaining, queue_mode)
        return 0
    if raw_rel in skipped:
        skipped.remove(raw_rel)
        done.append(raw_rel)
        queue_data["skipped"] = skipped
        queue_data["done"] = done
        _write_queue(queue_data)
        print(f"INFO: {raw_rel} 此前被标记为跳过，现已补做完成。")
        remaining = len(pending)
        _print_queue_status(remaining, queue_mode)
        return 0
    if raw_rel not in pending:
        print("[STOP] 该文件不属于当前批次。")
        return 0
    # raw_rel 在 pending 中（首次正常调用，no_concept_slugs 已在函数顶部写入）
    pending.remove(raw_rel)
    done.append(raw_rel)
    queue_data["pending"] = pending
    queue_data["done"] = done
    remaining = len(pending)
    total = queue_data.get("total", len(done) + remaining)
    if remaining > 0:
        _write_queue(queue_data)
        print(f"\nINFO: 批次进度：{len(done)}/{total} 完成，剩余 {remaining} 个。")
        _print_queue_status(remaining, queue_mode)
        return 0
    # 批次最后一个文件，执行批次末尾验证
    blocked, report, missing_raws = _run_batch_end_validation(queue_data, force=force)
    if not blocked:
        _finalize_batch(queue_data)
        return 0
    _requeue_missing_raws(queue_data, pending, done, missing_raws)
    print(
        f"[NEEDS_REVIEW] 批次末尾 concept/entity 覆盖验证失败：\n" +
        "\n".join(f"  - {line}" for line in report) +
        f"\n\n请为以上 source_map 补充对应的 concept/entity 词条后，"
        f"重新执行 --finalize（或使用 --force 跳过验证）。"
    )
    return EXIT_NEEDS_REVIEW
def _check_concept_coverage(done_rels: List[str], no_concept_slugs: List[str]) -> Tuple[bool, List[str], List[str]]:
    """
    返回 (是否阻断, 人类可读报告, 缺失覆盖的 raw_rel 列表)。
    注意：本函数刻意不使用 build_raw_source_index() 预建索引（即便 ingest.py 其他
    收集函数已采用该优化）。原因：本函数在批次末尾被调用时，本批次刚写入的
    concept/entity 页可能就是几秒前才落盘的，必须读最新磁盘状态，不能用调用更早的
    候选收集阶段建好的索引（那时这些新词条可能还不存在）。索引化此函数会导致
    "刚创建的概念页验证不到自己"的假阴性。
    """
    if not LOG_FILE.exists():
        return False, [], []
    log_text = read_file(LOG_FILE)
    done_norms = {normalize_path_str(r) for r in done_rels}
    done_raw_to_slug: Dict[str, str] = {}
    for _, rec_raw, _, rec_slug in parse_ingest_records(log_text):
        norm = normalize_path_str(rec_raw)
        if norm in done_norms:
            done_raw_to_slug[norm] = rec_slug
    batch_slugs_to_raws: Dict[str, Set[str]] = {}
    for norm, slug in done_raw_to_slug.items():
        batch_slugs_to_raws.setdefault(slug, set()).add(norm)
    batch_source_maps: Dict[str, str] = {}
    for norm, rec_slug in done_raw_to_slug.items():
        if rec_slug in no_concept_slugs:
            continue
        page = WIKI_DIR / "sources" / f"{rec_slug}.md"
        if page.exists():
            batch_source_maps[norm] = rec_slug
    if not batch_source_maps:
        return False, [], []
    covered: Dict[str, List[str]] = {r: [] for r in batch_source_maps}
    for page in all_wiki_pages():
        p_str = page.as_posix()
        if "/concepts/" not in p_str and "/entities/" not in p_str:
            continue
        content = read_file(page)
        fm = parse_frontmatter(content)
        sources_val = fm.get("sources") or ""
        if isinstance(sources_val, list):
            sources_links = []
            for item in sources_val:
                if isinstance(item, str):
                    sources_links.extend(extract_wikilinks(item))
        else:
            sources_links = extract_wikilinks(sources_val)
        norm_links = {normalize_path_str(lk) for lk in sources_links}
        for raw_rel in batch_source_maps:
            if raw_rel in norm_links:
                body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL).strip()
                if body:
                    covered[raw_rel].append(page.stem)
    missing_raws: List[str] = [
        raw_rel for raw_rel in batch_source_maps if not covered[raw_rel]
    ]
    missing_report = [
        f"[[{raw_rel}]]（source_map: {batch_source_maps[raw_rel]}）未被任何 concept/entity 引用"
        for raw_rel in missing_raws
    ]
    return bool(missing_raws), missing_report, missing_raws
def _finalize_batch(queue_data: dict) -> None:
    done = queue_data.get("done", [])
    skipped = queue_data.get("skipped", [])
    total = queue_data.get("total", len(done))
    remaining_candidates = queue_data.get("remaining_candidates", [])
    print(f"\nOK: 批次完成（{len(done)}/{total}）。")
    if remaining_candidates:
        still_pending = [c for c in remaining_candidates if c not in done and c not in skipped]
        if still_pending:
            INGEST_QUEUE_FILE.unlink(missing_ok=True)
            print(f"INFO: 自动续批：剩余 {len(still_pending)} 个文件。\n")
            scan_and_build_queue(still_pending)
            print(f"\n[CONTINUE] 立即执行：python -m Tools.ingest")
            return
    if INGEST_QUEUE_FILE.exists():
        INGEST_QUEUE_FILE.unlink()
    print("[STOP] 所有候选文件已全部完成。")
    print("\n>>> 批次后续建议："
          "\n  1. 请更新 Wiki/overview.md（当前研究焦点、跨领域联系等）"
          f"\n  2. 若本批次摄入 ≥3 个文件，建议运行：python -m Tools.lint")
def _skip_and_advance(raw_rel: str, reason: str = "", force: bool = False) -> None:
    """跳过文件并推进批次。统一写入错误日志（若提供reason），并处理队列。"""
    queue_data = _read_queue()
    if queue_data is None:
        print("[STOP] 无批次清单。")
        return
    pending = queue_data.get("pending", [])
    done = queue_data.get("done", [])
    skipped = queue_data.get("skipped", [])
    queue_mode = queue_data.get("mode", "normal")
    if reason:
        _write_error_log(f"ingest | {Path(raw_rel).name}", reason)
    if raw_rel in done:
        print(f"WARN: {raw_rel} 已通过 finalize 完成，无法再标记为 skip。")
        return
    if raw_rel in skipped:
        return  # 已在 skipped 中，无需重复操作
    if raw_rel not in pending:
        # 文件不在当前批次，仅输出警告，不改变队列状态，让用户重新确认
        print(f"WARN: {raw_rel} 不在当前批次待处理列表中，无法跳过。请确认文件路径是否正确。")
        return
    # raw_rel 在 pending 中，执行跳过
    pending.remove(raw_rel)
    skipped.append(raw_rel)
    queue_data["pending"] = pending
    queue_data["skipped"] = skipped
    _write_queue(queue_data)
    remaining = len(pending)
    if remaining == 0:
        blocked, report, missing_raws = _run_batch_end_validation(queue_data, force=force)
        if not blocked:
            _finalize_batch(queue_data)
        else:
            _requeue_missing_raws(queue_data, pending, done, missing_raws)
            requeue_msg = (f"已将缺失的源文件放回队列头部。\n" if missing_raws else "")
            print(
                f"[NEEDS_REVIEW] 批次末尾 concept/entity 覆盖验证失败，"
                f"{requeue_msg}"
                f"验证失败详情：\n" +
                "\n".join(f"  - {line}" for line in report) +
                f"\n\n请补充对应词条后重新执行 --finalize，或使用 --force 跳过验证。"
            )
    else:
        print(f"\nINFO: 已跳过，批次剩余 {remaining} 个。")
        _print_queue_status(remaining, queue_mode)
# ──────────────────────────────────────────────
# 文件处理
# ──────────────────────────────────────────────
def _convert_to_markdown(file_path: Path) -> Tuple[bool, str]:
    if file_path.suffix.lower() == ".md":
        return True, read_file(file_path)
    if not MARKITDOWN_AVAILABLE:
        print(f"WARN: markitdown 未安装，无法转换 {file_path.name}。\n"
              f"请运行 pip install 'markitdown>=0.1.0' 后重试。")
        return False, ""
    try:
        result = subprocess.run(
            ["markitdown", str(file_path)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return True, result.stdout
        print(f"WARN: markitdown 转换失败: {file_path.name}\n{result.stderr[:300]}")
        return False, ""
    except Exception as e:
        print(f"WARN: markitdown 转换异常: {file_path.name}: {e}")
        return False, ""
def _get_annotation(file_path: Path) -> str:
    try:
        allowed = load_allowed_raw_dirs()
        mapping = {d["name"]: d.get("annotation", "") for d in allowed}
        parts = file_path.relative_to(RAW_DIR).parts
        if parts:
            return mapping.get(parts[0], "") or ""
    except Exception:
        pass
    return ""
def _write_error_log(operation: str, reason: str) -> None:
    today = date.today().isoformat()
    append_log(f"## [{today}] ERROR | {operation} | {reason}")
def ingest_file(file_path: Path, discuss_mode: bool = False, force: bool = False) -> int:
    """
    处理单个文件：检查、转换、展示内容。
    discuss_mode=True 时仅做内容展示（preview only），不打印操作步骤，
    批量讨论提示由 main() 在所有文件展示完毕后统一输出。
    返回值：0=成功，1=跳过（文件不存在/转换失败），2=需人工确认（超大文件）
    """
    try:
        rel = normalize_path_str(file_path.relative_to(REPO_ROOT).as_posix())
    except ValueError:
        abs_path = (REPO_ROOT / file_path).resolve()
        try:
            rel = normalize_path_str(abs_path.relative_to(REPO_ROOT).as_posix())
            file_path = abs_path
        except ValueError:
            print(f"WARN: 路径不在仓库范围内: {file_path}")
            return 1
    if not file_path.exists():
        print(f"WARN: 文件不存在: {rel}")
        _skip_and_advance(rel, reason="文件不存在")
        return 1
    try:
        file_hash = sha256_file(file_path)
    except Exception as e:
        _write_error_log(f"ingest | {file_path.name}", f"读取文件失败: {e}")
        return 1
    annotation = _get_annotation(file_path)
    print(f"\n{'='*60}")
    print(f"处理文件: {rel}")
    if annotation:
        print(f"加注类型: （{annotation}）")
    print(f"文件哈希: sha256:{file_hash}")
    try:
        raw_size = file_path.stat().st_size
    except Exception:
        raw_size = 0
    if raw_size > MAX_BYTES and not force:
        print(f"\nWARN: 大文件警告：{rel}（{raw_size:,} 字节，约 {raw_size // 1000} KB）。\n"
              f"建议手动拆分后重新摄入，或使用 --force 强制摄入。")
        print("[NEEDS_REVIEW] 超大文件需人工确认。")
        return 2
    ok, md_content = _convert_to_markdown(file_path)
    if not ok:
        _skip_and_advance(rel, reason="文件转换失败")
        return 1
    log_index = _load_log_index()
    if rel in log_index and file_hash != log_index[rel]:
        related_pages = find_pages_by_raw_source(rel)
        for page in related_pages:
            page_content = read_file(page)
            if re.search(r"^pending_review:\s*false\s*$", page_content, re.MULTILINE):
                updated = re.sub(
                    r"^pending_review:\s*false\s*$",
                    "pending_review: true",
                    page_content,
                    flags=re.MULTILINE,
                )
                write_file(page, updated)
                print(f"INFO: 已标记 {page.name} 为 pending_review（源文件已修改）。")
    print(f"\n[INGEST_CONTENT] raw_rel={rel} hash={file_hash}")
    if annotation:
        print(f"加注规则：所有观点/推论/主观内容加注（{annotation}）")
    else:
        print("加注规则：无需加注")
    print(f"双链格式：使用基于 Vault 根目录的绝对路径，如 [[Raw/Sources/xxx.md]]")
    print(f"\n--- 文件内容（前 {CONTENT_PREVIEW_CHARS} 字符）---\n{md_content[:CONTENT_PREVIEW_CHARS]}")
    if len(md_content) > CONTENT_PREVIEW_CHARS:
        print(f"\n[截断] 文件共 {len(md_content)} 字符，已显示前 {CONTENT_PREVIEW_CHARS} 字符。"
              f"如需完整内容请用文件读取工具直接读取 {rel}")
    print("---")
    if discuss_mode:
        # discuss 模式：仅展示内容，不打印操作步骤。
        # 批量讨论提示由 main() 在所有文件展示完毕后统一输出。
        return 0
    print(f"\n【Agent 操作步骤】\n"
          f"1. 根据以上内容写入/更新 Wiki/sources/ 下的摘要词条\n"
          f"2. 写入/更新 Wiki/concepts/ 和 Wiki/entities/ 下的相关词条\n"
          f"   【批次约束】每个 source_map 词条必须至少对应一个 concept 或 entity，\n"
          f"   该词条的 frontmatter sources 字段须包含对应的 Raw 文件路径。\n"
          f"   批次内所有文件处理完后统一验证，不通过则阻断，需补充后重试。\n"
          f"   若某文件确实无可提取概念（纯数据表/日程等），在 --finalize 中传入\n"
          f"   --no-concept --no-concept-reason \"<原因>\" 豁免该文件。\n"
          f"3. 确认所有 [[wikilink]] 指向已存在页面（断链需同步新建桩页）\n"
          f"4. 确定 slug（词条中文文件名去后缀）、title（显示标题）、brief（≤30字摘要）\n"
          f"5. 词条全部写入后，执行：\n"
          f"   python -m Tools.ingest --finalize <slug> <title> \"{rel}\" --brief \"<brief>\"\n"
          f"   [--no-concept --no-concept-reason \"<原因>\"] # 仅无可提取概念时使用\n"
          f"\n   若需跳过本文件（无法处理），执行：\n"
          f"   python -m Tools.ingest --skip \"{rel}\"\n")
    return 0
# ──────────────────────────────────────────────
# --skip / --finalize 回传
# ──────────────────────────────────────────────
def run_skip(raw_rel: str, force: bool = False) -> int:
    normalized = normalize_path_str(raw_rel)
    print(f"INFO: 已跳过 {normalized}")
    _skip_and_advance(normalized, reason="用户主动跳过", force=force)
    return 0
def _update_index(slug: str, subdir: str, title: str, brief: str = "") -> None:
    if not INDEX_FILE.exists():
        return
    content = read_file(INDEX_FILE)
    section_header = WIKI_SECTION_HEADERS.get(subdir)
    if not section_header or f"({subdir}/{slug}.md)" in content:
        return
    if section_header not in content:
        return
    brief_part = f" -- {brief.strip()}" if brief and brief.strip() else ""
    link_line = f"- [{title}]({subdir}/{slug}.md){brief_part}\n"
    section_start = content.index(section_header)
    insert_from = section_start + len(section_header)
    next_section = content.find("\n## ", insert_from)
    if next_section == -1:
        content = content.rstrip("\n") + "\n" + link_line
    else:
        block_before = content[:next_section].rstrip("\n")
        block_after = content[next_section + 1:]
        content = block_before + "\n" + link_line + "\n" + block_after
    write_file(INDEX_FILE, content)
def _write_ingest_log(title: str, raw_rel: str, file_hash: str, slug: str) -> None:
    today = date.today().isoformat()
    entry = (
        f"## [{today}] ingest | {title} | [[{raw_rel}]] "
        f"| sha256:{file_hash} | slug:{slug}"
    )
    append_log(entry)
def _log_related_pages(raw_rel: str, file_hash: str) -> None:
    """为引用同一 raw_rel 但尚未有日志的概念/实体页补充日志条目。"""
    normalized_rel = normalize_path_str(raw_rel)
    log_text = read_file(LOG_FILE) if LOG_FILE.exists() else ""
    existing_slugs = set(parse_log_slugs(log_text).keys())
    today = date.today().isoformat()
    related = find_pages_by_raw_source(normalized_rel)
    for page in related:
        rel = page.relative_to(REPO_ROOT).as_posix()
        if not (rel.startswith("Wiki/concepts/") or rel.startswith("Wiki/entities/")):
            continue
        slug = page.stem
        if slug in existing_slugs:
            continue
        content = read_file(page)
        fm = parse_frontmatter(content)
        title = fm.get("title", slug)
        entry = (
            f"## [{today}] ingest | {title} | [[{normalized_rel}]] "
            f"| sha256:{file_hash} | slug:{slug}"
        )
        append_log(entry)
        subdir = "concepts" if rel.startswith("Wiki/concepts/") else "entities"
        _update_index(slug, subdir, title)
        print(f"  → 补齐日志: {subdir}/{slug}.md")
def _patch_index_brief(slug: str, subdir: str, title: str, brief: str) -> None:
    """在 index.md 中定位词条并补充/更新 brief 摘要。"""
    if not INDEX_FILE.exists():
        return
    idx_content = read_file(INDEX_FILE)
    link_pattern = re.compile(rf"^- \[{re.escape(title)}\]\({subdir}/{re.escape(slug)}\.md\)(.*)$", re.MULTILINE)
    m = link_pattern.search(idx_content)
    if m and not m.group(1).strip():
        new_line = f"- [{title}]({subdir}/{slug}.md) -- {brief.strip()}"
        idx_content = link_pattern.sub(new_line, idx_content, count=1)
        write_file(INDEX_FILE, idx_content)
        print(f"INFO: 已补充 index.md 中 {slug} 的摘要（brief）。")
    elif m:
        print(f"INFO: index.md 中 {slug} 已有摘要，--brief 参数被忽略。")
    else:
        print(f"WARN: 未能在 index.md 中定位 {slug} 对应的记录行（可能因 title 含特殊字符导致匹配失败），"
              f"--brief 参数未生效。请 Agent 手动检查并更新 Wiki/index.md 中该词条的摘要。")
def run_finalize(slug: str, title: str, raw_rel: str, brief: str = "",
                 force: bool = False,
                 no_concept: bool = False,
                 no_concept_reason: str = "") -> int:
    subdir: Optional[str] = None
    for d in ("concepts", "entities", "disambiguations", "syntheses", "sources"):
        if (WIKI_DIR / d / f"{slug}.md").exists():
            subdir = d
            break
    if subdir is None:
        print(f"WARN: 未找到 Wiki/*/{slug}.md，请确认 Agent 已完成词条写入后再调用 --finalize。")
        return 1
    raw_path = REPO_ROOT / raw_rel
    if not raw_path.exists():
        print(f"WARN: 原始文件不存在: {raw_rel}")
        return 1
    file_hash = sha256_file(raw_path)
    normalized_rel = normalize_path_str(raw_rel)
    log_index = _load_log_index()
    already_current = (normalized_rel in log_index and log_index[normalized_rel] == file_hash)
    if already_current:
        print(f"INFO: {raw_rel} 已摄入且哈希未变，跳过日志更新。")
        if brief and brief.strip():
            _patch_index_brief(slug, subdir, title, brief)
    else:
        if normalized_rel not in log_index:
            conflict, existing_src = check_slug_conflict(
                slug, raw_rel=normalized_rel
            )
            if conflict:
                print(f"[NEEDS_REVIEW] Slug 冲突：{subdir}/{slug}.md 已被其他来源占用（{existing_src}）。\n"
                      f"请为本词条指定新的 slug。")
                return EXIT_NEEDS_REVIEW
        _update_index(slug, subdir, title, brief=brief)
        _write_ingest_log(title, raw_rel, file_hash, slug)
        git_add_commit([WIKI_DIR], f"ingest: {title}")
        qmd_embed_wiki()
        print(f"OK: 摄入完成：{title}（slug: {slug}，存入 Wiki/{subdir}/）")
    _log_related_pages(raw_rel, file_hash)
    result = _advance_queue(
        normalized_rel, subdir=subdir, slug=slug, title=title,
        force=force, no_concept=no_concept,
    )
    if no_concept and result != EXIT_NEEDS_REVIEW:
        if LOG_FILE.exists():
            existing_log = read_file(LOG_FILE)
            marker = f"no-concept | [[{normalized_rel}]]"
            if marker not in existing_log:
                reason_str = f"（原因：{no_concept_reason}）" if no_concept_reason else "（原因未说明）"
                today_str = date.today().isoformat()
                append_log(f"## [{today_str}] ingest | no-concept | [[{normalized_rel}]] {reason_str}")
                print(f"INFO: 该文件已豁免 concept/entity 检查 {reason_str}")
    return result
# ──────────────────────────────────────────────
# main()
# ──────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM Wiki 摄入工具 v2.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
三种模式，批处理和讨论模式超过 DEFAULT_BATCH_SIZE 个文件均自动截断为一批：
批处理模式（默认，自动逐篇处理）：
  python -m Tools.ingest <路径>                  # 指定文件/目录，自动递归展开
  python -m Tools.ingest A.pdf B.md C.pdf        # 指定多个文件
  python -m Tools.ingest --force <文件>          # 强制摄入超大文件
  注意：无参数时仅恢复已有队列，不会全库扫描。需全库扫描请显式指定 Raw/ 目录。
批量预读讨论模式（最多 5 个文件一批，统一展示后讨论词条结构）：
  python -m Tools.ingest <路径> --discuss        # 指定范围，或指定 Raw/ 进行全库预读
  不带路径的 `--discuss` 仅恢复已有 discuss 批次，不会自动扫描全库。
完成词条写入后回传：
  python -m Tools.ingest --finalize <slug> <title> <raw_rel> [--brief "摘要"] [--force]
    [--no-concept --no-concept-reason "<原因>"]     # 仅无可提取概念时使用
跳过无法处理的文件（可配合 --force 跳过批次末尾验证）：
  python -m Tools.ingest --skip <raw_rel> [--force]
discuss 模式流控信号说明：
  [DISCUSS_READY]    预读完成，等待讨论后逐篇执行 --finalize
  [DISCUSS_CONTINUE] 本文件 finalize 完成，继续为剩余文件执行 --finalize
  [NEEDS_REVIEW]     需补充词条或处理冲突后重新 finalize
  [STOP]             批次全部完成
""",
    )
    parser.add_argument("targets", nargs="*", help="文件或目录路径（可混合；无参数时仅恢复已有队列）")
    parser.add_argument("--discuss", action="store_true",
                        help="批量预读讨论模式（最多5个文件，统一展示后讨论词条结构）")
    parser.add_argument("--force", action="store_true",
                        help="强制摄入超大文件；与 --skip 共用时跳过批次末尾验证")
    parser.add_argument("--finalize", nargs=3, metavar=("SLUG", "TITLE", "RAW_REL"),
                        help="Agent 完成词条写入后回传：slug、显示标题、原始文件路径")
    parser.add_argument("--brief", default="", help="词条一句话摘要（≤30字）")
    parser.add_argument("--no-concept", action="store_true", help="声明该文件无可提取概念")
    parser.add_argument("--no-concept-reason", default="", dest="no_concept_reason",
                        help="--no-concept 的原因说明")
    parser.add_argument("--skip", metavar="RAW_REL", help="跳过指定文件并推进批次")
    parser.add_argument("--abandon", action="store_true",
                        help="放弃当前批次队列，停止处理（不清除已完成的摄入记录）")
    args = parser.parse_args()
    if args.skip:
        return run_skip(args.skip, force=args.force)
    if args.finalize:
        slug, title, raw_rel = args.finalize
        return run_finalize(
            slug, title, raw_rel,
            brief=args.brief,
            force=args.force,
            no_concept=args.no_concept,
            no_concept_reason=args.no_concept_reason,
        )
    if args.abandon:
        if INGEST_QUEUE_FILE.exists():
            INGEST_QUEUE_FILE.unlink()
            print("[STOP] 队列已清空，已放弃当前批次。")
        else:
            print("无活跃批次。")
        return 0
    if args.targets:
        candidates = _collect_candidates_from_args(args.targets)
        if not candidates and not _queue_has_pending():
            print("OK: 指定路径下无需摄入或更新的文件。")
            return 0
    else:
        # 无参数时仅恢复已有队列，不得全库扫描创建新批次
        if _queue_has_pending():
            candidates = []
        else:
            print("无活跃批次。请通过 python -m Tools.ingest <路径> 指定待处理文件。")
            return 0
    # discuss 模式：建队列时记录 mode="discuss"，使 _advance_queue 输出正确信号
    queue_mode = "discuss" if args.discuss else "normal"
    first = scan_and_build_queue(candidates, mode=queue_mode)
    if first is None:
        return 0
    if not args.discuss:
        return ingest_file(
            REPO_ROOT / first,
            discuss_mode=False,
            force=args.force,
        )
    # ── discuss 批量预读模式 ──────────────────────────────────────────
    # 从队列中取最多 DEFAULT_BATCH_SIZE 个文件，逐一展示内容。
    # 展示完毕后统一输出讨论提示，Agent 讨论后逐篇 finalize。
    # _advance_queue 感知 mode="discuss"，输出 [DISCUSS_CONTINUE] 而非 [CONTINUE]。
    queue_data = _read_queue()
    if queue_data is None:
        print("[STOP] 无批次清单。")
        return 0
    # 若恢复的是残留普通批次（mode != discuss），pending 已超过 DEFAULT_BATCH_SIZE，
    # 切片确保讨论批次不超过上限；正常 discuss 批次本身已限制在 DEFAULT_BATCH_SIZE 以内。
    pending = queue_data.get("pending", [])
    discuss_batch = pending[:DEFAULT_BATCH_SIZE]
    print(f"\n{'='*60}")
    print(f"[DISCUSS 批量预读] 本批次共 {len(discuss_batch)} 个文件，逐一展示内容后统一讨论。")
    print(f"{'='*60}")
    # 预读失败的文件立即从队列移除，不进入讨论
    failed_rels: List[str] = []
    for idx, rel in enumerate(discuss_batch, 1):
        file_path = REPO_ROOT / rel
        print(f"\n{'─'*60}")
        print(f"[{idx}/{len(discuss_batch)}] {rel}")
        print(f"{'─'*60}")
        ret = ingest_file(file_path, discuss_mode=True, force=args.force)
        if ret != 0:
            print(f"WARN: 文件预读失败（ret={ret}），已从讨论批次移除：{rel}")
            _skip_and_advance(rel, reason="预读失败")
            failed_rels.append(rel)
    # 剔除失败文件，只讨论成功预读的文件
    discuss_batch = [r for r in discuss_batch if r not in failed_rels]
    if not discuss_batch:
        print(f"\n[STOP] 本批次所有文件均预读失败（共 {len(failed_rels)} 个），无可讨论内容。")
        return 0
    # 所有文件展示完毕，统一输出讨论提示
    print(f"\n{'='*60}")
    print(f"[DISCUSS 批量预读完成] 以上 {len(discuss_batch)} 个文件已全部展示。")
    if failed_rels:
        print(f"\n注意：以下 {len(failed_rels)} 个文件预读失败，已自动跳过，无需处理：")
        for r in failed_rels:
            print(f"  - {r}")
    print(f"\n请与研究者讨论以下事项：")
    print(f"  1. 每个文件对应的词条结构（slug、title、需新建/合并的 concept/entity）")
    print(f"  2. 跨文件的词条协调（避免重叠、确认消歧需求）")
    print(f"  3. 是否有文件需要跳过（用 --skip 处理）")
    print(f"\n讨论完成后，按任意顺序逐篇执行 finalize：")
    for rel in discuss_batch:
        print(f"  python -m Tools.ingest --finalize <slug> <title> \"{rel}\" --brief \"<摘要>\"")
    print(f"\n  若需跳过某文件：")
    print(f"  python -m Tools.ingest --skip \"<raw_rel>\"")
    print(f"\n每次 finalize 后观察输出信号：")
    print(f"  [DISCUSS_CONTINUE] → 继续为下一个文件执行 --finalize")
    print(f"  [NEEDS_REVIEW]     → 补充缺失词条后重新执行 --finalize")
    print(f"  [STOP]             → 批次全部完成")
    # 输出明确的流控信号，Agent 据此进入等待讨论状态
    print(f"\n[DISCUSS_READY] 预读完成，等待讨论后逐篇执行 --finalize。")
    print(f"{'='*60}\n")
    return 0
if __name__ == "__main__":
    sys.exit(main())
```

---

#### Tools/lint.py

```python
#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import List, Tuple
from Tools.common import (
    REPO_ROOT, WIKI_DIR, RAW_DIR, LOG_FILE, INDEX_FILE,
    read_file, write_file, append_log,
    extract_wikilinks, all_wiki_pages, resolve_wikilink,
    load_allowed_raw_dirs, agent_llm, parse_log_slugs, load_graph_json,
    parse_frontmatter, parse_ingest_records, parse_moved_paths,
    normalize_path_str, is_raw_path,
    EXIT_OK, EXIT_BLOCKED, EXIT_LLM_PENDING,
    _extract_raw_sources_from_frontmatter,  # E: lint.py unify sources parsing 修复：导入常量
)
SEMANTIC_CONTEXT = WIKI_DIR / "_semantic_lint_context.md"
ANNOTATION_RESULT_FILE = WIKI_DIR / "_annotation_check_result.md"
BLIND_SPOT_RESULT_FILE = WIKI_DIR / "_blind_spot_result.md"
def _get_last_ingest_date(raw_rel: str) -> str:
    if not LOG_FILE.exists():
        return ""
    log_text = read_file(LOG_FILE)
    dates = [d for d, rel, _, _ in parse_ingest_records(log_text) if rel == raw_rel]
    return max(dates) if dates else ""
def _build_link_graph() -> dict:
    """一次性扫描所有 wiki 页面，返回 {page_path_str: {"links": [...], "content": str}}。"""
    graph = {}
    for page in all_wiki_pages():
        content = read_file(page)
        graph[str(page)] = {
            "page": page,
            "content": content,
            "links": extract_wikilinks(content),
        }
    return graph
def check_orphan_pages(link_graph: dict) -> list:
    inbound: set = set()
    excluded_stems = {"index", "log", "overview"}
    for entry in link_graph.values():
        for link in entry["links"]:
            if link.startswith("Raw/"):
                continue
            resolved = resolve_wikilink(link)
            if resolved:
                inbound.add(str(resolved))
    issues = []
    for entry in link_graph.values():
        page = entry["page"]
        if page.stem in excluded_stems:
            continue
        rel = page.relative_to(WIKI_DIR).as_posix()
        if rel.startswith("syntheses/") or rel.startswith("sources/"):
            continue
        if str(page.resolve()) not in inbound:
            issues.append(f"孤儿页: {page.relative_to(REPO_ROOT).as_posix()}")
    return issues
def check_stale_syntheses() -> list:
    issues = []
    syntheses_dir = WIKI_DIR / "syntheses"
    if not syntheses_dir.exists():
        return issues
    for page in syntheses_dir.rglob("*.md"):
        content = read_file(page)
        fm = parse_frontmatter(content)
        last_updated = fm.get("last_updated", "")
        if not last_updated:
            continue
        source_links = []
        for raw_src in _extract_raw_sources_from_frontmatter(fm):
            if not raw_src.startswith("Raw/"):
                source_links.append(raw_src)
        raw_paths_set: set = set()
        for link in source_links:
            if is_raw_path(link):
                raw_paths_set.add(link)
            else:
                resolved = resolve_wikilink(link)
                if resolved and resolved.exists():
                    ref_content = read_file(resolved)
                    ref_fm = parse_frontmatter(ref_content)
                    ref_links = []
                    for ref_src in _extract_raw_sources_from_frontmatter(ref_fm):
                        if not ref_src.startswith("Raw/"):
                            ref_links.append(ref_src)
                    for rs in ref_links:
                        if is_raw_path(rs):
                            raw_paths_set.add(rs)
        for raw_rel in raw_paths_set:
            latest_ingest = _get_last_ingest_date(raw_rel)
            if latest_ingest and latest_ingest > last_updated:
                issues.append(
                    f"过时综述: {page.relative_to(REPO_ROOT).as_posix()}"
                    f"（last_updated={last_updated}，但 [[{raw_rel}]]"
                    f" 在 {latest_ingest} 有新摄入）"
                )
                break
    return issues
def check_missing_entities(link_graph: dict) -> list:
    link_count: dict = {}
    entities_dir = WIKI_DIR / "entities"
    existing_entities = {p.stem for p in entities_dir.rglob("*.md")} if entities_dir.exists() else set()
    for entry in link_graph.values():
        for link in set(entry["links"]):
            if link.startswith("Raw/"):
                continue
            if resolve_wikilink(link):
                continue
            stem = Path(link.split("|")[0].strip()).name
            if not stem:
                continue
            link_count[stem] = link_count.get(stem, 0) + 1
    issues = []
    for stem, count in link_count.items():
        if count >= 3 and stem not in existing_entities:
            issues.append(f"缺失实体页: [[{stem}]] 被 {count} 个页面引用但无独立词条")
    return issues
def check_sparse_pages(link_graph: dict) -> list:
    issues = []
    excluded_stems = {"index", "log", "overview"}
    for entry in link_graph.values():
        page = entry["page"]
        if page.stem in excluded_stems:
            continue
        non_raw_links = [l for l in entry["links"] if not l.startswith("Raw/")]
        if len(non_raw_links) < 2:
            issues.append(f"稀疏页: {page.relative_to(REPO_ROOT).as_posix()}（仅 {len(non_raw_links)} 条出站双链）")
    return issues
def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
def check_annotation_missing(pages_with_sources: list,
                             apply_answer_file: str = "",
                             apply_answer_text: str = "") -> Tuple[str, bool]:
    try:
        allowed = load_allowed_raw_dirs()
    except (FileNotFoundError, ValueError) as e:
        return f"加注缺失：无法加载目录配置（{e}），跳过检查。", False
    annotation_map = {d["name"]: d.get("annotation", "") for d in allowed if d.get("annotation")}
    entries = []
    for page, raw_paths, _ in pages_with_sources:
        needed_annotations = set()
        for rp in raw_paths:
            if is_raw_path(rp):
                normalized = rp
            else:
                normalized = "Raw/" + rp.lstrip("/")
            parts = Path(normalized).parts
            if len(parts) >= 2:
                ann = annotation_map.get(parts[1], "")
                if ann:
                    needed_annotations.add(f"（{ann}）")
        if not needed_annotations:
            continue
        content = read_file(page)
        entries.append({
            "page": page.relative_to(REPO_ROOT).as_posix(),
            "expected_annotations": sorted(needed_annotations),
            "sources": raw_paths,
            "content_preview": content[:500],
        })
    if not entries:
        return "加注缺失：无需检查（无来自需要加注目录的词条）。", False
    # 统一基于 entries 序列化计算哈希，保证缓存一致性
    entries_hash = _content_hash(json.dumps(entries, sort_keys=True, ensure_ascii=False))
    result_text = ""
    if apply_answer_file:
        p = Path(apply_answer_file)
        if p.exists():
            result_text = read_file(p).strip()
    if not result_text and apply_answer_text:
        result_text = apply_answer_text.strip()
    if result_text:
        write_file(ANNOTATION_RESULT_FILE, f"# sha256:{entries_hash}\n{result_text}")
        return f"加注缺失检查结果：\n{result_text}", False
    # 检查缓存：读取第一行 sha256 头，比对当前 entries_hash
    if ANNOTATION_RESULT_FILE.exists():
        cached = read_file(ANNOTATION_RESULT_FILE)
        m = re.match(r"^# sha256:([a-f0-9]+)", cached)
        if m and m.group(1) == entries_hash:
            result_text = re.sub(r"^# sha256:.*\n", "", cached).strip()
            return f"加注缺失检查结果（缓存）：\n{result_text}", False
    # 未命中缓存，写入上下文文件并请求 LLM
    context_lines = [
        "# 加注缺失语义检查上下文\n\n",
        "请 Agent 读取以下词条，检查正文中他人观点/推论/主观内容是否已正确加注。\n\n"
    ]
    for e in entries:
        context_lines.append(f"## {e['page']}\n")
        context_lines.append(f"- 期望加注标记（任一或多个）：{', '.join(e['expected_annotations'])}\n")
        context_lines.append(f"- 来源文件：{', '.join(e['sources'])}\n")
        context_lines.append(f"- 内容预览：\n\n{e['content_preview']}\n\n\n")
    full_context = "".join(context_lines)
    write_file(SEMANTIC_CONTEXT, full_context)
    lint_prompt = (
        f"请阅读 Wiki/_semantic_lint_context.md 中列出的 {len(entries)} 个词条，"
        f"检查每个词条正文中来自他人文档的推论、观点、主观内容，"
        f"是否已正确标注对应的加注标记（期望标记见各词条说明）。\n\n"
        f"输出格式：对每个词条，列出缺少加注的具体句子，并建议补充的加注标记。"
        f"若全部合规，输出\"[PASS] 全部合规\"。"
    )
    result = agent_llm(lint_prompt, output_var="ANNOTATION_CHECK_RESULT")
    if result == "[AGENT_PENDING]":
        return (
            f"加注缺失：已将 {len(entries)} 个词条写入 Wiki/_semantic_lint_context.md，"
            f"当前 Agent 正在执行语义检查（见上方 [AGENT_LLM_REQUEST] 输出）。\n"
            f"请完成推理后将结果写入 {ANNOTATION_RESULT_FILE} 或使用 --apply-annotation-check 回传，"
            f"然后重新运行 python -m Tools.lint 以完成审计。"
        ), True
    write_file(ANNOTATION_RESULT_FILE, f"# sha256:{entries_hash}\n{result}")
    return f"加注缺失检查结果：\n{result}", False
def check_slug_conflicts() -> list:
    """检查日志中同一 slug 对应多个不同 Raw 源文件的冲突，使用 move 归一化避免假阳性。"""
    if not LOG_FILE.exists():
        return []
    log_text = read_file(LOG_FILE)
    moved = parse_moved_paths(log_text)
    slug_to_raws: dict = {}
    for _, raw_rel, _, slug in parse_ingest_records(log_text):
        norm = normalize_path_str(raw_rel)
        # 若存在 move 记录，映射到当前路径
        current = moved.get(norm, norm)
        slug_to_raws.setdefault(slug, set()).add(current)
    conflicts = [
        f"slug '{s}' 对应多个不同来源文件: {raws}"
        for s, raws in slug_to_raws.items() if len(raws) > 1
    ]
    return conflicts
def check_blind_spots(apply_answer_file: str = "", apply_answer_text: str = "") -> Tuple[str, bool]:
    if not INDEX_FILE.exists():
        return "知识盲区：index.md 不存在，跳过分析。", False
    index_content = read_file(INDEX_FILE)
    current_hash = _content_hash(index_content)
    result_text = ""
    if apply_answer_file:
        p = Path(apply_answer_file)
        if p.exists():
            result_text = read_file(p).strip()
    if not result_text and apply_answer_text:
        result_text = apply_answer_text.strip()
    if result_text:
        write_file(BLIND_SPOT_RESULT_FILE, f"# sha256:{current_hash}\n{result_text}")
        return f"知识盲区推荐：\n{result_text}", False
    if BLIND_SPOT_RESULT_FILE.exists():
        cached = read_file(BLIND_SPOT_RESULT_FILE)
        m = re.match(r"^# sha256:([a-f0-9]+)", cached)
        if m and m.group(1) == current_hash:
            result_text = re.sub(r"^# sha256:.*\n", "", cached).strip()
            return f"知识盲区推荐（缓存）：\n{result_text}", False
    blind_spot_prompt = (
        f"请阅读以下知识库目录（Wiki/index.md），识别出 3-5 个常见问题可能无法被现有词条覆盖的主题盲区。\n"
        f"对每个盲区，建议 1-3 条具体的 web 搜索查询词（中文），以便研究者补充材料。\n\n"
        f"输出格式（Markdown 列表，无需前言）：\n"
        f"- 盲区主题：搜索建议：查询词A、查询词B\n\n"
        f"--- index.md 内容 ---\n{index_content[:3000]}"
    )
    result = agent_llm(blind_spot_prompt, output_var="BLIND_SPOT_RESULT")
    if result == "[AGENT_PENDING]":
        return (
            "知识盲区：分析请求已发出（见上方 [AGENT_LLM_REQUEST] 输出），"
            f"结果将由 Agent 补充。请完成推理后将结果写入 {BLIND_SPOT_RESULT_FILE} 或使用 --apply-blind-spots 回传，"
            "然后重新运行 python -m Tools.lint 以完成审计。"
        ), True
    write_file(BLIND_SPOT_RESULT_FILE, f"# sha256:{current_hash}\n{result}")
    return f"知识盲区推荐：\n{result}", False
def check_graph_health() -> list:
    graph_data = load_graph_json()
    if not graph_data:
        return []
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", []) + graph_data.get("inferred_edges", [])
    if not nodes:
        return []
    root_special = {"index.md", "log.md", "overview.md"}
    active_nodes = [n for n in nodes if n["id"] not in root_special]
    if not active_nodes:
        return []
    issues = []
    degrees = {n["id"]: 0 for n in active_nodes}
    for e in edges:
        from_id = e.get("from", "")
        to_id = e.get("to", "")
        if from_id in degrees:
            degrees[from_id] += 1
        if to_id in degrees:
            degrees[to_id] += 1
    deg_values = list(degrees.values())
    if len(deg_values) >= 2:
        mu = statistics.mean(deg_values)
        sigma = statistics.stdev(deg_values)
        threshold = mu + 2 * sigma
        for n in active_nodes:
            if degrees.get(n["id"], 0) > threshold:
                issues.append(
                    f"上帝节点: {n['id']}（度数 {degrees[n['id']]}，mu+2sigma={threshold:.1f}）"
                )
                page = resolve_wikilink(n["id"])
                if page and len(read_file(page)) < 500:
                    issues.append(f"枢纽存根: {n['id']}（高度数但内容 < 500 字）")
    contradicts = [e for e in edges if e.get("relation") == "contradicts"]
    if edges and len(contradicts) / len(edges) > 0.15:
        issues.append(
            f"冲突边密度过高: contradicts 边占比 {len(contradicts)/len(edges):.1%}（> 15%）"
        )
    return issues
def run_lint(save: bool = False,
             apply_annotation_check: str = "",
             apply_annotation_text: str = "",
             apply_blind_spots: str = "",
             apply_blind_text: str = "") -> int:
    today = date.today().isoformat()
    print("=" * 60)
    print("LLM Wiki 质量审计报告")
    print("=" * 60)
    try:
        allowed = load_allowed_raw_dirs()
        dir_names = {d["name"] for d in allowed if d.get("ingest", True)}
    except (FileNotFoundError, ValueError) as e:
        print(f"WARN: 无法加载目录配置：{e}")
        dir_names = set()
    pages_with_sources = []
    for page in all_wiki_pages():
        content = read_file(page)
        fm = parse_frontmatter(content)
        raw_paths = list(_extract_raw_sources_from_frontmatter(fm))
        if any(
            is_raw_path(rp)
            and len(Path(rp).parts) >= 2
            and Path(rp).parts[1] in dir_names
            for rp in raw_paths
        ):
            pages_with_sources.append((page, raw_paths, ""))
    link_graph = _build_link_graph()
    checks = {
        "孤儿页": check_orphan_pages(link_graph),
        "过时综述": check_stale_syntheses(),
        "缺失实体页": check_missing_entities(link_graph),
        "稀疏页": check_sparse_pages(link_graph),
        "Slug冲突": check_slug_conflicts(),
        "图谱感知": check_graph_health(),
    }
    annotation_text, annotation_pending = check_annotation_missing(
        pages_with_sources,
        apply_answer_file=apply_annotation_check,
        apply_answer_text=apply_annotation_text,
    )
    blind_spot_text, blind_pending = check_blind_spots(
        apply_answer_file=apply_blind_spots,
        apply_answer_text=apply_blind_text,
    )
    pending_llm = annotation_pending or blind_pending
    report_lines = []
    for category, issues in checks.items():
        status = "[PASS]" if not issues else f"[WARN] {len(issues)} 项"
        print(f"\n[{category}] {status}")
        report_lines.append(f"\n## {category}\n")
        if not issues:
            report_lines.append("[PASS]\n")
        else:
            for issue in issues:
                print(f"  - {issue}")
                report_lines.append(f"- {issue}\n")
    print(f"\n[加注缺失]\n{annotation_text}")
    report_lines.append(f"\n## 加注缺失\n{annotation_text}\n")
    print(f"\n[知识盲区推荐]\n{blind_spot_text}")
    report_lines.append(f"\n## 知识盲区推荐\n{blind_spot_text}\n")
    all_issues = [item for issues in checks.values() for item in issues]
    severe = len(all_issues)
    if pending_llm:
        print("\n" + "=" * 60)
        print("WARN: 语义审计未完成：需要 Agent 处理 LLM 推理请求后重新运行 lint。")
        print("完成推理后请将结果写入对应文件或使用 --apply-* 参数回传，然后再次执行 python -m Tools.lint。")
        print("=" * 60)
        if save:
            report_path = WIKI_DIR / "lint-report.md"
            partial_note = "\n\n## WARN: 本报告不完整\n语义检查（加注缺失/知识盲区）待 Agent 完成推理后重新运行 lint 补充。\n"
            write_file(report_path, f"# 质量审计报告（部分） {today}\n" + "".join(report_lines) + partial_note)
            print(f"\n部分报告已保存至 Wiki/lint-report.md（结构化检查结果已写入，语义检查待补充）")
        return EXIT_LLM_PENDING  # Bug 3 修复：使用常量
    print("\n" + "=" * 60)
    passed = severe == 0
    if passed:
        print("[PASS] 全部通过，知识库质量良好。")
    else:
        print(f"[WARN] 共发现 {severe} 项严重问题，建议处理后重新审计。")
    if severe > 3:
        schema_note = (
            "\nAGENTS.md 演化建议：本次审计发现多项质量问题，"
            "建议与研究者讨论是否修订 AGENTS.md 中的对应条款，"
            "以避免同类问题在后续摄入中反复出现。"
        )
        print(schema_note)
        report_lines.append(f"\n## Schema 演化建议\n{schema_note.strip()}\n")
    print("=" * 60)
    summary = "通过" if passed else f"{severe}项严重问题"
    append_log(f"## [{today}] lint | {summary}")
    if save:
        report_path = WIKI_DIR / "lint-report.md"
        write_file(report_path, f"# 质量审计报告 {today}\n" + "".join(report_lines))
        print(f"\n报告已保存至 Wiki/lint-report.md")
    return EXIT_OK if passed else EXIT_BLOCKED  # Bug 3 修复：使用常量
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Wiki 质量审计")
    parser.add_argument("--save", action="store_true", help="将报告保存至 Wiki/lint-report.md")
    parser.add_argument("--apply-annotation-check", default="", help="回传加注检查结果的文件路径")
    parser.add_argument("--apply-annotation-text", default="", help="直接回传加注检查结果文本")
    parser.add_argument("--apply-blind-spots", default="", help="回传知识盲区推荐结果的文件路径")
    parser.add_argument("--apply-blind-text", default="", help="直接回传知识盲区推荐结果文本")
    args = parser.parse_args()
    sys.exit(run_lint(
        save=args.save,
        apply_annotation_check=args.apply_annotation_check,
        apply_annotation_text=args.apply_annotation_text,
        apply_blind_spots=args.apply_blind_spots,
        apply_blind_text=args.apply_blind_text,
    ))
```

---

#### Tools/query.py

```python
#!/usr/bin/env python3
"""
LLM Wiki 查询工具。
先查 Wiki，盲区回退至 Raw，新洞见自动织网。
退出码约定：与 common.py EXIT_* 常量保持一致。
运行方式：
  python -m Tools.query <问题>
  python -m Tools.query <问题> --save --slug <slug>
  python -m Tools.query --apply --slug <slug> --answer "<答案文本>" [<问题>]
  python -m Tools.query --apply --slug <slug> --answer-file <文件路径> [<问题>]
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional
from Tools.common import (
    REPO_ROOT, WIKI_DIR, RAW_DIR, LOG_FILE, INDEX_FILE,
    PYTHON_BIN, QMD_AVAILABLE, PENDING_QUERY,
    WIKI_SECTION_HEADERS,
    read_file, write_file, append_log,
    extract_wikilinks, all_wiki_pages, resolve_wikilink,
    check_slug_conflict, git_add_commit, agent_llm, load_graph_json,
    qmd_embed_wiki, _run_qmd, parse_frontmatter,
    EXIT_OK, EXIT_NEEDS_REVIEW,
)
MAX_WIKI_HITS = 12
def _search_wiki_index(keywords: list) -> list:
    if not INDEX_FILE.exists():
        return []
    index_text = read_file(INDEX_FILE)
    hits = set()
    for kw in keywords:
        for line in index_text.splitlines():
            if kw.lower() in line.lower():
                m = re.search(r"\[([^\]]*)\]\(([^)]+\.md)\)", line)
                if m:
                    p = WIKI_DIR / m.group(2)
                    if p.exists():
                        hits.add(p.relative_to(REPO_ROOT).as_posix())
    graph_data = load_graph_json()
    if graph_data and hits:
        edges = graph_data.get("edges", []) + graph_data.get("inferred_edges", [])
        neighbor_hits = set()
        for h in list(hits):
            rel = Path(h).relative_to(WIKI_DIR).as_posix()
            for e in edges:
                if e.get("from") == rel:
                    neighbor_p = WIKI_DIR / e["to"]
                    if neighbor_p.exists():
                        neighbor_hits.add(neighbor_p.relative_to(REPO_ROOT).as_posix())
                elif e.get("to") == rel:
                    neighbor_p = WIKI_DIR / e["from"]
                    if neighbor_p.exists():
                        neighbor_hits.add(neighbor_p.relative_to(REPO_ROOT).as_posix())
        all_hits = list(hits) + [h for h in neighbor_hits if h not in hits]
        return all_hits[:MAX_WIKI_HITS]
    return list(hits)[:MAX_WIKI_HITS]
def _strip_qmd_prefix(path: str) -> str:
    return re.sub(r"^qmd://[^/]+/", "", path)
def _search_qmd(question: str, collection: str = "wiki", n: int = 8) -> list:
    if not QMD_AVAILABLE:
        return []
    try:
        result = _run_qmd(
            ["query", question, "--collection", collection,
             "--format", "json", "-n", str(n)],
            cwd=REPO_ROOT, capture_output=True, text=False, timeout=30
        )
        if result.returncode == 0:
            raw = result.stdout
            # 处理 BOM 和编码问题
            for enc in ("utf-8-sig", "utf-8", "utf-16"):
                try:
                    data = json.loads(raw.decode(enc))
                    return [
                        _strip_qmd_prefix(item.get("file", ""))
                        for item in data if item.get("file")
                    ]
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
    except Exception:
        pass
    return []
def _save_synthesis(question: str, answer: str, slug: str,
                    source_hits: Optional[List[str]] = None,
                    update: bool = False) -> int:
    synth_path = WIKI_DIR / "syntheses" / f"{slug}.md"
    is_existing_synthesis = synth_path.exists()
    if is_existing_synthesis and not update:
        print(
            f"[NEEDS_REVIEW] 综述页 syntheses/{slug}.md 已存在。\n"
            f"若希望更新该综述（例如本次查询是对同一主题的补充或修订），"
            f"请在命令中追加 --update 参数并重新执行 --apply；\n"
            f"若这是一个不同的问题，请改用新的 --slug。"
        )
        return EXIT_NEEDS_REVIEW
    if not is_existing_synthesis:
        conflict, existing = check_slug_conflict(slug, raw_rel=None)
        if conflict:
            print(f"[NEEDS_REVIEW] slug 冲突：{slug}.md 已存在于其他词条类型（来源：{existing}）。\n"
                  f"综述页 slug 须全局唯一，请指定新的 slug。")
            return EXIT_NEEDS_REVIEW
    today = date.today().isoformat()
    escaped_title = (
        question[:80]
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
    )
    sources_list: List[str] = []
    if source_hits:
        for h in source_hits:
            link = f"[[{h}]]" if not h.startswith("[[") else h
            sources_list.append(link)
    if is_existing_synthesis and update:
        old_content = read_file(synth_path)
        old_fm = parse_frontmatter(old_content)
        old_sources_val = old_fm.get("sources", [])
        if isinstance(old_sources_val, list):
            old_sources = [str(item) for item in old_sources_val if isinstance(item, str)]
        else:
            # 如果是字符串，尝试提取双链
            old_sources = extract_wikilinks(old_sources_val) if isinstance(old_sources_val, str) else []
        # 合并去重
        merged_sources = list(dict.fromkeys(old_sources + sources_list))
        status = old_fm.get("status", "open")
        open_questions = old_fm.get("open_questions", [])
        content = (
            f"---\n"
            f"title: \"{escaped_title}\"\n"
            f"type: synthesis\n"
            f"tags: []\n"
            f"sources: {json.dumps(merged_sources, ensure_ascii=False)}\n"
            f"status: {status}\n"
            f"open_questions: {json.dumps(open_questions, ensure_ascii=False)}\n"
            f"last_updated: {today}\n"
            f"---\n\n"
            f"## 结论\n\n{answer}\n\n"
            f"## 论据与引用\n"
            f"<!-- 请 Agent 补充引用词条的 [[wikilink]] 并加注 （据查询合成，未经来源验证）-->\n"
        )
        write_file(synth_path, content)
        append_log(f"## [{today}] query-synthesis-update | {question[:80]} | slug:{slug}")
        git_add_commit([synth_path, LOG_FILE], f"query-synthesis-update: {question[:60]}")
        qmd_embed_wiki()
        print(f"OK: 已更新 Wiki/syntheses/{slug}.md（sources 已合并去重，原 status/open_questions 已保留）")
        return 0
    # 新建模式
    content = (
        f"---\n"
        f"title: \"{escaped_title}\"\n"
        f"type: synthesis\n"
        f"tags: []\n"
        f"sources: {json.dumps(sources_list, ensure_ascii=False)}\n"
        f"status: open\n"
        f"open_questions: []\n"
        f"last_updated: {today}\n"
        f"---\n\n"
        f"## 结论\n\n{answer}\n\n"
        f"## 论据与引用\n"
        f"<!-- 请 Agent 补充引用词条的 [[wikilink]] 并加注 （据查询合成，未经来源验证）-->\n"
    )
    synth_dir = WIKI_DIR / "syntheses"
    synth_dir.mkdir(exist_ok=True)
    write_file(synth_dir / f"{slug}.md", content)
    if INDEX_FILE.exists():
        idx = read_file(INDEX_FILE)
        link_line = f"- [{escaped_title[:60]}](syntheses/{slug}.md)\n"
        syntheses_header = WIKI_SECTION_HEADERS.get("syntheses", "## Syntheses")
        if syntheses_header in idx and f"syntheses/{slug}.md" not in idx:
            pos = idx.index(syntheses_header) + len(syntheses_header)
            next_sec = idx.find("\n## ", pos)
            if next_sec == -1:
                if not idx.endswith("\n"):
                    idx += "\n"
                idx += link_line
            else:
                idx = idx[:next_sec] + "\n" + link_line + idx[next_sec:]
            write_file(INDEX_FILE, idx)
    append_log(f"## [{today}] query-synthesis | {question[:80]} | slug:{slug}")
    git_add_commit(
        [INDEX_FILE, LOG_FILE, synth_dir / f"{slug}.md"],
        f"query-synthesis: {question[:60]}"
    )
    qmd_embed_wiki()
    print(f"OK: 已归档至 Wiki/syntheses/{slug}.md")
    return 0
def run_query(question: str, save: bool = False, slug: str = "",
              apply_answer: str = "",
              qmd_hits_file: str = "",
              source_hits: Optional[List[str]] = None,
              update: bool = False) -> int:
    if apply_answer and slug:
        return _save_synthesis(question, apply_answer, slug, source_hits=source_hits, update=update)
    print(f"\n查询: {question}\n")
    keywords = [kw for kw in re.split(r"[\s，,]+", question) if kw]
    synth_dir = WIKI_DIR / "syntheses"
    open_questions = []
    if synth_dir.exists():
        for p in synth_dir.rglob("*.md"):
            content = read_file(p)
            if re.search(r"^status:\s*open", content, re.MULTILINE):
                open_questions.append(p.relative_to(REPO_ROOT).as_posix())
    if open_questions:
        print(f"INFO: 已知开放问题（共 {len(open_questions)} 个）：")
        for oq in open_questions[:5]:
            print(f"  - {oq}")
    wiki_hits: list = []
    if qmd_hits_file:
        hits_path = Path(qmd_hits_file)
        if hits_path.exists():
            raw_text = ""
            # 尝试多种编码，包括带BOM的
            for enc in ("utf-8-sig", "utf-8", "utf-16"):
                try:
                    raw_text = hits_path.read_text(encoding=enc)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            if not raw_text:
                print("WARN: 无法读取 qmd 命中文件编码，降级至内部检索")
            else:
                try:
                    raw = json.loads(raw_text)
                    if raw and isinstance(raw[0], dict):
                        candidates = [_strip_qmd_prefix(item.get("file", "")) for item in raw if item.get("file")]
                    else:
                        candidates = raw
                    wiki_hits = [h for h in candidates if h and (REPO_ROOT / h).exists()]
                    if wiki_hits:
                        print(f"INFO: 使用外部 qmd 检索结果（{len(wiki_hits)} 个命中）")
                    else:
                        print("INFO: 外部 qmd 结果为空，降级至内部检索")
                except Exception as e:
                    print(f"WARN: 读取 qmd 命中文件失败（{e}），降级至内部检索")
        else:
            print(f"WARN: qmd 命中文件不存在（{qmd_hits_file}），降级至内部检索")
    if not wiki_hits:
        if QMD_AVAILABLE:
            wiki_hits = _search_qmd(question, "wiki", 8)
            if not wiki_hits:
                print("WARN: qmd 检索无命中，降级至 index.md 关键词匹配")
                wiki_hits = _search_wiki_index(keywords)
        else:
            print("WARN: qmd 不可用，使用 index.md 关键词匹配")
            wiki_hits = _search_wiki_index(keywords)
    if wiki_hits:
        print(f"\nOK: Wiki 层命中 {len(wiki_hits)} 个词条：")
        for h in wiki_hits:
            print(f"  - {h}")
        print("\n请 Agent 自行使用文件读取工具查看上述文件内容，综合分析后给出答案。")
    else:
        print("WARN: Wiki 层无命中，回退至 Raw 层检索。")
        raw_hits = []
        qmd_raw_hits = []
        if QMD_AVAILABLE:
            qmd_raw_hits = _search_qmd(question, "raw", 8)
        if qmd_raw_hits:
            raw_hits = qmd_raw_hits
        else:
            SEARCHABLE_EXTS = {".md", ".txt"}
            for f in RAW_DIR.rglob("*"):
                if not f.is_file() or f.suffix.lower() not in SEARCHABLE_EXTS:
                    continue
                content = read_file(f)
                if any(kw.lower() in content.lower() for kw in keywords):
                    raw_hits.append(f.relative_to(REPO_ROOT).as_posix())
        if not raw_hits:
            other_raw = [
                f.relative_to(REPO_ROOT).as_posix()
                for f in RAW_DIR.rglob("*")
                if f.is_file() and f.suffix.lower() in {".pdf", ".docx", ".pptx", ".xlsx", ".epub"}
            ]
            if other_raw:
                print(f"INFO: Raw 层另有 {len(other_raw)} 个非文本文件无法关键词搜索（建议安装 qmd 以启用语义检索）")
                for of in other_raw[:3]:
                    print(f"  - {of}")
        if raw_hits:
            print(f"\nWARN: Raw 层命中 {len(raw_hits)} 个文件（知识盲区，Wiki 覆盖不足）：")
            for rh in raw_hits[:5]:
                print(f"  - {rh}")
            print("\n是否立即对上述文件执行 ingest 以填补盲区？")
            print("请 Agent 自行读取 Raw 文件内容作答，末尾附注知识盲区警告。")
        else:
            print("WARN: Wiki 和 Raw 层均无命中。\n该主题存在知识盲区，建议补充原始笔记至 Raw/ 后重新查询。")
    if save:
        if not slug:
            print("\nWARN: --save 需要提供 --slug 参数。")
            return 1
        existing_synth = (WIKI_DIR / "syntheses" / f"{slug}.md").exists()
        if existing_synth and not update:
            print(
                f"\nWARN: 综述页 syntheses/{slug}.md 已存在。"
                f"若要更新该综述，请追加 --update 参数；否则请更换 --slug。"
            )
            return 2
        answer_prompt = (
            f"问题：{question}\n"
            f"命中文件路径：{wiki_hits}\n"
            f"请自行读取这些文件内容，生成一个结构化的答案。"
        )
        answer = agent_llm(answer_prompt, output_var="SYNTHESIS_ANSWER")
        if answer == "[AGENT_PENDING]":
            pending_data = {
                "question": question,
                "slug": slug,
                "hit_paths": wiki_hits,
                "update": update,
                "timestamp": date.today().isoformat()
            }
            write_file(PENDING_QUERY, json.dumps(pending_data, ensure_ascii=False, indent=2))
            escaped_question = question[:80].replace('"', '\\"')
            update_flag = " --update" if update else ""
            print("\nWARN: 答案将由当前 Agent 生成。Agent 完成推理后，请执行：\n"
                  f"  python -m Tools.query \"{escaped_question}\" --apply --slug {slug} --answer \"<答案>\"{update_flag}\n"
                  f"  或写入文件后：python -m Tools.query --apply --slug {slug} --answer-file <路径>{update_flag}\n")
            return 0
        return _save_synthesis(question, answer, slug, source_hits=wiki_hits, update=update)
    else:
        print(f"\nINFO: 是否将本次答案归档为综述页？\n"
              f"（说 'query: {question} --save --slug <中文短语>' 触发归档；"
              f"若该 slug 已存在综述，追加 --update 以更新）")
    return 0
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Wiki 查询工具")
    parser.add_argument("question", nargs="?", default="", help="查询问题")
    parser.add_argument("--save", action="store_true", help="将答案归档至 Wiki/syntheses/")
    parser.add_argument("--slug", default="", help="归档 slug（2-6 字中文短语）")
    parser.add_argument("--update", action="store_true",
                        help="允许覆盖更新已存在的同名综述页（sources 自动合并去重，"
                             "保留原 status/open_questions）")
    parser.add_argument("--apply", action="store_true", help="应用已生成的答案（配合 --answer 使用）")
    parser.add_argument("--answer", default="", help="Agent 生成的答案文本")
    parser.add_argument("--answer-file", default="",
                        help="从文件读取答案文本（替代 --answer，避免 shell 转义问题）")
    parser.add_argument("--qmd-hits", default="", dest="qmd_hits",
                        help="外部 qmd 检索结果文件路径（JSON 数组）")
    args = parser.parse_args()
    if args.apply:
        answer_text = args.answer
        if args.answer_file:
            try:
                answer_text = Path(args.answer_file).read_text(encoding="utf-8")
            except Exception as e:
                print(f"WARN: 读取 --answer-file 失败（{e}）")
                sys.exit(1)
        if not answer_text or not args.slug:
            print("WARN: --apply 需要同时提供 --slug 和 --answer 或 --answer-file")
            sys.exit(1)
        pending_data = {}
        if PENDING_QUERY.exists():
            try:
                pending_data = json.loads(PENDING_QUERY.read_text(encoding="utf-8"))
            except Exception:
                pass
        question = args.question or pending_data.get("question", "")
        if not question:
            print("WARN: 未能获取原始问题文本，综述标题将降级为 slug: {args.slug}。")
            question = args.slug
        source_hits = pending_data.get("hit_paths", [])
        if pending_data and not source_hits:
            print("WARN: pending 文件中无 hit_paths 记录，综述的 sources 字段将为空。")
        update_flag = args.update or bool(pending_data.get("update", False))
        sys.exit(run_query(question, save=True, slug=args.slug,
                           apply_answer=answer_text, source_hits=source_hits,
                           update=update_flag))
    if not args.question:
        print("WARN: 请提供查询问题，例如：python -m Tools.query '什么是纯粹理性批判'")
        sys.exit(1)
    sys.exit(run_query(args.question, save=args.save, slug=args.slug, update=args.update,
                       qmd_hits_file=args.qmd_hits))
```

---

#### Tools/build_graph.py

```python
#!/usr/bin/env python3
from __future__ import annotations
"""
Build the knowledge graph from the wiki.
Usage:
    python tools/build_graph.py               # full rebuild (with Agent-assisted inference)
    python tools/build_graph.py --no-infer    # skip semantic inference (faster)
    python tools/build_graph.py --open        # open graph.html in browser after build
    python tools/build_graph.py --apply-inferred  # merge previously inferred edges
Outputs:
    graph/graph.json    — node/edge data (cached by SHA256)
    graph/graph.html    — interactive vis.js visualization
    graph/graph-report.md — optional health report
Edge types:
    EXTRACTED   — explicit [[wikilink]] in a page
    INFERRED    — Agent-detected implicit relationship
    AMBIGUOUS   — low-confidence inferred relationship
"""
import re
import json
import argparse
import statistics
import hashlib
import webbrowser
from pathlib import Path
from datetime import date
import sys
try:
    import networkx as nx
    from networkx.algorithms import community as nx_community
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: networkx not installed. Community detection disabled. Run: pip install networkx", file=sys.stderr)
from Tools.common import (
    REPO_ROOT, WIKI_DIR, LOG_FILE, GRAPH_DIR,
    read_file, write_file, append_log, init_env, ensure_utf8,
    extract_wikilinks, all_wiki_pages, agent_llm,
)
GRAPH_JSON = GRAPH_DIR / "graph.json"
GRAPH_HTML = GRAPH_DIR / "graph.html"
CACHE_FILE = GRAPH_DIR / ".cache.json"
INFERRED_EDGES_FILE = GRAPH_DIR / ".inferred_edges.jsonl"
CONTEXT_FILE = GRAPH_DIR / ".infer-context.json"
RESULTS_FILE = GRAPH_DIR / ".infer-results.json"
# Node type → color mapping
TYPE_COLORS = {
    "source": "#4CAF50",
    "entity": "#2196F3",
    "concept": "#FF9800",
    "synthesis": "#9C27B0",
    "unknown": "#9E9E9E",
}
EDGE_COLORS = {
    "EXTRACTED": "#555555",
    "INFERRED": "#FF5722",
    "AMBIGUOUS": "#BDBDBD",
}
COMMUNITY_COLORS = [
    "#E91E63", "#00BCD4", "#8BC34A", "#FF5722", "#673AB7",
    "#FFC107", "#009688", "#F44336", "#3F51B5", "#CDDC39",
]
def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
def extract_frontmatter_type(content: str) -> str:
    match = re.search(r'^type:\s*(\S+)', content, re.MULTILINE)
    return match.group(1).strip('"\'') if match else "unknown"
def page_id(path: Path) -> str:
    return path.relative_to(WIKI_DIR).as_posix().replace(".md", "")
def edge_id(src: str, target: str, edge_type: str) -> str:
    return f"{src}->{target}:{edge_type}"
def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return {}
    return {}
def save_cache(cache: dict):
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
def build_nodes(pages: list[Path]) -> list[dict]:
    nodes = []
    for p in pages:
        content = read_file(p)
        node_type = extract_frontmatter_type(content)
        title_match = re.search(r'^title:\s*"?([^"\n]+)"?', content, re.MULTILINE)
        label = title_match.group(1).strip() if title_match else p.stem
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL)
        preview_lines = [line.strip() for line in body.splitlines() if line.strip()]
        preview = " ".join(preview_lines[:3])[:220]
        nodes.append({
            "id": page_id(p),
            "label": label,
            "type": node_type,
            "color": TYPE_COLORS.get(node_type, TYPE_COLORS["unknown"]),
            "path": str(p.relative_to(REPO_ROOT)),
            "markdown": content,
            "preview": preview,
        })
    return nodes
def _parse_relation_annotations(content: str) -> dict[str, str]:
    VALID_RELATIONS = {"supports", "contradicts", "extends", "depends_on"}
    result: dict[str, str] = {}
    in_related = False
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'^related\s*:', stripped):
            in_related = True
            continue
        if in_related:
            if stripped and not stripped.startswith('-') and ':' in stripped and not stripped.startswith('#'):
                break
            m = re.search(r'\[\[([^\]]+)\]\].*?#\s*(\w+)', stripped)
            if m:
                target_raw = m.group(1).strip().removeprefix('Wiki/').removesuffix('.md')
                rel = m.group(2).lower()
                if rel in VALID_RELATIONS:
                    result[target_raw] = rel
    return result
def build_extracted_edges(pages: list[Path]) -> list[dict]:
    stem_map = {p.stem.lower(): page_id(p) for p in pages}
    path_map = {page_id(p).lower(): page_id(p) for p in pages}
    edges = []
    seen = set()
    for p in pages:
        content = read_file(p)
        src = page_id(p)
        relation_annotations = _parse_relation_annotations(content)
        for link in extract_wikilinks(content):
            normalized = link.lower().replace('\\', '/')
            if normalized.startswith('wiki/'):
                normalized = normalized[5:]
            if normalized.startswith('raw/'):
                continue
            normalized_no_ext = normalized.removesuffix('.md')
            target = stem_map.get(normalized_no_ext) or path_map.get(normalized_no_ext)
            if target and target != src:
                key = (src, target)
                if key not in seen:
                    seen.add(key)
                    rel = relation_annotations.get(normalized_no_ext, "link")
                    edges.append({
                        "id": edge_id(src, target, "EXTRACTED"),
                        "from": src,
                        "to": target,
                        "type": "EXTRACTED",
                        "relation": rel,
                        "color": EDGE_COLORS["EXTRACTED"],
                        "confidence": 1.0,
                    })
    return edges
def load_checkpoint() -> tuple[list[dict], set[str]]:
    edges = []
    completed = set()
    if INFERRED_EDGES_FILE.exists():
        for line in INFERRED_EDGES_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                completed.add(record["page_id"])
                for edge in record.get("edges", []):
                    if not isinstance(edge, dict) or "from" not in edge or "to" not in edge:
                        continue
                    rel_type = edge.get("type", "INFERRED")
                    edges.append({
                        "id": edge.get("id", edge_id(edge["from"], edge["to"], rel_type)),
                        "from": edge["from"],
                        "to": edge["to"],
                        "type": rel_type,
                        "title": edge.get("title", edge.get("relationship", "")),
                        "label": edge.get("label", ""),
                        "color": edge.get("color", EDGE_COLORS.get(rel_type, EDGE_COLORS["INFERRED"])),
                        "confidence": float(edge.get("confidence", 0.7)),
                    })
            except (json.JSONDecodeError, KeyError):
                continue
    return edges, completed
def append_checkpoint(page_id_str: str, edges: list[dict]):
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    record = {"page_id": page_id_str, "edges": edges, "ts": date.today().isoformat()}
    with open(INFERRED_EDGES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
# ── Bug 6 修复：build_inferred_edges 返回 (edges, is_complete) ──
def build_inferred_edges(pages: list[Path], existing_edges: list[dict], cache: dict, resume: bool = True) -> tuple[list[dict], bool]:
    """
    返回 (edges, is_complete)。
    修复 Bug 6：原实现挂起时只 return edges，调用方无法区分
    "推断完整完成" 和 "推断因 Agent 异步推理被中断、仅含缓存边" 两种情况。
    """
    checkpoint_edges, completed_ids = load_checkpoint() if resume else ([], set())
    new_edges = list(checkpoint_edges)
    changed_pages = []
    for p in pages:
        pid = page_id(p)
        if pid in completed_ids:
            continue
        content = read_file(p)
        h = sha256(content)
        entry = cache.get(str(p))
        if isinstance(entry, dict) and entry.get("hash") == h:
            for rel in entry.get("edges", []):
                rel_type = rel.get("type", "INFERRED")
                confidence = float(rel.get("confidence", 0.7))
                new_edges.append({
                    "id": edge_id(pid, rel["to"], rel_type),
                    "from": pid, "to": rel["to"], "type": rel_type,
                    "title": rel.get("relationship", ""), "label": "",
                    "color": EDGE_COLORS.get(rel_type, EDGE_COLORS["INFERRED"]),
                    "confidence": confidence,
                })
        else:
            changed_pages.append(p)
    if not changed_pages:
        print("  no changed pages — skipping semantic inference")
        return new_edges, True   # 完整：没有待推断的新页面
    print(f"  inferring relationships for {len(changed_pages)} pages (global inference)...")
    context_nodes = []
    for p in pages:
        content = read_file(p)
        pid = page_id(p)
        fm_type = extract_frontmatter_type(content)
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL)
        context_nodes.append({"id": pid, "type": fm_type, "preview": body[:500].strip()})
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps({"nodes": context_nodes}, indent=2), encoding="utf-8")
    node_list = "\n".join(f"- {n['id']} ({n['type']})" for n in context_nodes)
    prompt = f"""Analyze the following wiki pages and infer implicit semantic relationships between them.
Pages:
{node_list}
For each page, identify up to 3 significant relationships to other pages that are NOT already captured by explicit wikilinks. Return a JSON object with an "edges" array, each edge having fields:
  - "from": source page id
  - "to": target page id
  - "relationship": a one-line description of the relationship
  - "confidence": a number between 0 and 1 (>=0.7 for INFERRED, <0.7 for AMBIGUOUS)
  - "type": either "INFERRED" or "AMBIGUOUS" (optional, will be inferred from confidence)
Output strictly valid JSON only (no markdown). Example:
{{
  "edges": [
    {{"from": "concepts/ConceptA", "to": "concepts/ConceptB", "relationship": "provides foundation for", "confidence": 0.85}},
    ...
  ]
}}
"""
    raw = agent_llm(prompt, output_var="INFERRED_EDGES")
    if raw == "[AGENT_PENDING]":
        print(f"\nPass 2（语义推断）已挂起：已生成 Graph/.infer-context.json（{len(context_nodes)} 个节点）。")
        print("请完成推理后将结果（JSON）写入 Graph/.infer-results.json，然后运行：")
        print("  python -m Tools.build_graph --apply-inferred")
        return new_edges, False   # ── 修复 Bug 6：明确标记不完整 ──
    try:
        clean = re.sub(r"^```(?:json)?\s*", "", raw)
        clean = re.sub(r"\s*```$", "", clean)
        data = json.loads(clean)
        inferred_edges = data.get("edges", [])
    except Exception as e:
        print(f"WARN: 推断结果解析失败: {e}")
        return new_edges, False   # 解析失败同样视为不完整
    node_ids = {page_id(p) for p in pages}
    valid_edges = []
    for e in inferred_edges:
        if e.get("from") in node_ids and e.get("to") in node_ids:
            confidence = float(e.get("confidence", 0.7))
            rel_type = e.get("type", "INFERRED" if confidence >= 0.7 else "AMBIGUOUS")
            valid_edges.append({
                "id": edge_id(e["from"], e["to"], rel_type),
                "from": e["from"], "to": e["to"], "type": rel_type,
                "title": e.get("relationship", ""), "label": "",
                "color": EDGE_COLORS.get(rel_type, EDGE_COLORS["INFERRED"]),
                "confidence": confidence,
            })
    from_edges = {}
    for ve in valid_edges:
        from_edges.setdefault(ve["from"], []).append(ve)
    for pid, edges_list in from_edges.items():
        page_path = next((p for p in pages if page_id(p) == pid), None)
        if page_path:
            content = read_file(page_path)
            h = sha256(content)
            rels = [{"to": e["to"], "relationship": e.get("title", ""),
                    "confidence": e["confidence"], "type": e["type"]} for e in edges_list]
            cache[str(page_path)] = {"hash": h, "edges": rels}
            append_checkpoint(pid, edges_list)
    new_edges.extend(valid_edges)
    print(f"  inferred {len(valid_edges)} edges from Agent.")
    return new_edges, True
def deduplicate_edges(edges: list[dict]) -> list[dict]:
    best = {}
    for e in edges:
        a, b = e["from"], e["to"]
        key = (min(a, b), max(a, b))
        existing = best.get(key)
        if not existing or e.get("confidence", 0) > existing.get("confidence", 0):
            best[key] = e
    deduped = []
    for edge in best.values():
        rel_type = edge.get("type", "INFERRED")
        edge["id"] = edge.get("id", edge_id(edge["from"], edge["to"], rel_type))
        edge["color"] = edge.get("color", EDGE_COLORS.get(rel_type, EDGE_COLORS["INFERRED"]))
        edge["confidence"] = float(edge.get("confidence", 0.7 if rel_type != "EXTRACTED" else 1.0))
        edge.setdefault("title", "")
        edge.setdefault("label", "")
        deduped.append(edge)
    return deduped
def detect_communities(nodes: list[dict], edges: list[dict]) -> dict[str, int]:
    if not HAS_NETWORKX:
        return {}
    G = nx.Graph()
    for n in nodes:
        G.add_node(n["id"])
    for e in edges:
        G.add_edge(e["from"], e["to"])
    if G.number_of_edges() == 0:
        return {}
    try:
        communities = nx_community.louvain_communities(G, seed=42)
        node_to_community = {}
        for i, comm in enumerate(communities):
            for node in comm:
                node_to_community[node] = i
        return node_to_community
    except Exception:
        return {}
def render_html(nodes: list[dict], edges: list[dict]) -> str:
    nodes_json = json.dumps(nodes, indent=2, ensure_ascii=False)
    edges_json = json.dumps(edges, indent=2, ensure_ascii=False)
    legend_items = "".join(
        f'<span style="background:{color};padding:3px 8px;margin:2px;border-radius:3px;font-size:12px">{t}</span>'
        for t, color in TYPE_COLORS.items() if t != "unknown"
    )
    n_extracted = len([e for e in edges if e.get('type') == 'EXTRACTED'])
    n_inferred = len([e for e in edges if e.get('type') == 'INFERRED'])
    n_ambiguous = len([e for e in edges if e.get('type') == 'AMBIGUOUS'])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LLM Wiki — Knowledge Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin: 0; background: #1a1a2e; font-family: 'Inter', sans-serif; color: #eee; }}
  #graph {{ width: 100vw; height: 100vh; }}
  #controls {{
    position: fixed; top: 10px; left: 10px; background: rgba(10,10,30,0.88);
    padding: 14px; border-radius: 10px; z-index: 10; max-width: 280px;
    backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.08);
  }}
  #controls h3 {{ margin: 0 0 10px; font-size: 15px; letter-spacing: 0.5px; }}
  #search {{ width: 100%; padding: 6px 8px; margin-bottom: 10px; background: #222; color: #eee; border: 1px solid #444; border-radius: 6px; font-size: 13px; }}
  #controls p {{ margin: 10px 0 0; font-size: 11px; color: #9ea3b0; line-height: 1.5; }}
  .filter-group {{ margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); }}
  .filter-group label {{ display: block; font-size: 12px; color: #bbb; margin-bottom: 4px; }}
  .slider-row {{ display: flex; align-items: center; gap: 8px; margin-top: 4px; }}
  .slider-row input[type=range] {{ flex: 1; accent-color: #FF5722; }}
  .slider-val {{ font-size: 12px; color: #FF5722; min-width: 28px; text-align: right; font-weight: bold; }}
  .cb-row {{ display: flex; align-items: center; gap: 6px; font-size: 12px; margin: 3px 0; cursor: pointer; }}
  .cb-row input {{ accent-color: #FF5722; }}
  #drawer {{
    position: fixed; top: 0; right: 0; width: clamp(480px, 33vw, 720px); max-width: 100vw; height: 100vh;
    background: rgba(7, 10, 24, 0.96); border-left: 1px solid rgba(255,255,255,0.08);
    box-shadow: -18px 0 36px rgba(0,0,0,0.35); z-index: 20; display: none;
    flex-direction: column; backdrop-filter: blur(10px);
  }}
  #drawer.open {{ display: flex; }}
  #drawer-header {{
    padding: 18px 18px 12px; border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  #drawer-topline {{
    display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  }}
  #drawer-title {{ margin: 0; font-size: 20px; line-height: 1.2; }}
  #drawer-close {{
    background: transparent; color: #9ea3b0; border: 0; font-size: 24px; line-height: 1;
    cursor: pointer; padding: 0;
  }}
  #drawer-meta {{ margin-top: 8px; font-size: 12px; color: #9ea3b0; }}
  #drawer-path {{ margin-top: 6px; font-size: 12px; color: #72788a; word-break: break-all; }}
  #drawer-preview {{
    margin-top: 12px; font-size: 13px; color: #d7d9e0; line-height: 1.6;
  }}
  #drawer-related {{
    padding: 12px 18px 0; font-size: 12px; color: #9ea3b0;
  }}
  #drawer-related-list {{
    display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;
  }}
  .related-chip {{
    background: rgba(255,255,255,0.08); color: #f1f2f7; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px; font-size: 12px; padding: 5px 10px; cursor: pointer;
  }}
  #drawer-content {{
    flex: 1; min-height: 0; padding: 14px 18px 18px; overflow: auto;
  }}
  #drawer-markdown {{
    color: #e6e8ef; font-size: 13px; line-height: 1.72;
  }}
  #drawer-markdown h1, #drawer-markdown h2, #drawer-markdown h3,
  #drawer-markdown h4, #drawer-markdown h5, #drawer-markdown h6 {{
    margin: 1.2em 0 0.55em; line-height: 1.3; color: #fff;
  }}
  #drawer-markdown h1 {{ font-size: 24px; }}
  #drawer-markdown h2 {{ font-size: 20px; }}
  #drawer-markdown h3 {{ font-size: 17px; }}
  #drawer-markdown p {{ margin: 0 0 0.95em; }}
  #drawer-markdown ul, #drawer-markdown ol {{ margin: 0 0 1em 1.35em; padding: 0; }}
  #drawer-markdown li {{ margin: 0.35em 0; }}
  #drawer-markdown hr {{ border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.2em 0; }}
  #drawer-markdown blockquote {{
    margin: 0 0 1em; padding: 0.85em 1em; border-left: 3px solid rgba(101, 181, 255, 0.8);
    background: rgba(255,255,255,0.04); color: #d7d9e0; border-radius: 0 10px 10px 0;
  }}
  #drawer-markdown pre {{
    margin: 0 0 1em; white-space: pre-wrap; word-break: break-word; line-height: 1.55;
    font-size: 12px; color: #e6e8ef; background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 16px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }}
  #drawer-markdown code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.92em; background: rgba(255,255,255,0.08); padding: 0.16em 0.38em;
    border-radius: 6px; color: #ffde91;
  }}
  #drawer-markdown pre code {{ background: transparent; padding: 0; color: inherit; border-radius: 0; }}
  #drawer-markdown .wikilink {{ color: #86c8ff; font-weight: 600; }}
  @media (max-width: 960px) {{
    #drawer {{ width: 100vw; }}
  }}
  #stats {{
    position: fixed; top: 10px; right: 10px; background: rgba(10,10,30,0.88);
    padding: 10px 14px; border-radius: 10px; font-size: 12px;
    backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.08);
  }}
</style>
</head>
<body>
<div id="controls">
  <h3>LLM Wiki Graph</h3>
  <input id="search" type="text" placeholder="Search nodes..." oninput="searchNodes(this.value)">
  <div>{legend_items}</div>
  <div class="filter-group">
    <label>Edge Types</label>
    <div class="cb-row"><input type="checkbox" id="cb-extracted" checked onchange="applyFilters()"><span style="color:#888">━</span> Extracted ({n_extracted})</div>
    <div class="cb-row"><input type="checkbox" id="cb-inferred" checked onchange="applyFilters()"><span style="color:#FF5722">━</span> Inferred ({n_inferred})</div>
    <div class="cb-row"><input type="checkbox" id="cb-ambiguous" onchange="applyFilters()"><span style="color:#BDBDBD">━</span> Ambiguous ({n_ambiguous})</div>
  </div>
  <div class="filter-group">
    <label>Min Confidence</label>
    <div class="slider-row">
      <input type="range" id="conf-slider" min="0" max="100" value="50" oninput="applyFilters()">
      <span class="slider-val" id="conf-val">0.50</span>
    </div>
  </div>
  <p>Click a node to highlight its connected neighbors and view the markdown on the right. Click the background to restore the full graph.</p>
</div>
<div id="graph"></div>
<aside id="drawer">
  <div id="drawer-header">
    <div id="drawer-topline">
      <h2 id="drawer-title"></h2>
      <button id="drawer-close" onclick="clearSelection()" aria-label="Close drawer">×</button>
    </div>
    <div id="drawer-meta"></div>
    <div id="drawer-path"></div>
    <div id="drawer-preview"></div>
  </div>
  <div id="drawer-related">
    Related nodes
    <div id="drawer-related-list"></div>
  </div>
  <div id="drawer-content">
    <div id="drawer-markdown"></div>
  </div>
</aside>
<div id="stats"></div>
<script>
const originalNodes = {nodes_json};
const originalEdges = {edges_json}.map(edge => ({{
  ...edge,
  id: edge.id || `${{edge.from}}->${{edge.to}}:${{edge.type || "INFERRED"}}`,
}}));
const nodes = new vis.DataSet(originalNodes);
const edges = new vis.DataSet(originalEdges);
const adjacency = new Map();
const searchInput = document.getElementById("search");
const stats = document.getElementById("stats");
const controls = {{
  extracted: document.getElementById("cb-extracted"),
  inferred: document.getElementById("cb-inferred"),
  ambiguous: document.getElementById("cb-ambiguous"),
  confSlider: document.getElementById("conf-slider"),
  confValue: document.getElementById("conf-val"),
}};
const nodeMap = new Map(originalNodes.map(node => [node.id, node]));
let activeNodeId = null;
function hexToRgba(color, alpha) {{
  if (!color) return `rgba(255, 255, 255, ${{alpha}})`;
  const normalized = color.replace("#", "");
  const value = normalized.length === 3
    ? normalized.split("").map(ch => ch + ch).join("")
    : normalized;
  const intValue = Number.parseInt(value, 16);
  const r = (intValue >> 16) & 255;
  const g = (intValue >> 8) & 255;
  const b = intValue & 255;
  return `rgba(${{r}}, ${{g}}, ${{b}}, ${{alpha}})`;
}}
function escapeHtml(text) {{
  return (text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}}
function stripFrontmatter(markdown) {{
  return (markdown || "").replace(/^---\\n[\\s\\S]*?\\n---\\n?/, "");
}}
function renderInlineMarkdown(text) {{
  let html = escapeHtml(text);
  html = html.replace(/\\[\\[([^\\]]+)\\]\\]/g, '<span class="wikilink">[[$1]]</span>');
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
  html = html.replace(/\\*([^*]+)\\*/g, "<em>$1</em>");
  return html;
}}
function renderMarkdown(markdown) {{
  const lines = stripFrontmatter(markdown).split(/\\r?\\n/);
  const html = [];
  let paragraph = [];
  let listType = null;
  let listItems = [];
  let quoteLines = [];
  let inCodeBlock = false;
  let codeLines = [];
  function flushParagraph() {{
    if (!paragraph.length) return;
    html.push(`<p>${{renderInlineMarkdown(paragraph.join(" "))}}</p>`);
    paragraph = [];
  }}
  function flushList() {{
    if (!listType || !listItems.length) return;
    const items = listItems.map(item => `<li>${{renderInlineMarkdown(item)}}</li>`).join("");
    html.push(`<${{listType}}>${{items}}</${{listType}}>`);
    listType = null;
    listItems = [];
  }}
  function flushQuote() {{
    if (!quoteLines.length) return;
    html.push(`<blockquote>${{quoteLines.map(line => renderInlineMarkdown(line)).join("<br>")}}</blockquote>`);
    quoteLines = [];
  }}
  function flushCode() {{
    if (!codeLines.length) {{
      html.push("<pre><code></code></pre>");
      return;
    }}
    html.push(`<pre><code>${{escapeHtml(codeLines.join("\\n"))}}</code></pre>`);
    codeLines = [];
  }}
  for (const rawLine of lines) {{
    const line = rawLine.replace(/\\t/g, "    ");
    const trimmed = line.trim();
    if (trimmed.startsWith("```")) {{
      flushParagraph();
      flushList();
      flushQuote();
      if (inCodeBlock) {{
        flushCode();
        inCodeBlock = false;
      }} else {{
        inCodeBlock = true;
      }}
      continue;
    }}
    if (inCodeBlock) {{
      codeLines.push(rawLine);
      continue;
    }}
    if (!trimmed) {{
      flushParagraph();
      flushList();
      flushQuote();
      continue;
    }}
    const headingMatch = trimmed.match(/^(#{1,6})\\s+(.+)$/);
    if (headingMatch) {{
      flushParagraph();
      flushList();
      flushQuote();
      const level = headingMatch[1].length;
      html.push(`<h${{level}}>${{renderInlineMarkdown(headingMatch[2])}}</h${{level}}>`);
      continue;
    }}
    if (/^(-{3,}|\\*{3,})$/.test(trimmed)) {{
      flushParagraph();
      flushList();
      flushQuote();
      html.push("<hr>");
      continue;
    }}
    const quoteMatch = trimmed.match(/^>\\s?(.*)$/);
    if (quoteMatch) {{
      flushParagraph();
      flushList();
      quoteLines.push(quoteMatch[1]);
      continue;
    }}
    flushQuote();
    const unorderedMatch = trimmed.match(/^[-*]\\s+(.+)$/);
    if (unorderedMatch) {{
      flushParagraph();
      if (listType && listType !== "ul") flushList();
      listType = "ul";
      listItems.push(unorderedMatch[1]);
      continue;
    }}
    const orderedMatch = trimmed.match(/^\\d+\\.\\s+(.+)$/);
    if (orderedMatch) {{
      flushParagraph();
      if (listType && listType !== "ol") flushList();
      listType = "ol";
      listItems.push(orderedMatch[1]);
      continue;
    }}
    flushList();
    paragraph.push(trimmed);
  }}
  if (inCodeBlock) flushCode();
  flushParagraph();
  flushList();
  flushQuote();
  return html.join("");
}}
function rebuildAdjacency(filteredEdges) {{
  adjacency.clear();
  for (const node of originalNodes) {{
    adjacency.set(node.id, new Set());
  }}
  for (const edge of filteredEdges) {{
    if (!adjacency.has(edge.from)) adjacency.set(edge.from, new Set());
    if (!adjacency.has(edge.to)) adjacency.set(edge.to, new Set());
    adjacency.get(edge.from).add(edge.to);
    adjacency.get(edge.to).add(edge.from);
  }}
}}
function currentEdgeState() {{
  const minConf = parseInt(controls.confSlider.value, 10) / 100;
  controls.confValue.textContent = minConf.toFixed(2);
  return {{
    showExtracted: controls.extracted.checked,
    showInferred: controls.inferred.checked,
    showAmbiguous: controls.ambiguous.checked,
    minConf,
  }};
}}
function passesEdgeFilters(edge, edgeState) {{
  const typeOk = (edge.type === "EXTRACTED" && edgeState.showExtracted)
    || (edge.type === "INFERRED" && edgeState.showInferred)
    || (edge.type === "AMBIGUOUS" && edgeState.showAmbiguous);
  const confOk = (edge.confidence ?? 1.0) >= edgeState.minConf;
  return typeOk && confOk;
}}
function searchNodes(q) {{
  applyFilters(q, activeNodeId);
}}
function clearSelection() {{
  activeNodeId = null;
  closeDrawer();
  applyFilters(searchInput.value, null);
}}
function closeDrawer() {{
  document.getElementById("drawer").classList.remove("open");
}}
function openDrawer(node, relatedIds) {{
  document.getElementById("drawer").classList.add("open");
  document.getElementById("drawer-title").textContent = node.label;
  const communityText = Number.isInteger(node.group) && node.group >= 0 ? ` · community ${{node.group}}` : "";
  document.getElementById("drawer-meta").textContent = `${{node.type}}${{communityText}}`;
  document.getElementById("drawer-path").textContent = node.path;
  document.getElementById("drawer-preview").textContent = node.preview || "";
  document.getElementById("drawer-markdown").innerHTML = renderMarkdown(node.markdown || "");
  const relatedList = document.getElementById("drawer-related-list");
  relatedList.innerHTML = "";
  const relatedNodes = originalNodes
    .filter(item => relatedIds.has(item.id) && item.id !== node.id)
    .sort((a, b) => a.label.localeCompare(b.label));
  if (relatedNodes.length === 0) {{
    const empty = document.createElement("span");
    empty.textContent = "No directly connected nodes";
    relatedList.appendChild(empty);
    return;
  }}
  for (const related of relatedNodes) {{
    const chip = document.createElement("button");
    chip.className = "related-chip";
    chip.textContent = related.label;
    chip.onclick = () => focusNode(related.id);
    relatedList.appendChild(chip);
  }}
}}
function applyFilters(query = searchInput.value, selectedNodeId = activeNodeId) {{
  const lower = (query || "").trim().toLowerCase();
  const edgeState = currentEdgeState();
  const filteredEdges = originalEdges.filter(edge => passesEdgeFilters(edge, edgeState));
  rebuildAdjacency(filteredEdges);
  const relatedIds = selectedNodeId
    ? new Set([selectedNodeId, ...(adjacency.get(selectedNodeId) || [])])
    : null;
  const filteredNodeIds = new Set();
  for (const edge of filteredEdges) {{
    filteredNodeIds.add(edge.from);
    filteredNodeIds.add(edge.to);
  }}
  let visibleNodeCount = 0;
  const nodeUpdates = originalNodes.map(node => {{
    const matchesSearch = !lower || node.label.toLowerCase().includes(lower);
    const isActive = selectedNodeId === node.id;
    const isConnected = filteredNodeIds.has(node.id);
    const isRelated = !relatedIds || relatedIds.has(node.id);
    const hidden = !selectedNodeId && !lower && !isConnected;
    const emphasized = matchesSearch && isRelated && (isConnected || !!lower || isActive);
    if (!hidden) {{
      visibleNodeCount += 1;
    }}
    return {{
      id: node.id,
      hidden,
      color: {{
        background: emphasized ? node.color : hexToRgba(node.color, hidden ? 0.05 : 0.14),
        border: emphasized ? hexToRgba(node.color, 0.96) : hexToRgba(node.color, hidden ? 0.08 : 0.22),
        highlight: {{ background: node.color, border: hexToRgba(node.color, 1) }},
        hover: {{ background: node.color, border: hexToRgba(node.color, 1) }},
      }},
      font: {{
        color: emphasized ? "#f2f3f8" : hidden ? "rgba(242,243,248,0.08)" : "rgba(242,243,248,0.2)",
      }},
      borderWidth: isActive ? 5 : 2,
      size: isActive ? 18 : 12,
    }};
  }});
  const edgeUpdates = originalEdges.map(edge => {{
    const enabled = passesEdgeFilters(edge, edgeState);
    if (!enabled) {{
      return {{ id: edge.id, hidden: true }};
    }}
    const matchesSearch = !lower
      || nodeMap.get(edge.from)?.label.toLowerCase().includes(lower)
      || nodeMap.get(edge.to)?.label.toLowerCase().includes(lower);
    const isRelated = !relatedIds || relatedIds.has(edge.from) || relatedIds.has(edge.to);
    const touchesActive = !!selectedNodeId && (edge.from === selectedNodeId || edge.to === selectedNodeId);
    const emphasized = matchesSearch && isRelated;
    return {{
      id: edge.id,
      hidden: false,
      width: touchesActive ? 2.8 : emphasized ? 1.2 : 0.6,
      color: emphasized ? edge.color : hexToRgba(edge.color, 0.08),
    }};
  }});
  nodes.update(nodeUpdates);
  edges.update(edgeUpdates);
  if (selectedNodeId) {{
    const activeNode = nodeMap.get(selectedNodeId);
    if (activeNode) {{
      openDrawer(activeNode, relatedIds || new Set([selectedNodeId]));
    }}
  }}
  const focusSuffix = selectedNodeId && nodeMap.get(selectedNodeId)
    ? ` · focused: ${{nodeMap.get(selectedNodeId).label}}`
    : "";
  stats.textContent = `${{visibleNodeCount}} nodes · ${{filteredEdges.length}} edges${{focusSuffix}}`;
}}
const container = document.getElementById("graph");
// Adaptive physics based on graph size
const nodeCount = originalNodes.length;
const gravConst = nodeCount > 80 ? -8000 : nodeCount > 30 ? -5000 : -2000;
const springLen = nodeCount > 80 ? 250 : nodeCount > 30 ? 200 : 150;
const network = new vis.Network(container, {{ nodes, edges }}, {{
  nodes: {{
    shape: "dot",
    font: {{ color: "#ddd", size: 12, strokeWidth: 3, strokeColor: "#111" }},
    borderWidth: 1.5,
    scaling: {{
      min: 8,
      max: 40,
      label: {{ enabled: true, min: 10, max: 20, drawThreshold: 6, maxVisible: 24 }},
    }},
  }},
  edges: {{
    width: 0.8,
    smooth: {{ type: "continuous" }},
    arrows: {{ to: {{ enabled: true, scaleFactor: 0.4 }} }},
    color: {{ inherit: false }},
    hoverWidth: 2,
  }},
  physics: {{
    stabilization: {{ iterations: 250, updateInterval: 25, fit: true }},
    barnesHut: {{ gravitationalConstant: gravConst, springLength: springLen, springConstant: 0.02, damping: 0.15 }},
    minVelocity: 0.75,
  }},
  interaction: {{ hover: true, tooltipDelay: 150, hideEdgesOnDrag: true, hideEdgesOnZoom: true }},
}});
// Ensure the graph fits the viewport after physics stabilization
network.once("stabilizationIterationsDone", function () {{
  network.fit({{ animation: {{ duration: 400, easingFunction: "easeInOutQuad" }} }});
}});
function focusNode(nodeId) {{
  activeNodeId = nodeId;
  applyFilters(searchInput.value, nodeId);
  const node = nodeMap.get(nodeId) || nodes.get(nodeId);
  const relatedIds = new Set([nodeId, ...(adjacency.get(nodeId) || [])]);
  openDrawer(node, relatedIds);
  network.focus(nodeId, {{
    scale: 1.1,
    animation: {{ duration: 300, easingFunction: "easeInOutQuad" }},
  }});
}}
network.on("click", params => {{
  if (params.nodes.length > 0) {{
    focusNode(params.nodes[0]);
  }} else {{
    clearSelection();
  }}
}});
applyFilters();
</script>
</body>
</html>"""
def generate_report(nodes: list[dict], edges: list[dict], communities: dict[str, int],
                    pages: list[Path] | None = None) -> str:
    today = date.today().isoformat()
    n_nodes = len(nodes)
    n_edges = len(edges)
    if n_nodes == 0:
        return f"# Graph Insights Report — {today}\n\nWiki is empty — nothing to report.\n"
    G = nx.Graph()
    for n in nodes:
        G.add_node(n["id"])
    for e in edges:
        G.add_edge(e["from"], e["to"])
    degrees = dict(G.degree())
    edges_per_node = n_edges / n_nodes if n_nodes else 0
    density = nx.density(G)
    if edges_per_node >= 2.0:
        health = "✅ healthy"
    elif edges_per_node >= 1.0:
        health = "⚠️ warning"
    else:
        health = "🔴 critical"
    orphans = sorted([n for n, d in degrees.items() if d == 0])
    orphan_count = len(orphans)
    orphan_pct = (orphan_count / n_nodes * 100) if n_nodes else 0
    deg_values = list(degrees.values())
    mean_deg = statistics.mean(deg_values) if deg_values else 0
    std_deg = statistics.stdev(deg_values) if len(deg_values) > 1 else 0
    god_threshold = mean_deg + 2 * std_deg
    god_nodes = sorted(
        [(n, d) for n, d in degrees.items() if d > god_threshold],
        key=lambda x: x[1],
        reverse=True,
    )
    community_count = len(set(communities.values())) if communities else 0
    comm_members: dict[int, list[str]] = {}
    for node_id, comm_id in communities.items():
        comm_members.setdefault(comm_id, []).append(node_id)
    cross_comm_edges: dict[tuple[int, int], list[dict]] = {}
    for e in edges:
        ca = communities.get(e["from"], -1)
        cb = communities.get(e["to"], -1)
        if ca >= 0 and cb >= 0 and ca != cb:
            key = (min(ca, cb), max(ca, cb))
            cross_comm_edges.setdefault(key, []).append(e)
    fragile_bridges = [
        (pair, edge_list[0])
        for pair, edge_list in sorted(cross_comm_edges.items())
        if len(edge_list) == 1
    ]
    lines = [
        f"# Graph Insights Report — {today}",
        "",
        "## Health Summary",
        f"- **{n_nodes}** nodes, **{n_edges}** edges ({edges_per_node:.2f} edges/node — {health})",
        f"- **{orphan_count}** orphan nodes ({orphan_pct:.1f}%) — target: <10%",
        f"- **{community_count}** communities",
        f"- Link density: {density:.4f}",
        "",
        f"## 🔴 Orphan Nodes ({orphan_count} pages, {orphan_pct:.1f}%)",
    ]
    if orphans:
        lines.append("These pages have zero graph connections. Consider adding [[wikilinks]]:")
        for o in orphans:
            lines.append(f"- `{o}`")
    else:
        lines.append("No orphan nodes — excellent!")
    lines.append("")
    lines.append("## 🟡 God Nodes (Hub Pages)")
    if god_nodes:
        lines.append("These nodes carry disproportionate connectivity (degree > μ+2σ). Verify they are comprehensive:")
        lines.append("| Node | Degree | % of Edges | Community |")
        lines.append("|---|---|---|---|")
        for node_id, deg in god_nodes:
            edge_pct = (deg / (2 * n_edges) * 100) if n_edges else 0
            comm = communities.get(node_id, -1)
            lines.append(f"| `{node_id}` | {deg} | {edge_pct:.1f}% | {comm} |")
    else:
        lines.append("No god nodes detected — degree distribution is balanced.")
    lines.append("")
    lines.append("## 🟡 Fragile Bridges")
    if fragile_bridges:
        lines.append("Community pairs connected by only 1 edge — one deleted link breaks them:")
        for (ca, cb), edge in fragile_bridges:
            lines.append(f"- Community {ca} ↔ Community {cb} via `{edge['from']}` → `{edge['to']}`")
    else:
        lines.append("No fragile bridges — all community connections are redundant.")
    lines.append("")
    lines.append("## 🟢 Community Overview")
    if comm_members:
        lines.append("| Community | Nodes | Key Members |")
        lines.append("|---|---|---|")
        for comm_id in sorted(comm_members.keys()):
            members = comm_members[comm_id]
            members_sorted = sorted(members, key=lambda m: degrees.get(m, 0), reverse=True)
            key_members = ", ".join(members_sorted[:5])
            if len(members_sorted) > 5:
                key_members += ", …"
            lines.append(f"| {comm_id} | {len(members)} | {key_members} |")
    else:
        lines.append("No communities detected.")
    lines.append("")
    # Phantom hubs (referenced but non-existent pages)
    if pages:
        existing_stems = {p.stem.lower() for p in pages}
        existing_paths = {page_id(p).lower() for p in pages}
        refs: dict[str, set[str]] = {}
        for p in pages:
            content = read_file(p)
            links = extract_wikilinks(content)
            src = page_id(p)
            for link in links:
                normalized = link.lower().replace('\\', '/')
                if normalized.startswith('wiki/'):
                    normalized = normalized[5:]
                if normalized.startswith('raw/'):
                    continue
                if normalized in existing_stems or normalized in existing_paths:
                    continue
                refs.setdefault(link, set()).add(src)
        phantoms = [
            {"name": name, "ref_count": len(sources), "referenced_by": sorted(sources)}
            for name, sources in refs.items()
            if len(sources) >= 2
        ]
        phantoms.sort(key=lambda x: x["ref_count"], reverse=True)
        lines.append("## 🟠 Phantom Hubs (referenced but non-existent pages)")
        if phantoms:
            lines.append("These pages are referenced by 2+ existing pages but don't exist yet.")
            lines.append("They represent strong page creation signals — prioritize by reference count:")
            lines.append("| Page Name | References | Referenced By |")
            lines.append("|---|---|---|")
            for ph in phantoms:
                refs_preview = ", ".join(ph["referenced_by"][:3])
                if len(ph["referenced_by"]) > 3:
                    refs_preview += ", …"
                lines.append(f"| `[[{ph['name']}]]` | {ph['ref_count']} | {refs_preview} |")
        else:
            lines.append("No phantom hubs — all referenced pages exist.")
    else:
        lines.append("Phantom hub detection skipped (no page data available).")
    lines.append("")
    lines.append("## Suggested Actions")
    actions = []
    if orphans:
        actions.append(f"1. Add wikilinks to top orphan pages (highest potential impact: {orphans[0]})")
    if god_nodes:
        actions.append(f"{len(actions)+1}. Review god nodes for stub content vs. genuine hubs")
    if fragile_bridges:
        actions.append(f"{len(actions)+1}. Strengthen fragile bridges with cross-references")
    if phantoms:
        actions.append(f"{len(actions)+1}. Create pages for top phantom hubs (start with `[[{phantoms[0]['name']}]]` — {phantoms[0]['ref_count']} references)")
    if not actions:
        actions.append("1. Graph is in good shape — maintain current linking practices")
    lines.extend(actions)
    lines.append("")
    # Contradicts density
    contradicts_edges = [e for e in edges if e.get("relation") == "contradicts"]
    n_contradicts = len(contradicts_edges)
    contradicts_density = (n_contradicts / n_edges * 100) if n_edges else 0
    lines.append("## ⚔️ Contradicts Edge Density")
    if n_contradicts == 0:
        lines.append("No `contradicts` edges found. Annotate conflicting concepts in `related:` fields with `# contradicts` to surface systematic disagreements.")
    else:
        density_label = "🔴 high — systematic disagreements present" if contradicts_density > 20 else "🟡 moderate" if contradicts_density > 8 else "🟢 low"
        lines.append(f"{n_contradicts} contradicts edge(s) out of {n_edges} total ({contradicts_density:.1f}%) — {density_label}")
        lines.append("| From | To |")
        lines.append("|---|---|")
        for ce in contradicts_edges[:15]:
            lines.append(f"| `{ce['from']}` | `{ce['to']}` |")
        if n_contradicts > 15:
            lines.append(f"| … and {n_contradicts - 15} more | |")
    lines.append("")
    return "\n".join(lines)
# ── Bug 6 修复：build_graph 完整整合 inference_complete 标志 ──
def build_graph(infer: bool = True, open_browser: bool = False, clean: bool = False,
                report: bool = False, save: bool = False, apply_inferred: bool = False):
    pages = all_wiki_pages()
    today = date.today().isoformat()
    if not pages:
        print("Wiki is empty. Ingest some sources first.")
        return
    print(f"Building graph from {len(pages)} wiki pages...")
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    if clean and INFERRED_EDGES_FILE.exists():
        INFERRED_EDGES_FILE.unlink()
        print("  cleaned: removed inference checkpoint")
    cache = load_cache()
    print("  Pass 1: extracting wikilinks...")
    nodes = build_nodes(pages)
    edges = build_extracted_edges(pages)
    print(f"  → {len(edges)} extracted edges")
    inferred = []
    inference_complete = True  # 默认值，apply_inferred/no-infer 路径下视为"无需推断即完整"
    if apply_inferred:
        if RESULTS_FILE.exists():
            try:
                data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
                inferred_edges_data = data.get("inferred_edges", [])
                node_ids = {n["id"] for n in nodes}
                for e in inferred_edges_data:
                    if e.get("from") in node_ids and e.get("to") in node_ids:
                        rel_type = e.get("type", "INFERRED")
                        confidence = float(e.get("confidence", 0.7))
                        inferred.append({
                            "id": edge_id(e["from"], e["to"], rel_type),
                            "from": e["from"], "to": e["to"], "type": rel_type,
                            "title": e.get("relationship", ""), "label": "",
                            "color": EDGE_COLORS.get(rel_type, EDGE_COLORS["INFERRED"]),
                            "confidence": confidence,
                        })
                print(f"  → applied {len(inferred)} inferred edges from results file")
            except Exception as e:
                print(f"  WARN: failed to apply inferred edges: {e}")
                inference_complete = False
        else:
            print("  WARN: --apply-inferred specified but Graph/.infer-results.json not found")
            inference_complete = False
    elif infer:
        print("  Pass 2: inferring semantic relationships (Agent-assisted)...")
        inferred, inference_complete = build_inferred_edges(pages, edges, cache, resume=not clean)
        print(f"  → {len(inferred)} inferred edges loaded"
              + ("" if inference_complete else "（不完整：仍有页面待推断，见下方提示）"))
        save_cache(cache)
    # infer=False（--no-infer）：inference_complete 保持 True，因为用户主动选择跳过，不算"不完整"
    edges.extend(inferred)
    before_dedup = len(edges)
    edges = deduplicate_edges(edges)
    if before_dedup != len(edges):
        print(f"  dedup: {before_dedup} → {len(edges)} edges")
    print("  Running Louvain community detection...")
    communities = detect_communities(nodes, edges)
    for node in nodes:
        comm_id = communities.get(node["id"], -1)
        if comm_id >= 0:
            node["color"] = COMMUNITY_COLORS[comm_id % len(COMMUNITY_COLORS)]
        node["group"] = comm_id
    degree_map: dict = {}
    for e in edges:
        degree_map[e["from"]] = degree_map.get(e["from"], 0) + 1
        degree_map[e["to"]] = degree_map.get(e["to"], 0) + 1
    for node in nodes:
        node["value"] = degree_map.get(node["id"], 0) + 1
    extracted_edges = [e for e in edges if e.get("type") == "EXTRACTED"]
    inferred_edges_out = [e for e in edges if e.get("type") in ("INFERRED", "AMBIGUOUS")]
    graph_data = {
        "nodes": nodes,
        "edges": extracted_edges,
        "inferred_edges": inferred_edges_out,
        "built": today,
        "inference_complete": inference_complete,  # ── 修复 Bug 6：持久化完整性标记 ──
    }
    GRAPH_JSON.write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved: Graph/graph.json  ({len(nodes)} nodes, {len(edges)} edges)")
    html = render_html(nodes, edges)
    GRAPH_HTML.write_text(html, encoding="utf-8")
    print(f"  saved: Graph/graph.html")
    status_tag = "完整" if inference_complete else "不完整（需 --apply-inferred 补全）"
    append_log(f"## [{today}] graph | 重建图谱 ({len(nodes)} 节点, {len(edges)} 边, {status_tag})")
    if report:
        if not HAS_NETWORKX:
            print("Warning: networkx not installed. Cannot generate report.")
        else:
            report_text = generate_report(nodes, edges, communities, pages=pages)
            if not inference_complete:
                report_text = (
                    "> WARN: 本次图谱推断未完整完成，以下报告基于部分推断边生成，"
                    "上帝节点/社区结构等统计可能不准确。请运行 `--apply-inferred` 补全后重新生成报告。\n\n"
                    + report_text
                )
            print("\n" + report_text)
            if save:
                report_path = GRAPH_DIR / "graph-report.md"
                report_path.write_text(report_text, encoding="utf-8")
                print(f"  saved: {report_path.relative_to(REPO_ROOT)}")
            append_log(f"## [{today}] graph | 图谱健康报告生成 ({len(nodes)} 节点分析)")
    if open_browser:
        webbrowser.open(str(GRAPH_HTML.resolve()))
    if not inference_complete:
        print(f"\n[NEEDS_REVIEW] 本次图谱推断未完整完成，graph.json 中 inference_complete=false。"
              f"请完成推理后运行: python -m Tools.build_graph --apply-inferred")
if __name__ == "__main__":
    init_env()
    ensure_utf8()
    parser = argparse.ArgumentParser(description="Build LLM Wiki knowledge graph (Agent-assisted inference)")
    parser.add_argument("--no-infer", action="store_true", help="Skip semantic inference (faster)")
    parser.add_argument("--open", action="store_true", help="Open graph.html in browser")
    parser.add_argument("--clean", action="store_true", help="Delete checkpoint and force full re-inference")
    parser.add_argument("--report", action="store_true", help="Generate graph health report")
    parser.add_argument("--save", action="store_true", help="Save report to graph/graph-report.md")
    parser.add_argument("--apply-inferred", action="store_true", help="Merge previously inferred edges from Graph/.infer-results.json")
    args = parser.parse_args()
    build_graph(
        infer=not args.no_infer,
        open_browser=args.open,
        clean=args.clean,
        report=args.report,
        save=args.save,
        apply_inferred=args.apply_inferred,
    )
```

---

### 1.10 初始化 Git 仓库

```bash
git init
git branch -M main
git config --local user.name "LLM Wiki Agent"
git config --local user.email "llm-wiki@local"
```

### 1.11 追加 bootstrap 记录到 log.md

Wiki/log.md 末尾追加（将 `<YYYY-MM-DD>` 替换为当天日期）：

```
## [<YYYY-MM-DD>] bootstrap | LLM Wiki OS v1.0 骨架建立
```

### 1.12 首次 Git 提交

```bash
git add AGENTS.md README.md .gitignore .llm-wiki/ Raw/ Wiki/ Graph/ Tools/
git commit -m "chore: bootstrap LLM Wiki OS v1.0"
```

若用户在 §1.1 提供了远程仓库 URL：

```bash
git remote add origin <URL>
git push -u origin main
```

### 1.13 最终验证与报告

```bash
python -m Tools.health --help
python -m Tools.ingest --help
python -m Tools.lint --help
python -m Tools.query --help
python -m Tools.build_graph --help
```

运行一次健康检查以确认初始状态：

```bash
python -m Tools.health
```

> 注：bootstrap 刚完成时 health 可能会报告一些非阻塞提示（如 overview.md 的占位内容），属正常现象，将在首次摄入后自然消除。

打印完整目录树：

```bash
Get-ChildItem -Recurse -File | Select-Object -ExpandProperty FullName | Sort-Object
```

```bash
git log --oneline
```

**下一步操作提示**：

```
Bootstrap 完成。请阅读 AGENTS.md 了解完整操作规程。快速开始：
1. 将文件放入 Raw/ 对应子目录
2. 在 AI 会话中说 ingest <路径> 开始摄入（或说 ingest 恢复已有批次）
3. 说 query: <问题> 触发查询
4. 每次新会话先执行 health 检查仓库状态
```

---

### §2 AGENTS.md 模板

Agent 请将以下内容**原样写入**目标库的 `AGENTS.md` 文件。

**不要写入本节最外层的 ` ```markdown ` 起始行和结尾的 ` ``` ` 行**（它们是本提示词的边界标记）。

AGENTS.md 内部词条模板（§3.1–§3.5）中的 ` ```markdown ` 代码块标记**应原样保留**，它们是用于向 Agent 展示格式的示例。

```markdown
# AGENTS.md（最高操作契约）
<!-- version: v1.0 | created: 2025-06-17 | updated: 2026-06-19 -->
本文件是 Agent 每次执行前必读的最高宪法。所有工作流、规则、模板均以本文件为唯一权威来源。
何时修订：当某条规则反复产生不符合预期的结果，或某个工作流与实际使用习惯持续偏差时，与研究者讨论后修订。
## 会话启动规程（每次新会话必须首先执行）
1. 运行健康检查：`python -m Tools.health`
2. 读取 `Wiki/log.md` 最近 10 条记录，了解上次会话操作上下文
3. 读取 `Wiki/index.md`，获取当前知识库词条全貌
4. 报告：健康状态摘要 + 上次会话摘要 + 当前词条数
5. 等待研究者指令
健康检查失败降级：若 health 命令因 Python 环境或磁盘权限失败而无法执行，输出具体错误信息，告知研究者“本次会话未完成健康检查”，记录风险后继续。
qmd 集合提示：若 health 报告中出现 “qmd 集合未初始化” 警告，请在开始前提醒研究者运行对应的 qmd init 命令。
## 快速触发指令
| 指令 | 触发工作流 | 对应命令 | 说明 |
|------|-----------|---------|------|
| `ingest` | 恢复已有批次 | `python -m Tools.ingest` | 无参数仅恢复队列，不扫描全库；需全库扫描请指定 Raw/ 目录 |
| `ingest <文件或目录> [...]` | 批处理摄入（指定范围） | `python -m Tools.ingest <路径> [路径...]` | 支持文件、目录混合，自动截断，详见 §四 |
| `ingest [路径...] --discuss` | 批量预读讨论模式 | `python -m Tools.ingest [路径...] --discuss` | 批量展示最多 5 个文件内容，统一讨论词条结构后逐篇 finalize；不带路径时仅恢复已有 discuss 批次，不会自动扫描 |
| `ingest --finalize <slug> <title> <file> [--force] [--no-concept --no-concept-reason "<原因>"]` | 摄入完成回传 | `python -m Tools.ingest --finalize <slug> <title> <路径> [--force] [--no-concept --no-concept-reason "<原因>"]` | 词条写入完成后推进批次；--force 跳过验证；--no-concept 豁免无可提取概念的文件 |
| `ingest --skip <raw_rel> [--force]` | 跳过文件并推进 | `python -m Tools.ingest --skip <路径> [--force]` | 跳过无法处理的文件；可加 --force 跳过批次末尾验证 |
| `query: <问题>` | 查询工作流（两步） | Step 1：`qmd query "<问题>" --collection wiki --format json -n 8 > .qmd-hits.json`；Step 2：`python -m Tools.query "<问题>" --qmd-hits .qmd-hits.json` | qmd 不可用或失败时直接执行 Step 2（脚本自动降级）。保存结果追加 `--save --slug <slug>`；Agent 推理完成后归档使用 `--apply --slug <slug> --answer "<答案>"`（强烈建议带上原始问题文本）。 |
| `health` | 健康检查 | `python -m Tools.health` | 零 LLM 调用，每次会话必跑；仅阻塞项影响退出码 |
| `lint` | 质量审计 | `python -m Tools.lint` | 摄入批次 ≥3 个文件后运行 |
| `build graph` | 图谱分析 | `python -m Tools.build_graph` | 可选扩展，建议 50+ 词条后使用 |
| `chore: move` / `chore: rename` / `chore: delete` | 维护操作 | 见 §十 | — |
**执行纪律**：
- `ingest`：通过 Agent 环境可用的任务追踪机制创建各步骤追踪清单，每完成一步更新一次状态
- `query` / `health` / `lint` / `graph`：使用内联步骤标注推进
- Python 解释器：优先使用 `python -m` 方式运行脚本
**多工作流并发处理**：lint、graph 推断产生的 `[AGENT_LLM_REQUEST]`，一律在当前摄入批次的 `[STOP] 批次已全部完成` 信号之后处理，不在批次中途响应，除非研究者主动打断。
## 一、路径规范
【根目录定义】：本契约所有路径及 Obsidian [[wikilink]] 均以 Vault 根目录（包含 AGENTS.md、Raw/、Wiki/、Graph/、Tools/ 的那一层）为唯一基准面。
【双链绝对化】：所有指向 Raw 层或 Wiki 层的链接，必须使用基于 Vault 根目录的绝对路径，严禁使用 `../` 等相对路径。
示例：`[[Wiki/concepts/xxx.md]]`、`[[Raw/Sources/xxx.pdf]]`
## 二、Raw 层目录与加注规则
Raw 层由研究者完全掌管，Agent 只读取，不做任何修改或移动。
【单一事实源】：Raw 层各子目录的名称、加注类型（annotation）、是否参与摄入（ingest），以 `.llm-wiki/raw-mapping.json` 为唯一权威来源。Agent 每次需要查询目录配置时，读取该文件，依据文件所在 Raw 根下第一级子目录名查找对应条目。
研究者可自行在 Raw 子目录下创建更深层的归档目录，Agent 扫描时会递归发现，加注映射始终以 Raw 根下第一级子目录为准。
【加注执行规则】（具体 annotation 文字见 raw-mapping.json）：
- annotation 非空的目录：摄入时所有他人观点/推论/主观内容写入 Wiki 时强制加注（<annotation值>）
  示例（annotation="据文献"）：某理论认为 X 是 Y 的充分条件（据文献）。
  示例（annotation="个人思考"）：休谟的同一性论证在数量与统一性边界处存在逻辑断层（个人思考）。
- annotation 为 null 的目录（如 Assets）：不独立摄入，不加注
【Assets 定位与图片读取规则】：Assets/ 目录不独立摄入。当摄入含图片引用的 Markdown 文件时，Agent 在该次摄入流程内读取被引用的图片作为补充上下文：
1. 先完整读取文本内容，按正常流程生成词条草稿
2. 识别文中 `![[...]]` 或 `![](Raw/Assets/...)` 引用的图片路径
3. 尝试读取相关图片；图片不可读时输出警告 `WARN: 图片不可读: <路径>（原因：...）`，跳过该图片，不阻塞摄入流程
4. 将可读图片信息补充进对应词条的相关章节，标注 `[[图示补充]]`
【禁止主观裁判】：Agent 仅作为“知识整合编译器”，不得独立判断哪种研究观点或诠释“更正确”。
【禁止自我引用】：严禁将 Agent 自己之前在 Wiki 词条里写就的总结性言论，作为推导或佐证新事实的“客观证据”。
【禁止推断型事实填补】：当来源文件中某项信息缺失时，Agent 严禁根据上下文合理性进行推断补全。缺失即缺失：标注为空白或写入 `[[来源缺失，待补充]]`。
【查询合成加注】：由查询工作流跨词条合成产生的新推论，必须加注 `（据查询合成，未经来源验证）`，与直接来源于 Raw 层的事实明确区分。
## 三、词条元数据与排版规范
词条类型说明：研究者需要关注和浏览的词条是 concepts（抽象概念）和 entities（具体对象）两类。sources/ 和 syntheses/ 由 Agent 自动生成和维护。disambiguations/ 在遇到歧义词时按需生成。
### 命名规范
| 词条类型 | 命名规范 | 示例 |
|---------|---------|------|
| 概念词条（concepts/） | 中文概念名.md（必须，严禁拼音，英文专有名词保留英文） | 纯粹理性批判.md、BullPutSpread.md |
| 实体词条（entities/） | 中文通用名.md（人名用中文常用译名；无译名时保留原文） | 康德.md、ImmanuelKant.md |
| 长文摘要（sources/） | 中文书名或文章标题.md（与原著标题保持一致） | 思考快与慢.md |
| 消歧词条（disambiguations/） | 中文词条名（流派）.md | 空（佛教）.md、空（道家）.md |
| 综述页（syntheses/） | 中文语义短语.md（2-6字，概括查询主题） | 动量策略失效条件.md |
【中文文件名强制规则】：所有 Wiki 词条文件名必须使用中文（或保留原文的英文专有名词），严禁使用汉语拼音作为文件名。
【slug 全局唯一性】：所有词条类型（concepts、entities、sources、syntheses、disambiguations）共享同一全局 slug 命名空间，严禁重复。Agent 在创建任何词条前必须通过 check_slug_conflict 校验全局唯一性。
【slug 一致性原则】：同一来源文件在不同会话中必须生成相同的 slug。生成 slug 后立即记录至 log.md 的 `slug:` 字段。若检测到 slug 冲突（相同 slug 对应不同来源文件），输出警告，等待研究者手动确认重命名，不自动覆盖。
【多切片同一著作的 slug 规则】：同一本书被切分为多个 Raw 文件时：
- 每个 Raw 文件在 `--finalize` 中必须使用**独立的、唯一的 slug**
- slug 格式：`书名_切片标记`（如 `康德纯粹理性批判提要_先验要素论_part1`）
- master source_map（总纲页）独立创建，`raw_link` 设为空字符串 `""`，`sources` 列出所有切片，**不得**通过 `--finalize` 创建或占用任何切片的 slug
- 严禁将 master slug 用于任何单个切片的 `--finalize`
### 3.1 标准概念词条（Wiki/concepts/）
```markdown

---

title: ""

type: concept

aliases: ["", "", ""]

domain: "<从 .llm-wiki/domain-enum.json 枚举中选取，如：<DOMAIN_FIRST>>"

subdomain: ""

era: "<可选：历史时代 / 年份 / 无>"

tags: []

sources: ["[[Raw/Sources/xxx.md]]"]   # 必须使用单行 JSON 数组字符串，每个元素为 [[Raw/...]] 维基链接

related: [""]

# related 字段语义边类型注释（可选，供 build_graph.py 读取以生成加权边）：

# "[[相关词条]] # supports"

# "[[相关词条]] # contradicts"

event_date:

last_updated: YYYY-MM-DD

pending_review: false

---

## 核心定义

（150 字以内，精准的本质定义，严禁前言后语）

## 核心论点与逻辑演进

（无序列表 - 结构化呈现。加注规则见 §二）

## 边界防御与相近概念区分

对比 [[...]]：指出本质区别，严禁语义串味。

## 关联实体

[[...]]

## 原始事实追溯

来源：[[...]]

```
domain 字段填写规范：必须从 `.llm-wiki/domain-enum.json` 当前定义的合法枚举中选取（bootstrap 默认：<DOMAIN_ENUM>）。health 命令会自动校验该字段合法性。不确定时填写枚举中的最后一项（通常为“其他”）。研究者可通过编辑 `.llm-wiki/domain-enum.json` 及本文件中的枚举说明来扩展领域。
【Concept 与 Entity 边界定义】：
- 归入 Concept：抽象的策略、定理、机制、算法、方法论、思想体系。判断标准：可复现、可泛化、不绑定唯一历史实例。
- 归入 Entity：具有唯一历史身份的具体对象。判断标准：存在唯一时空坐标，无法被泛化复现。
- 边界判断规则：若对某对象能问“这个概念在其他场合还适用吗？”且答案为“是”，归 Concept；若只能问“这件事发生过吗？”，归 Entity。
### 3.2 实体词条（Wiki/entities/）
```markdown

---

title: "<人名 / 著作名 / 机构名 / 事件名>"

type: entity

entity_type: person | organization | work | event

tags: []

sources: ["[[Raw/Sources/xxx.md]]"]   # 若引用 Raw 文件，必须使用单行 JSON 数组字符串，每项为 [[Raw/...]] 维基链接

last_updated: YYYY-MM-DD

---

## 简介

（100 字以内。加注规则见 §二）

## 核心关联概念

[[...]]

## 原始事实追溯

来源：[[...]]

```
### 3.3 长文摘要映射（Wiki/sources/）
仅由 Raw/Sources/ 或其他 ingest=true 目录的文件触发。
```markdown

---

title: "<书名 / 长文标题>"

type: source_map

author: ""

raw_link: "[[]]"  # 必须使用 [[Raw/...]] 维基链接格式，check_slug_conflict 据此验证来源归属

last_updated: YYYY-MM-DD

pending_review: false

---

## 整体脉络与摘要

（加注规则见 §二）

## 核心抽取概念

（向 Wiki/concepts/ 建立辐射双链。此节**仅允许**指向 `Wiki/concepts/` 的抽象概念链接。）

[[概念]]：一句话说明关联（据文献）

> **⚠️ 硬性约束**：`## 核心抽取概念` 节**严禁**出现指向 entities/ 或 sources/ 或 disambiguations/ 的任何链接。实体（人、著作、机构）仅在词条 frontmatter `sources:` 字段及 `## 核心关联概念/关联实体` 节中引用。若该 raw 文件可提取的概念为空，将本节留空即可——不要把实体链接当概念充数。batch 末尾 concept/entity 覆盖验证的"entity 覆盖"由实体词条的 frontmatter `sources:` 字段达成，与本节无关。

>

> **自查清单**：写入本节前逐条核验（每问均需为"是"）→ (1) 此 wikilink 目标是否在 `Wiki/concepts/` 下？(2) 它是可复现、可泛化的抽象吗？(3) 去掉它是否使双链失去实质语义？任一为"否"则移出本节。

## 章节要点

```
### 3.4 消歧导航页（Wiki/disambiguations/）
```markdown

---

title: ""

type: disambiguation

last_updated: YYYY-MM-DD

---

本词条在不同传统或领域下存在多个完全独立的实质含义，请选择对应专页：

[[概念（流派A）.md]] — 流派 A 视角的核心要义

[[概念（流派B）.md]] — 流派 B 视角的核心要义

> **WARN**：审计守则——若原始笔记未明确指明流派或语境，默认不写入任何消歧专页，输出警告，挂起等待研究者人工确认后分配。

```
消歧词条重命名注意：执行 chore: rename 时，除更新所有双链外，还需同步更新该消歧页内所有指向相关专页的导航链接，避免断链。
### 3.5 综述页（Wiki/syntheses/）
```markdown

---

title: ""

type: synthesis

tags: []

sources: [""]

status: open | closed

open_questions: []

last_updated: YYYY-MM-DD

---

## 结论

## 论据与引用

[[词条]]：……（据查询合成，未经来源验证）

```
## 四、摄入工作流（Ingest Workflow）
**触发与范围判定**：
| 用户指令 | 候选文件范围 | 批次大小 | 停止时机 |
|---------|-------------|---------|---------|
| `ingest` | 仅恢复已有队列 | — | 本批次处理完即停 |
| `ingest <文件或目录> [...]` | 仅限指定路径（目录递归展开） | 见 ingest.py DEFAULT_BATCH_SIZE | 本批次处理完即停 |
| `ingest [路径...] --discuss` | 与对应无 --discuss 版本相同；**不带路径时仅恢复已有 discuss 批次** | 最多 5 个（一批） | 批量展示全部内容后统一讨论，讨论完成后逐篇 finalize |
【目录意图识别规则】：当用户说“处理 Sources 下所有文件”或给出目录路径时，Agent 将目录路径直接作为参数传入 `python -m Tools.ingest <目录路径>`，**严禁**手动展开目录为文件列表拼接到命令行。目录展开和批次截断完全由脚本内部统一处理。
【主题过滤规则】：用户指定**特定主题**（如“处理精神现象学”“处理传习录”）时，Agent 必须将匹配该主题的具体文件列表传入，**严禁**传入上层目录。具体做法：先用 Get-ChildItem -Filter “*关键字*” 获取目标文件列表，逐一传入 python -m Tools.ingest <路径1> <路径2> ...。传入父目录会导致脚本按文件名排序取全域文件，而非用户指定的主题。
**PowerShell 路径空格陷阱**：Windows 路径含空格（`D:\Program files\...`）时，**严禁**用 `$($files -join ' ')` 拼接数组为单字符串传给 Python，这会导致路径在空格处被拆分为多个参数。正确做法：将 `$files` 数组直接传递给 Python（PowerShell 自动做数组展开为独立参数），或在 workdir 设到项目根的前提下使用相对路径。
正确示例：
```powershell

# 正确：数组直接传递

$files = Get-ChildItem -Recurse -Filter "*精神现象学*" | Select-Object -ExpandProperty FullName

python -m Tools.ingest $files

# 正确：或先用替换去掉前缀再用相对路径（同时设 workdir=项目根）

$files = Get-ChildItem -Recurse -Filter "*精神现象学*" | Select-Object -ExpandProperty FullName | ForEach-Object { $_.Replace("D:\Program files\LLMwiki\", "") }

python -m Tools.ingest $files

```
`--discuss` 使用限制：仅当用户明确表示需要先讨论词条结构时方可加 `--discuss` 参数。默认情况下**不加**，直接进入单篇自动处理循环。请注意 **`--discuss` 不带路径参数时不会自动扫描全库**，只会恢复已有的 discuss 批次；如需针对新文件启动 discuss，须同时指定文件/目录。
**核心步骤**（单文件循环模式）：
1. Agent 根据触发指令执行 `python -m Tools.ingest [路径...] [--discuss]`。
   - **无 --discuss**：脚本扫描并生成批次，立即输出第一个待处理文件的内容（前 4000 字符）及上下文信息，进入单篇自动处理循环。
   - **有 --discuss**：脚本批量展示最多 5 个文件的内容（每个文件前 4000 字符），全部展示完毕后输出统一讨论提示，等待研究者与 Agent 讨论词条结构。讨论完成后，按任意顺序逐篇执行 `--finalize` 回传；若某文件决定跳过，执行 `--skip`。
2. Agent 为该文件创建或更新对应的 Wiki 词条（source_map + 相关 concept/entity 等）。
3. Agent 调用 `python -m Tools.ingest --finalize <slug> <title> <路径> [--brief "<摘要>"] [--no-concept ...]` 完成回传。脚本更新 index.md、日志、Git 提交、qmd 索引，并输出 `[CONTINUE]`（尚有文件）或 `[STOP]`（批次完成）。
4. 若脚本输出 `[CONTINUE]`，Agent 立即执行 `python -m Tools.ingest`（无参数），脚本自动从队列取下一个文件，输出其内容，回到步骤 2；若输出 `[STOP]`，停止。
批次最后一文件 finalize 后，脚本检查本批次每个 source_map 是否至少对应一个 concept/entity 词条。若缺失且未使用 `--no-concept` 豁免，则阻断返回 exit code 2，并将缺失的源文件从 done 移回 pending 队列头部。Agent 创建对应概念/实体页后重新执行 `--finalize` 即可。若来源确实不含有概念性内容（如纯数据表、日程、个人记录），使用 `--no-concept` 豁免，或 `--force` 跳过整个验证。
**【--no-concept 硬约束】— 禁止模式化套用，必须逐文件评估。**
`--no-concept` 仅当满足以下 **所有** 条件时才可使用：
1. 文件中不存在任何可提取的抽象概念（定理、机制、方法论、思想体系）
2. 文件中不存在任何可提取的唯一历史实体（人物、著作、机构、事件）
**执行纪律**：在调用 `--finalize --no-concept` 之前，Agent 必须在内心回答以下三个问题（不在日志中输出，作为思维硬性检查）：
1. 这个文件是"纯 quote 堆砌"还是"有结构的知识概括"？若为后者，不可豁免。
2. 这个文件的标题/标签中是否包含特定哲学方法、思想体系、术语系统？若包含，不可豁免。
3. 这个文件是否指向一个唯一的历史实体（人物、著作、宗教经典）？若是，必须创建 entity。
**逐文件评估原则**：禁止将某个文件的 `--no-concept` 判断模式化地延续到下一个文件。每遇到一个新文件，必须独立评估上述三条规则。最危险的模式化陷阱例子：遇到连续 5 个文件名带"摘录"的文件就自动全部 `--no-concept`——这是本次事故的直接原因，永久禁止。
**【entity 覆盖 ≠ 概念豁免】**：entity 词条已存在且 `sources:` 字段引用了某 Raw 文件，**不代表**该 Raw 文件的摘录/摘要应豁免概念提取。entity 覆盖仅解决"该来源有对应的实体页"这一需求，不解决"该摘录内容中有无抽象概念需要提取"的问题。判断是否使用 `--no-concept` 时，**entity 的存在不是相关因素**。必须回归到 `【--no-concept 硬约束】` 的三条准用条件和五条禁止条件做独立判断。
【去重判断依据】：由 ingest 自动完成路径与 SHA-256 哈希的比对，Agent 无需手动计算。
【支持格式】：.md 直接摄入；.pdf、.docx、.pptx、.xlsx、.html、.txt、.epub 等通过 markitdown 自动转换后摄入。
【调用前检查】：Agent 在调用 `python -m Tools.ingest` 之前，若 `.llm-wiki/ingest-queue.json` 存在且 pending 列表非空，说明有未完成批次。此时脚本会自动检测并提示继续，Agent 直接执行 `python -m Tools.ingest` 即可恢复上次批次，无需任何额外参数。
【overview.md 强制更新规则】：每次 ingest 批次完成后，Agent 必须检查并实质性更新 Wiki/overview.md，至少替换掉 `## 当前研究焦点` 节的占位注释 `<!-- ... -->`，写入本次摄入涉及的核心主题与领域。其他三个 section 也应在有足够信息时更新。health 命令会检测所有仍为占位的 section 并报告。
【批次停止规则】：
每完成一个文件的 `--finalize`，脚本会在末尾输出以下之一：
- `[CONTINUE] 立即执行：python -m Tools.ingest` → Agent 必须立即执行此命令（无参数），脚本自动从 `.llm-wiki/ingest-queue.json` 读取下一个待处理文件。这是批量流程的唯一驱动机制。
- `[STOP] <原因说明>` → 停止，不再继续处理任何文件
以脚本输出信号为准，无需额外判断。`[STOP]` 后即便全库仍有待摄入文件，也不主动继续，除非用户再次触发。
【批次末尾 concept/entity 覆盖验证】：
批次最后一个文件处理完毕（无论是 `--finalize` 还是 `--skip`）后，脚本自动检查本批次每个 source_map 是否至少对应一个 concept/entity 词条（该词条 frontmatter sources 字段须引用对应 Raw 文件，且正文非空）。
- 验证通过 → 输出 `[STOP] 批次已全部完成`
- 验证失败 → 输出 `[NEEDS_REVIEW]` 并列出未覆盖的 source_map，将对应的源文件从 done 移回 pending，等待补充词条后重新执行 `--finalize`
- 若来源确实不含可提取概念（详见上方 `【--no-concept 硬约束】` 中的合格条件），在对应文件的 `--finalize` 中传入 `--no-concept --no-concept-reason "<原因>"` 豁免该文件；豁免记录写入 log.md
- 强制跳过验证：在最后一个文件的 `--finalize` 或 `--skip` 中传入 `--force`
## 五、增量合并与冲突处理协议
### 5.1 增量合并
新笔记摄入时，先检索 Wiki/ 是否已有对应词条：
- 无：根据对应模板新建词条
- 有：对比 Diff，将新物料细节无缝缝合进对应章节，严禁粗暴覆盖旧词条
- 注意：若新词条仅是已有词条的参数化变体或狭窄场景特例，优先合并进已有词条
### 5.2 冲突处理与 pending_review 协议
【冲突定义】：以下任一情况视为冲突，禁止 Agent 自行裁判，强制挂起：
- 核心定义段出现直接否定关系
- 数值、年份、因果方向明确不一致
- 同一词汇在新料与已有词条中指向完全不同的对象
- 核心概念定义发生结构性重构
冲突标记格式：
```markdown

WARN: 争议：

说法 A（来源：[[...]]）：……

说法 B（来源：[[...]]）：……

待研究者人工裁决。

```
同时将 pending_review 设为 true。
【文件修改后重新摄入的责任边界】：若源文件已被修改，`ingest_file` 会自动将引用该文件的词条标记为 `pending_review: true`，并提示 Agent 先与研究者确认裁决方向后再更新词条。Agent 在收到该提示后，应将该词条的冲突审查纳入本次摄入的待办事项，与研究者沟通后再完成 finalize。
【pending_review 裁决流程】：研究者完成裁决后，Agent 删除冲突标记，按裁决结果更新正文，将 pending_review 改回 false，更新 last_updated，追加日志并 Git 提交。
【冲突降级规则】：若研究者在当前会话中主动指出某条 pending_review 标记长期未处理且无法裁决，Agent 可在不否定任何一方观点的情况下，将冲突双方均保留至词条正文，移除 pending_review 标记，并追加日志 `## [日期] chore | manual-resolve: [[词条]]（研究者确认降级，双方保留）`。
### 5.3 消歧触发规则
一旦发现同一词汇在不同传统或领域下存在实质性定义撕裂：
- 将原词条升级为消歧导航页
- 为每个独立含义创建独立词条（文件名：`概念（流派）.md`）
- 若原始笔记未明确指明流派，输出警告，挂起等待人工确认
- 消歧导航页及其子专页若在单次摄入中一并创建：(1) `--finalize` 的 slug 参数只能登记其中一个，其余文件会触发 health『日志覆盖缺失』提示；(2) 消歧导航页本身在创建初期通常还没有其他词条的入站双链，会触发 lint『孤儿页』提示。两者均为 NON_BLOCKING/非阻塞，属预期行为，待后续摄入逐步建立双链后会自然消失。
## 六、查询工作流（Query Workflow）
触发：`query: <问题>` → 按两步执行（qmd 可用时先执行 Step 1，否则直接执行 Step 2）
执行步骤：
1. **【强制】qmd 语义检索**：
   ```bash
   qmd query "<问题>" --collection wiki --format json -n 8 > .qmd-hits.json
   ```
   降级规则（按优先级，任一条件满足即跳过本步直接执行 Step 2）：
   - qmd 未安装 → 跳过，注明“qmd 未安装”
   - qmd 命令报错（集合未初始化、权限不足、任何非零退出码）→ 跳过，注明具体错误；不得因 Step 1 报错停止整个查询流程
   - `.qmd-hits.json` 写入成功但内容为空数组 `[]` → 正常传入 Step 2，脚本自动降级关键词匹配
2. 执行查询脚本：
   ```bash
   python -m Tools.query "<问题>" --qmd-hits .qmd-hits.json
   ```
   Step 1 跳过时省略 `--qmd-hits` 参数（脚本自动使用内部降级检索）。
3. Agent 读取命中文件内容，综合分析后给出答案。
4. 开放问题预读：扫描 Wiki/syntheses/ 中 status: open 的词条，判断是否与本次查询相关。
5. 生长机制：询问是否归档综述、是否摄入盲区文件。
【qmd 临时输出文件】：`.qmd-hits.json` 为单次查询的中间产物，.gitignore 已屏蔽，无需手动清理。
归档注意事项：若使用 `--save`，Agent 的 LLM 推理可能异步完成（见 `[AGENT_PENDING]` 提示）。此时脚本会保存上下文到 `.qmd-pending-query.json`，并提示使用 `--apply --slug <slug> --answer "<答案>"` 完成归档。强烈建议在 `--apply` 命令中保留原始问题文本作为位置参数。若遇到已存在的综述页，脚本会明确提示使用 `--update` 参数，Agent 应根据提示重新执行带 `--update` 的 `--apply` 命令。
【回哺硬性约束】：回哺内容必须加注 `（据查询合成，未经来源验证）`；若与词条既有内容存在矛盾，强制走冲突处理协议（见 §五）。
## 七、健康检查工作流（Health Workflow）
触发：`health` → `python -m Tools.health [--json] [--save]`
频率：每次会话启动规程中必跑 | 成本：零 LLM 调用
检查项：空文件/存根页、索引同步、日志覆盖（区分 ingest 和 query-synthesis 来源）、Overview 占位、断链、Assets 断链、Raw 目录合规、哈希一致性（含 move/delete 追踪，当关联词条已标记 pending_review 时不再重复报告）、pending_review 扫描、Domain 合规、Frontmatter 解析（检测 YAML 语法错误）、qmd 集合初始化状态、摄入批次残留。
**退出码**：仅当阻塞项（非 INFO 类别）存在问题时返回 1；日志覆盖、Overview 占位、摄入批次残留、Domain 合规、Frontmatter 解析等非阻塞提示不影响退出码。
**退出码统一约定**：`0`=通过/EXIT_OK，`1`=结构性问题需修复/EXIT_BLOCKED（health/lint 通用），`2`=挂起需人工或 Agent 介入后重跑——lint 中表示等待 LLM 推理回传（EXIT_LLM_PENDING），ingest 中表示 slug 冲突或 concept 覆盖验证失败（EXIT_NEEDS_REVIEW），两者数值相同但触发条件不同，不可混用判断逻辑。
## 八、质量审计工作流（Lint Workflow）
触发：`lint` → `python -m Tools.lint [--save]`
频率：每次摄入批次（`[STOP] 批次已全部完成`）后，若本批次摄入了 3 个以上文件，立即运行一次 lint；否则可累积到下次较大批次或研究者显式要求时运行。lint 是幂等的，不确定时直接运行即可。
检查项：孤儿页（豁免 sources/ 和 syntheses/）、过时综述、缺失实体页（Raw 源文件链接已被排除）、稀疏页（仅统计 Wiki 内部出站双链）、Slug 冲突、图谱感知检查（可选）、加注缺失（LLM 辅助，检查所有来源目录的加注合规性）、知识盲区推荐（LLM 辅助）。
LLM 依赖项：加注缺失和知识盲区检查需要 Agent LLM 推理。首次运行时，lint 会将推理请求以 `[AGENT_LLM_REQUEST]` 形式输出并挂起（exit code 2）。Agent 完成推理后，应使用 `--apply-annotation-check` 或 `--apply-blind-spots` 参数回传结果，或将结果直接写入 `Wiki/_annotation_check_result.md` / `Wiki/_blind_spot_result.md` 文件，然后重新运行 lint 即可完成审计。缓存基于待检查词条集合的内容哈希自动刷新，确保条目变化时重新评估。
**退出码约定**同 §七。
## 九、知识图谱工作流（Graph Workflow）【可选扩展】
适用时机：知识库积累到 50+ 词条后再考虑启用。
触发：`build graph` → `python -m Tools.build_graph [选项]`
**核心参数**（所有参数均可组合使用）：
| 参数 | 作用 |
|------|------|
| `--no-infer` | 跳过语义推断（Pass 2），仅生成显式边图谱 |
| `--open` | 生成后自动在浏览器中打开 `graph.html` |
| `--report` | 输出图谱健康报告（含孤儿节点、上帝节点、社区结构等） |
| `--save` | 将报告保存至 `Graph/graph-report.md` |
| `--clean` | 删除推断检查点（`.inferred_edges.jsonl`），强制重新进行语义推断 |
| `--apply-inferred` | **合并先前保存的推断结果**（从 `Graph/.infer-results.json` 读取） |
**工作流分为两阶段**：
1. **Pass 1（显式边提取）**
   - 扫描所有 Wiki 页面的 `[[wikilink]]` 及 `related:` 字段中的语义标注（`# supports`、`# contradicts` 等）
   - 零 LLM 调用，自动过滤指向 `Raw/` 的链接
   - 输出基础边集，保存至 `graph.json` 的 `edges` 字段
2. **Pass 2（语义推断，Agent 辅助）**
   - 收集所有页面的摘要（ID、类型、前 500 字预览），写入 `Graph/.infer-context.json`
   - 通过 Agent 协议（`agent_llm`）一次性生成全局推断边：Agent 阅读上下文后输出严格 JSON 格式的边列表（含 `from`、`to`、`relationship`、`confidence`）
   - 推断结果自动写入 `Graph/.infer-results.json`，并更新缓存与检查点
**恢复与合并机制（避免重复累积）**：
- 首次运行 `build graph`（不含 `--no-infer`）会创建上下文文件，并提示 `[AGENT_PENDING]`，等待 Agent 完成推理。
- Agent 完成推理后，**必须**使用 `python -m Tools.build_graph --apply-inferred` 来合并结果，**不可**直接重新运行 `build_graph`，否则会触发完整的 Pass 1+Pass 2 流程，导致基础边和推断边被重新生成，可能造成重复累积。
- `--apply-inferred` 会重新提取基础边（确保与当前磁盘内容一致），然后只读入 `Graph/.infer-results.json` 中的推断边并合并，最后更新 `graph.json` 和 `graph.html`。
- 若想重新进行语义推断（例如上下文变化），先使用 `--clean` 清除检查点，再运行不带 `--apply-inferred` 的 `build_graph`。
**输出文件**：
- `Graph/graph.json`：包含 `nodes`、`edges`（显式）、`inferred_edges`（推断），以及 `inference_complete` 布尔标志。
- `Graph/graph.html`：交互式可视化（vis.js）
- `Graph/graph-report.md`（使用 `--save` 时生成）
- `Graph/.infer-context.json` / `Graph/.infer-results.json`（中间文件，已加入 `.gitignore`）
**完整性标记**：若因 Agent 异步推理未完成而导致推断不全，`graph.json` 中的 `inference_complete` 字段为 `false`，控制台会输出 `[NEEDS_REVIEW]` 信号，提示运行 `--apply-inferred` 补全。此时生成的报告和日志均会标注“不完整”。
**健康报告自动生成**：`--report` 会输出以下指标：
- 孤儿节点比例、上帝节点（度数 > μ+2σ）
- 社区数量与关键成员
- 社区间脆弱桥（仅一条边连接）
- Phantom hubs（被多次引用但不存在的新页建议）
- `contradicts` 边密度
**运行示例**：
```bash

# 首次构建（含推断，挂起等待 Agent 输入）

python -m Tools.build_graph

# Agent 将推理结果写入 Graph/.infer-results.json 后，合并

python -m Tools.build_graph --apply-inferred

# 仅生成显式边图谱（无推断）

python -m Tools.build_graph --no-infer

# 生成并打开图谱，同时输出健康报告并保存

python -m Tools.build_graph --open --report --save

# 重新推断（清空检查点）

python -m Tools.build_graph --clean

```
> **注意**：Pass 2 依赖 Agent 协议，需当前 Agent 响应推理请求。若 Agent 无法及时完成，可先使用 `--no-infer` 生成基础图谱，待后续合适时机再运行完整流程。
## 十、命名规范与索引格式
命名规范见 §三【命名规范】表格。所有 slug 全局唯一。
log.md 格式：
```

## [YYYY-MM-DD] ingest | <标题> | [[<Raw相对路径>]] | sha256:<前32位> | slug:<词条文件名>

## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<词条文件名>

## [YYYY-MM-DD] query-synthesis-update | <问题关键词> | slug:<词条文件名>

## [YYYY-MM-DD] health | <通过/N项阻塞问题>

## [YYYY-MM-DD] lint | <通过/N项严重问题>

## [YYYY-MM-DD] graph | 重建图谱 (<节点数> 节点, <边数> 边, <完整/不完整>)

## [YYYY-MM-DD] chore | <操作描述>

## [YYYY-MM-DD] ERROR | <操作> | <原因>

## [YYYY-MM-DD] ingest | no-concept | [[<Raw相对路径>]] （原因：<...>）

```
chore 协议：
- `chore: move <旧路径> -> <新路径>`：更新日志与所有双链，health 自动追踪新路径。
- `chore: rename Wiki/<旧路径> -> Wiki/<新路径>`：重命名文件，更新所有双链（含消歧导航页）、index.md，追加日志 `| slug:<新文件名去后缀>` 并 Git 提交。
- `chore: delete <Raw路径>`：标记删除，更新引用该 Raw 文件的词条，将其 sources 字段中的对应链接移除或标记为 `pending_review: true`，追加日志。
## 十一、临时文件处理规范
以下文件均已被 `.gitignore` 屏蔽，Agent 在 `git add` 前无需额外清理。
| 类型 | 文件路径 | 用途 |
|------|---------|------|
| Lint 上下文 dump | `Wiki/_semantic_lint_context.md` | 供 Agent 读取 |
| Lint 回传缓存 | `Wiki/_annotation_check_result.md`、`Wiki/_blind_spot_result.md` | 保留供重跑使用，含内容哈希用于自动失效 |
| 图谱推断上下文 | `Graph/.infer-context.json`、`Graph/.infer-results.json` | 保留供 Agent 交互 |
| 图谱缓存 | `Graph/.cache.json` | — |
| 查询 pending 文件 | `.qmd-pending-query.json` | — |
| 查询临时命中文件 | `.qmd-hits.json` | 单次查询中间产物，无需手动清理 |
| 摄入批次清单 | `.llm-wiki/ingest-queue.json` | 运行时临时状态 |
| 工具中间输出 | `Tools/__pycache__/`、`*.pyc` | — |
| 检索索引目录 | `.qmd/` | — |
| Obsidian 配置 | `.obsidian/`、`workspace.json` | — |
| 工具运行报告 | `Wiki/health-report.md`、`Wiki/lint-report.md` | 用户确认保存后手动 `git add -f` |
## 十二、已知限制
- （设计边界） lint 的加注缺失检查已针对所有来源目录全量检查；仍存在语义误判的可能，Agent 在词条写入时应人工确保加注合规。
- （操作提示） `query --apply` 时强烈建议提供原始问题文本，防止 pending 文件丢失导致综述标题降级。若遇到已存在综述，需显式追加 `--update`。
- （设计简化） LLM 推理完全依赖外部 Agent 捕获 `[AGENT_LLM_REQUEST]` 块并回传结果；非 Agent 环境暂不支持。
- （环境限制，无法在工具层修复） `glob` 等部分文件搜索工具在 Windows 上对中文通配符支持不稳定。
  **判定信号**：若 `Get-ChildItem -Filter "*<中文>*"` 或同类调用返回空结果但确认文件存在，立即切换至：`[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8; Get-ChildItem -Recurse -Filter "*中文*"`，不要重试同一条命令两次以上。
```
