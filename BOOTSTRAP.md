# LLM Wiki 仓库创建提示词

**本文件用途**：将本文件复制到任意空白目录，交给一个具备文件系统与 Shell 工具的 AI Agent（如 Claude Code、Cursor、OpenCode 等）。  
Agent 阅读本文件后，将在该目录中完整创建一个符合 LLM Wiki 规范的知识操作系统骨架，所有工具脚本在 bootstrap 阶段一次性写入。  
**当前版本**：v1.0

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

在写入任何文件之前，通过一次对话确认以下三项。若用户拒绝回答或说“用默认”，使用括号内的默认值：

1. **Raw 层目录**：使用默认四类目录（Sources / Thoughts / Records / Assets），还是自定义？（默认：四类默认目录。若自定义，请用户列出目录名、各自的加注类型以及是否参与摄入；若未说明“是否摄入”则默认为 `true`。自定义后将完全不使用默认目录，所有后续 Raw 子目录规则均以用户提供的映射为准，包括 raw-mapping.json）
2. **Git 远程**：是否配置 origin？若是，提供 URL。（默认：暂不配置）
3. **知识领域（domain）枚举**：使用顿号分隔的列表，默认 **哲学、历史、宗教、文学、自然科学、技术、经济、其他**。是否增删？（默认：使用以上枚举。Agent 将据此生成 `.llm-wiki/domain-enum.json`，并将枚举列表写入 AGENTS.md §3.1 的说明中，同时将枚举中的第一项写入 frontmatter 示例的 domain 字段注释里。）

### 1.2 验证目标目录

目标目录为当前工作目录（`.`）——即本 bootstrap 文件所在的目录，所有后续步骤直接在 `.` 下操作。

```bash
ls -la .
```

- 目录为空（仅含本 bootstrap 文件）→ 直接继续
- 目录非空（含其他文件）→ 警告用户，要求显式确认是否在此目录继续

### 1.3 创建物理目录结构

用 `mkdir -p` 一次性创建所有目录。注意：

- `Wiki/` 下各子目录**绝对禁止再建子文件夹**，但必须将以下五个子目录全部创建：`concepts/`、`entities/`、`sources/`、`syntheses/`、`disambiguations/`
- `Raw/` 下仅预建用户在 §1.1 确认的子目录（默认四个；自定义则只建用户指定的目录）。用户随后可自行在这些子目录下创建更深的归档子目录，Agent 扫描时会递归发现，加注映射始终以 Raw 根下第一级子目录为准。
- `.llm-wiki/` 目录在此步骤创建；`raw-mapping.json` 和 `domain-enum.json` 在 §1.4 写入 AGENTS.md 后立即生成
- `Graph/` 初始仅预建根目录；`graph.json` / `graph.html` / `graph-report.md` 由 `build_graph.py` 运行时自动生成
- `Tools/` 立即创建空文件 `Tools/__init__.py`（执行 `touch Tools/__init__.py`）
- **任何子目录下均不创建 README.md**

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

- 一句话定位：这是个人 LLM 知识库，`Raw/` 放原始材料，`Wiki/` 是结构化沉淀。
- Raw 层目录说明：详细结构及加注规则见 `.llm-wiki/raw-mapping.json`。
- Wiki 层用户可见分类（`sources` / `syntheses` 标注为自动生成，研究者无需手动管理）。
- 快速上手：
  1. 把文件放进 `Raw/` 对应子目录
  2. 在 AI 会话中说 `ingest <路径>` 开始摄入（或说 `ingest` 恢复已有批次）
  3. 说 `query: <问题>` 触发查询
- 完整操作规程见 **AGENTS.md**（本文件无需重复指令细节，仅作定位与引导）。
- qmd 集合初始化提示：若已安装 qmd 但未初始化集合，健康检查会提示缺失，届时需运行：`qmd init --collection wiki Wiki/` 和 `qmd init --collection raw Raw/`
- Obsidian 设置提示：Settings -> Files and links 中将 Attachment 路径设为 `Raw/Assets`，将 New link format 设置为 Absolute path in vault
- Graph 层说明（标注为可选）：说 `build graph` 可生成知识图谱，前 50 次摄入无需使用

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

---

#### Tools/common.py

```python
import hashlib
import json
import os
import re
import subprocess as _sp
import sys
import tempfile
import unicodedata
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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

def _check_cli(cmd: str) -> bool:
    try:
        _sp.run([cmd, "--version"], capture_output=True, timeout=5, check=True)
        return True
    except Exception:
        pass
    try:
        _sp.run([sys.executable, "-m", cmd, "--version"], capture_output=True, timeout=5, check=True)
        return True
    except Exception:
        pass
    if sys.platform == "win32":
        try:
            _sp.run(["powershell", "-NoProfile", "-Command", f"& '{cmd}' --version"],
                    capture_output=True, timeout=5, check=True)
            return True
        except Exception:
            pass
    return False

QMD_AVAILABLE: bool = _check_cli("qmd")
MARKITDOWN_AVAILABLE: bool = _check_cli("markitdown")

def _run_qmd(args: List[str], **kwargs):
    """运行 qmd 命令，自动处理 Windows .ps1 兼容。"""
    if sys.platform == "win32":
        try:
            return _sp.run(["qmd"] + args, **kwargs)
        except Exception as e_qmd:
            try:
                loc = _sp.run(
                    ["powershell", "-NoProfile", "-Command", "(Get-Command qmd).Source"],
                    capture_output=True, timeout=10
                )
                ps1_path = loc.stdout.decode("utf-8", errors="replace").strip()
                if ps1_path:
                    try:
                        return _sp.run(["powershell", "-NoProfile", "-File", ps1_path] + args, **kwargs)
                    except Exception as e_ps:
                        print(f"WARN: 通过 PowerShell 调用 qmd 也失败: {e_ps}")
            except Exception:
                pass
            raise e_qmd
    else:
        return _sp.run(["qmd"] + args, **kwargs)

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

# 以下两个常量从 WIKI_SYSTEM_FILES 派生，保证一致性
WIKI_ROOT_SPECIAL_FILES: Set[str] = {"index.md", "log.md", "overview.md"}
WIKI_ROOT_SPECIAL_STEMS: Set[str] = {Path(f).stem for f in WIKI_ROOT_SPECIAL_FILES}

def extract_wikilinks(text: str) -> List[str]:
    raw = re.findall(r"\[\[([^\]]+)\]\]", text)
    targets = [item.split("|")[0].strip() for item in raw]
    return list(dict.fromkeys(targets))

def all_wiki_pages() -> List[Path]:
    if not WIKI_DIR.exists():
        return []
    return sorted(
        p for p in WIKI_DIR.rglob("*.md")
        if p.name not in WIKI_SYSTEM_FILES
    )

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

def parse_ingest_records(log_text: str) -> List[Tuple[str, str, str, str]]:
    pattern = re.compile(
        r"^## (\d{4}-\d{2}-\d{2}) ingest \| .+? \| \[\[(.+?)\]\] "
        r"\| sha256:([0-9a-f]{32}) \| slug:(\S+)",
        re.MULTILINE
    )
    return [(m.group(1), m.group(2), m.group(3), m.group(4)) for m in pattern.finditer(log_text)]

def parse_frontmatter(content: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result

def check_slug_conflict(
    slug: str,
    target_dir: str,
    operation_type: str,
    raw_rel: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """检查 slug 冲突。raw_rel 为 None 时任何同名文件均视为冲突。"""
    for subdir in ("concepts", "entities", "sources", "syntheses", "disambiguations"):
        target_path = WIKI_DIR / subdir / f"{slug}.md"
        if target_path.exists():
            if raw_rel and LOG_FILE.exists():
                log_text = LOG_FILE.read_text(encoding="utf-8")
                slug_raws: Set[str] = set()
                for _, rec_raw, _, rec_slug in parse_ingest_records(log_text):
                    if rec_slug == slug:
                        slug_raws.add(rec_raw)
                if raw_rel in slug_raws:
                    continue
            if raw_rel:
                content = read_file(target_path)
                fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                if fm_match:
                    fm_text = fm_match.group(1)
                    sources_field = re.search(r"sources:\s*\[([^\]]*)\]", fm_text)
                    if sources_field and normalize_path_str(raw_rel) in normalize_path_str(sources_field.group(1)):
                        continue
                    raw_link_field = re.search(r"raw_link:\s*['\"]?\[\[([^\]]*)\]\]", fm_text)
                    if raw_link_field and normalize_path_str(raw_rel) == normalize_path_str(raw_link_field.group(1)):
                        continue
            return True, target_path.relative_to(REPO_ROOT).as_posix()
    if LOG_FILE.exists() and raw_rel:
        log_text = LOG_FILE.read_text(encoding="utf-8")
        slug_to_raws: Dict[str, set] = {}
        for _, rec_raw, _, rec_slug in parse_ingest_records(log_text):
            slug_to_raws.setdefault(rec_slug, set()).add(rec_raw)
        if slug in slug_to_raws and raw_rel not in slug_to_raws[slug]:
            return True, f"log.md: slug '{slug}' 已被不同源文件使用: {slug_to_raws[slug]}"
    return False, None

def parse_log_slugs(log_text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for _, _, _, slug in parse_ingest_records(log_text):
        result[slug] = "ingest"
    # 匹配 query-synthesis 和 query-synthesis-update
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

def parse_moved_paths(log_text: str) -> Dict[str, str]:
    move_pattern = re.compile(
        r"^## (\d{4}-\d{2}-\d{2}) chore \| move: (.+?) -> (.+?)",
        re.MULTILINE
    )
    matches = list(move_pattern.finditer(log_text))
    matches.sort(key=lambda m: m.group(1))  # 按日期排序，防止日志乱序影响链式追踪
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
    parse_ingest_records, QMD_AVAILABLE, _run_qmd,
    WIKI_ROOT_SPECIAL_STEMS,
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
    excluded_names = WIKI_ROOT_SPECIAL_STEMS
    for rel, p in pages.items():
        stem = p.stem
        if stem in excluded_names:
            continue
        subdir = Path(rel).parts[1] if len(Path(rel).parts) > 1 else ""
        if stem not in slug_map:
            issues.append(f"日志覆盖缺失: {rel}")
        elif subdir == "syntheses" and slug_map[stem] != "query-synthesis":
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
        r"^## .+? chore \| delete: (.+?)",
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
    excluded_names = WIKI_ROOT_SPECIAL_STEMS
    for rel, p in pages.items():
        if p.stem in excluded_names:
            continue
        content = read_file(p)
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        fm_text = fm_match.group(1)
        # 块标量格式提示（非阻塞，INFO 级别）
        if re.search(r"^domain:\s*[>|]", fm_text, re.MULTILINE):
            issues.append(f"domain 使用了块标量格式（> 或 |），建议改为单行标量: {rel}")
            continue
        m = re.search(r"^domain:\s*(.+)", fm_text, re.MULTILINE)
        if not m:
            continue
        domain_val = m.group(1).strip().strip('"').strip("'")
        if domain_val and domain_val not in allowed:
            issues.append(f"domain 值非法: {rel}（值：{domain_val}，合法枚举：{', '.join(allowed)}）")
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
        "qmd集合状态": check_qmd_collections(),
        "摄入批次残留": check_ingest_queue_residual(),
    }

    # Domain 合规现在为非阻塞 INFO 级别，块标量格式及非法值均不会导致 health 失败
    NON_BLOCKING = {"日志覆盖", "Overview占位", "摄入批次残留", "Domain合规"}

    # 仅非阻塞项不计入 exit code 判定
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

    return 0 if passed else 1

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
    find_pages_by_raw_source, parse_ingest_records, qmd_embed_wiki,
    parse_frontmatter,
)

CONTENT_PREVIEW_CHARS = 4000
MAX_BYTES = 500_000
DEFAULT_BATCH_SIZE = 5

SUPPORTED_EXTS = {".md", ".txt", ".pdf", ".docx", ".pptx", ".xlsx", ".html", ".epub"}

# ──────────────────────────────────────────────
# 候选文件自然排序（中文卷号排序支持）
# ──────────────────────────────────────────────

_CHN_DIGIT = dict(zip('零一二三四五六七八九', range(10)))

def _chn_num_to_int(s: str) -> int:
    if not s:
        return 0
    n, cur = 0, 0
    for ch in s:
        if ch in _CHN_DIGIT:
            cur = _CHN_DIGIT[ch]
        elif ch == '十':
            n += cur * 10 if cur else 10
            cur = 0
        elif ch == '百':
            n += (cur or 1) * 100
            cur = 0
        elif ch == '千':
            n += (cur or 1) * 1000
            cur = 0
    return n + cur

def _series_grp(name: str) -> str:
    if name.startswith('Sliced_'):
        rest = name[7:]
    else:
        rest = name
    m = re.match(r'^([^_]+)', rest)
    if m:
        return m.group(1)
    return rest

def _extract_vol(name: str) -> int:
    """从文件名提取卷号数字，优先取卷/附录/前言等结构化标记，其次取首段数字。"""
    # 前言固定卷号 0
    if '前言' in name:
        return 0
    # 附录固定卷号 999
    if '附录' in name:
        return 999
    # 中文数字卷标：卷五/第十二卷/卷十二等
    m = re.search(r'[卷第]([' + ''.join(_CHN_DIGIT) + '十百千]+)', name)
    if m:
        return _chn_num_to_int(m.group(1))
    # 中文数字+顿号：一二、四五等
    m = re.search(r'([' + ''.join(_CHN_DIGIT) + '十百千]+)、', name)
    if m:
        return _chn_num_to_int(m.group(1))
    # 阿拉伯数字前缀
    m = re.match(r'.*?(\d+)', name)
    if m:
        return int(m.group(1))
    # 无编号者排最后
    return 9999

def _candidate_sort_key(f: Path) -> tuple:
    name = f.stem
    if name.startswith('Sliced_'):
        name = name[7:]
    series = _series_grp(name)
    vol = _extract_vol(name)
    return (series, vol, name)

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

def _collect_candidates_from_args(targets: List[str]) -> List[str]:
    log_index = _load_log_index()
    allowed_dirs = load_allowed_raw_dirs()
    ingest_map = {d["name"]: d.get("ingest", True) for d in allowed_dirs}
    seen = set()
    result = []

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
                           key=_candidate_sort_key)
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
            # 已有 source_map 则视为已摄入（比 log_index SHA 更可靠）
            if _has_source_map_for_raw(rel):
                continue
            if rel in log_index and sha256_file(f) == log_index[rel]:
                continue
            result.append(rel)

    result.sort(key=lambda rel: _candidate_sort_key(REPO_ROOT / rel))
    return result

def _collect_all_pending() -> List[str]:
    log_index = _load_log_index()
    try:
        allowed = load_allowed_raw_dirs()
    except (FileNotFoundError, ValueError) as e:
        print(f"WARN: 无法加载目录配置：{e}")
        return []
    ingest_dirs = [d["name"] for d in allowed if d.get("ingest", True)]
    result = []
    for dir_name in ingest_dirs:
        dir_path = RAW_DIR / dir_name
        if not dir_path.exists():
            continue
        for f in sorted(dir_path.rglob("*"), key=_candidate_sort_key):
            if not f.is_file() or f.suffix.lower() not in SUPPORTED_EXTS:
                continue
            rel = normalize_path_str(f.relative_to(REPO_ROOT).as_posix())
            # 已有 source_map 则视为已摄入（比 log_index SHA 更可靠）
            if _has_source_map_for_raw(rel):
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
        return existing["pending"][0]

    if not candidates:
        print("OK: 暂无需要摄入或更新的文件。")
        if INGEST_QUEUE_FILE.exists():
            INGEST_QUEUE_FILE.unlink()
        return None

    total_candidates = len(candidates)
    # ── 改进的分组批次逻辑：优先保证组间多样性 ──
    groups: Dict[str, List[str]] = {}
    for c in candidates:
        nc = normalize_path_str(c)
        grp = _series_grp(Path(nc).stem)
        groups.setdefault(grp, []).append(nc)
    # 按每组大小降序排序
    sorted_groups = sorted(groups.items(), key=lambda x: -len(x[1]))
    batch: List[str] = []
    # 轮询取文件，直至填满批次或所有组耗尽
    group_iters = [iter(files) for _, files in sorted_groups]
    while len(batch) < DEFAULT_BATCH_SIZE and group_iters:
        progressed = False
        for it in list(group_iters):
            try:
                f = next(it)
                batch.append(f)
                progressed = True
                if len(batch) >= DEFAULT_BATCH_SIZE:
                    break
            except StopIteration:
                group_iters.remove(it)
        if not progressed:
            break

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
    queue_mode = queue_data.get("mode", "normal")  # 读取批次模式

    if raw_rel in done:
        remaining = len(pending)
        if remaining == 0:
            print("[STOP] 批次已全部完成。")
        else:
            if queue_mode == "discuss":
                print(f"\nINFO: 批次进度：{len(done)}/{queue_data.get('total', len(done) + remaining)} 完成，剩余 {remaining} 个。")
                print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
            else:
                print(f"[CONTINUE] 立即执行：python -m Tools.ingest")
        return 0

    if raw_rel in skipped:
        skipped.remove(raw_rel)
        done.append(raw_rel)
        queue_data["skipped"] = skipped
        queue_data["done"] = done
        _write_queue(queue_data)
        print(f"INFO: {raw_rel} 此前被标记为跳过，现已补做完成。")
        remaining = len(pending)
        if remaining == 0:
            print("[STOP] 批次已全部完成。")
        else:
            if queue_mode == "discuss":
                print(f"\nINFO: 批次进度：{len(done)}/{queue_data.get('total', len(done) + remaining)} 完成，剩余 {remaining} 个。")
                print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
            else:
                print(f"[CONTINUE] 立即执行：python -m Tools.ingest")
        return 0

    if raw_rel not in pending:
        print("[STOP] 该文件不属于当前批次。")
        return 0

    if no_concept and subdir == "sources" and slug not in no_concept_slugs:
        no_concept_slugs.append(slug)
        queue_data["no_concept_slugs"] = no_concept_slugs

    pending.remove(raw_rel)
    done.append(raw_rel)
    queue_data["pending"] = pending
    queue_data["done"] = done

    remaining = len(pending)
    total = queue_data.get("total", len(done) + remaining)

    if remaining > 0:
        _write_queue(queue_data)
        print(f"\nINFO: 批次进度：{len(done)}/{total} 完成，剩余 {remaining} 个。")
        if queue_mode == "discuss":
            print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
        else:
            print(f"[CONTINUE] 立即执行：python -m Tools.ingest")
        return 0

    blocked, report, _ = _run_batch_end_validation(queue_data, force=force)
    if not blocked:
        _finalize_batch(queue_data)
        return 0

    # NEEDS_REVIEW：将当前文件插回队首
    pending.insert(0, raw_rel)
    done.remove(raw_rel)
    queue_data["pending"] = pending
    queue_data["done"] = done
    _write_queue(queue_data)

    print(
        f"[NEEDS_REVIEW] 批次末尾 concept/entity 覆盖验证失败：\n" +
        "\n".join(f"  - {line}" for line in report) +
        f"\n\n请为以上 source_map 补充对应的 concept/entity 词条后，"
        f"重新执行 --finalize（或使用 --force 跳过验证）。"
    )
    return 2

def _check_concept_coverage(done_rels: List[str], no_concept_slugs: List[str]) -> Tuple[bool, List[str], List[str]]:
    """
    返回 (是否阻断, 人类可读报告, 缺失覆盖的 raw_rel 列表)。
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
        sources_str = fm.get("sources", "")
        sources_links = extract_wikilinks(sources_str)
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
        if pending:
            if queue_mode == "discuss":
                print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
            else:
                print(f"[CONTINUE] 立即执行：python -m Tools.ingest")
        else:
            print("[STOP] 批次已全部完成。")
        return

    if raw_rel in skipped:
        if pending:
            if queue_mode == "discuss":
                print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
            else:
                print(f"[CONTINUE] 立即执行：python -m Tools.ingest")
        else:
            print("[STOP] 批次已全部完成。")
        return

    if raw_rel in pending:
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
            for mr in missing_raws:
                if mr in done:
                    done.remove(mr)
                    pending.insert(0, mr)
            if missing_raws:
                queue_data["pending"] = pending
                queue_data["done"] = done
                _write_queue(queue_data)
                print(
                    f"[NEEDS_REVIEW] 批次末尾 concept/entity 覆盖验证失败，"
                    f"已将缺失的源文件放回队列头部。\n"
                    f"验证失败详情：\n" +
                    "\n".join(f"  - {line}" for line in report) +
                    f"\n\n请补充对应词条后重新执行 --finalize，或使用 --force 跳过验证。"
                )
            else:
                print(
                    f"[NEEDS_REVIEW] 批次末尾 concept/entity 覆盖验证失败：\n" +
                    "\n".join(f"  - {line}" for line in report) +
                    f"\n\n请补充对应词条后重新执行 --finalize，或使用 --force 跳过验证。"
                )
    else:
        print(f"\nINFO: 已跳过，批次剩余 {remaining} 个。")
        if queue_mode == "discuss":
            print(f"[DISCUSS_CONTINUE] 请继续为剩余文件执行 --finalize，无需重新运行 python -m Tools.ingest。")
        else:
            print(f"[CONTINUE] 立即执行：python -m Tools.ingest")

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
        print(f"INFO: {raw_rel} 已摄入且哈希未变，跳过日志/index 更新。")
    else:
        if normalized_rel not in log_index:
            conflict, existing_src = check_slug_conflict(
                slug, subdir, "ingest", raw_rel=normalized_rel
            )
            if conflict:
                print(f"[NEEDS_REVIEW] Slug 冲突：{subdir}/{slug}.md 已被其他来源占用（{existing_src}）。\n"
                      f"请为本词条指定新的 slug。")
                return 2

        _update_index(slug, subdir, title, brief=brief)
        _write_ingest_log(title, raw_rel, file_hash, slug)
        git_add_commit([WIKI_DIR], f"ingest: {title}")
        qmd_embed_wiki()
        print(f"OK: 摄入完成：{title}（slug: {slug}，存入 Wiki/{subdir}/）")

    result = _advance_queue(
        normalized_rel, subdir=subdir, slug=slug, title=title,
        force=force, no_concept=no_concept,
    )

    if no_concept and result != 2:
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
        description="LLM Wiki 摄入工具 v2.4",
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

    # Bug-1 修复：预读失败的文件立即从队列移除，不进入讨论
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
    # 缺陷-2 修复：输出明确的流控信号，Agent 据此进入等待讨论状态
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
    parse_frontmatter, parse_ingest_records,
    normalize_path_str, is_raw_path,
    WIKI_ROOT_SPECIAL_FILES, WIKI_ROOT_SPECIAL_STEMS,
)

GRAPH_JSON = REPO_ROOT / "Graph" / "graph.json"
SEMANTIC_CONTEXT = WIKI_DIR / "_semantic_lint_context.md"
ANNOTATION_RESULT_FILE = WIKI_DIR / "_annotation_check_result.md"
BLIND_SPOT_RESULT_FILE = WIKI_DIR / "_blind_spot_result.md"

def _get_last_ingest_date(raw_rel: str) -> str:
    if not LOG_FILE.exists():
        return ""
    log_text = read_file(LOG_FILE)
    dates = [d for d, rel, _, _ in parse_ingest_records(log_text) if rel == raw_rel]
    return max(dates) if dates else ""

def check_orphan_pages() -> list:
    pages = list(all_wiki_pages())
    inbound: set = set()
    excluded_stems = WIKI_ROOT_SPECIAL_STEMS

    for page in pages:
        content = read_file(page)
        for link in extract_wikilinks(content):
            if is_raw_path(link):
                continue
            resolved = resolve_wikilink(link)
            if resolved:
                inbound.add(str(resolved))

    issues = []
    for page in pages:
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

        sources_str = fm.get("sources", "")
        source_links = re.findall(r"\[\[([^\]]+)\]\]", sources_str)

        raw_paths_set: set = set()
        for link in source_links:
            if is_raw_path(link):
                raw_paths_set.add(link)
            else:
                resolved = resolve_wikilink(link)
                if resolved and resolved.exists():
                    ref_content = read_file(resolved)
                    ref_fm = parse_frontmatter(ref_content)
                    ref_sources = re.findall(
                        r"\[\[([^\]]+)\]\]", ref_fm.get("sources", "")
                    )
                    for rs in ref_sources:
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

def check_missing_entities() -> list:
    link_count: dict = {}
    pages = list(all_wiki_pages())
    entities_dir = WIKI_DIR / "entities"
    existing_entities = {p.stem for p in entities_dir.rglob("*.md")} if entities_dir.exists() else set()

    for page in pages:
        content = read_file(page)
        for link in set(extract_wikilinks(content)):
            if is_raw_path(link): 
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

def check_sparse_pages() -> list:
    issues = []
    excluded_stems = WIKI_ROOT_SPECIAL_STEMS
    for page in all_wiki_pages():
        if page.stem in excluded_stems:
            continue
        content = read_file(page)
        non_raw_links = [l for l in extract_wikilinks(content) if not is_raw_path(l)]
        if len(non_raw_links) < 2:
            issues.append(
                f"稀疏页: {page.relative_to(REPO_ROOT).as_posix()}（仅 {len(non_raw_links)} 条出站双链）"
            )
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
    if not LOG_FILE.exists():
        return []
    log_text = read_file(LOG_FILE)

    slug_to_raws: dict = {}
    for _, raw_rel, _, slug in parse_ingest_records(log_text):
        slug_to_raws.setdefault(slug, set()).add(raw_rel)

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

    root_special = WIKI_ROOT_SPECIAL_FILES
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
        sources_str = fm.get("sources", "")
        raw_paths = re.findall(r"\[\[([^\]]+)\]\]", sources_str)
        if any(
            is_raw_path(rp)
            and len(Path(rp).parts) >= 2
            and Path(rp).parts[1] in dir_names
            for rp in raw_paths
        ):
            pages_with_sources.append((page, raw_paths, ""))

    checks = {
        "孤儿页": check_orphan_pages(),
        "过时综述": check_stale_syntheses(),
        "缺失实体页": check_missing_entities(),
        "稀疏页": check_sparse_pages(),
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
        return 2

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

    return 0 if passed else 1

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

运行方式：
  python -m Tools.query <问题>
  python -m Tools.query <问题> --save --slug <slug>
  python -m Tools.query --apply --slug <slug> --answer "<答案文本>" [<问题>]
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
    qmd_embed_wiki, _run_qmd,
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
        return 2

    if not is_existing_synthesis:
        conflict, existing = check_slug_conflict(slug, "syntheses", "query-synthesis", raw_rel=None)
        if conflict:
            print(f"[NEEDS_REVIEW] slug 冲突：{slug}.md 已存在于其他词条类型（来源：{existing}）。\n"
                  f"综述页 slug 须全局唯一，请指定新的 slug。")
            return 2

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
    sources_yaml = json.dumps(sources_list, ensure_ascii=False)

    if is_existing_synthesis and update:
        old_content = read_file(synth_path)
        old_fm_match = re.match(r"^---\n(.*?)\n---", old_content, re.DOTALL)
        old_sources: List[str] = []
        old_status = "open"
        old_open_questions = "[]"
        if old_fm_match:
            fm_text = old_fm_match.group(1)
            m_src = re.search(r"sources:\s*(\[.*?\])", fm_text)
            if m_src:
                try:
                    old_sources = json.loads(m_src.group(1))
                except Exception:
                    old_sources = []
            m_status = re.search(r"^status:\s*(\w+)", fm_text, re.MULTILINE)
            if m_status:
                old_status = m_status.group(1)
            m_oq = re.search(r"open_questions:\s*(\[.*?\])", fm_text)
            if m_oq:
                old_open_questions = m_oq.group(1)

        merged_sources = list(dict.fromkeys(old_sources + sources_list))
        merged_sources_yaml = json.dumps(merged_sources, ensure_ascii=False)

        content = (
            f"---\n"
            f"title: \"{escaped_title}\"\n"
            f"type: synthesis\n"
            f"tags: []\n"
            f"sources: {merged_sources_yaml}\n"
            f"status: {old_status}\n"
            f"open_questions: {old_open_questions}\n"
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
        f"sources: {sources_yaml}\n"
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
                  f"  python -m Tools.query \"{escaped_question}\" --apply --slug {slug} --answer \"<答案>\"{update_flag}\n")
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
    parser.add_argument("--qmd-hits", default="", dest="qmd_hits",
                        help="外部 qmd 检索结果文件路径（JSON 数组）")
    args = parser.parse_args()

    if args.apply:
        if not args.answer or not args.slug:
            print("WARN: --apply 需要同时提供 --slug 和 --answer")
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
                           apply_answer=args.answer, source_hits=source_hits,
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
"""
LLM Wiki 知识图谱生成工具（可选扩展）。
建议知识库积累 50+ 词条后再使用。

运行方式：python -m Tools.build_graph [--open] [--report] [--save] [--no-infer] [--apply-inferred]
"""

import argparse
import json
import re
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List

from Tools.common import (
    REPO_ROOT, WIKI_DIR, GRAPH_DIR,
    read_file, write_file, append_log,
    extract_wikilinks, all_wiki_pages, resolve_wikilink,
    agent_llm, git_add_commit, load_graph_json, parse_frontmatter,
    WIKI_ROOT_SPECIAL_FILES, is_raw_path,
)

GRAPH_JSON = GRAPH_DIR / "graph.json"
GRAPH_HTML = GRAPH_DIR / "graph.html"
GRAPH_REPORT = GRAPH_DIR / "graph-report.md"
INFER_CTX = GRAPH_DIR / ".infer-context.json"
INFER_RES = GRAPH_DIR / ".infer-results.json"

VALID_RELATION_TYPES = {"supports", "contradicts", "extends", "depends_on", "related"}

EDGE_COLORS = {
    "contradicts": "#ff4444",
    "INFERRED": "#aaaaaa",
    "default": "#888888",
}

def _extract_nodes_edges():
    EXCLUDE_DIRS = {"syntheses", "disambiguations"}
    root_special = WIKI_ROOT_SPECIAL_FILES
    nodes: dict = {}
    edges: list = []
    seen_edges: set = set()

    pages = all_wiki_pages()
    for page in pages:
        rel = page.relative_to(WIKI_DIR).as_posix()
        parts = Path(rel).parts
        subdir = parts[0] if len(parts) > 1 else ""

        content = read_file(page)
        fm = parse_frontmatter(content)
        node_id = rel

        if rel in root_special:
            nodes[node_id] = {
                "id": node_id,
                "label": fm.get("title", page.stem) or page.stem,
                "domain": "",
                "degree": 0,
            }
            continue

        nodes[node_id] = {
            "id": node_id,
            "label": fm.get("title", page.stem) or page.stem,
            "domain": fm.get("domain", ""),
            "degree": 0,
        }

        if subdir in EXCLUDE_DIRS:
            continue

        # 提取正文 wikilinks，跳过 Raw 链接
        for link in extract_wikilinks(content):
            if is_raw_path(link):
                continue
            resolved = resolve_wikilink(link)
            if not resolved or resolved == page.resolve():
                continue
            # 仅接受 Wiki 层内的链接
            try:
                target_id = resolved.relative_to(WIKI_DIR).as_posix()
            except ValueError:
                continue
            edge_key = (node_id, target_id)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append({
                    "from": node_id,
                    "to": target_id,
                    "type": "EXTRACTED",
                    "relation": "related",
                })

        # 处理 related 字段，同样跳过 Raw 链接
        related_str = fm.get("related", "")
        for raw_link in re.findall(r"\[\[([^\]]+)\]\]", related_str):
            link_name = raw_link.split("|")[0].strip()
            if is_raw_path(link_name):
                continue
            anno_match = re.search(
                rf"{re.escape(link_name)}\#\s*(\w+)",
                content
            )
            relation = "related"
            if anno_match and anno_match.group(1) in VALID_RELATION_TYPES:
                relation = anno_match.group(1)

            resolved = resolve_wikilink(link_name)
            if not resolved:
                continue
            try:
                target_id = resolved.relative_to(WIKI_DIR).as_posix()
            except ValueError:
                continue
            edge_key = (node_id, target_id, relation)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append({
                    "from": node_id,
                    "to": target_id,
                    "type": "EXTRACTED",
                    "relation": relation,
                })

    for e in edges:
        if e["from"] in nodes:
            nodes[e["from"]]["degree"] += 1
        if e["to"] in nodes:
            nodes[e["to"]]["degree"] += 1

    return list(nodes.values()), edges

def _validate_inferred_edges(inferred_edges: list, node_ids: set) -> list:
    """校验推断边的 from/to 是否真实存在于节点列表中，返回有效边列表 [Bug C 修复]"""
    valid_edges = []
    ghost_count = 0
    for e in inferred_edges:
        from_ok = e.get("from", "") in node_ids
        to_ok = e.get("to", "") in node_ids
        if from_ok and to_ok:
            valid_edges.append(e)
        else:
            ghost_count += 1
            if ghost_count <= 5:
                missing = []
                if not from_ok:
                    missing.append(f"from='{e.get('from')}'")
                if not to_ok:
                    missing.append(f"to='{e.get('to')}'")
                print(f"  WARN: 推断边引用不存在的节点：{', '.join(missing)}，已丢弃")
    if ghost_count > 5:
        print(f"  WARN: 共 {ghost_count} 条推断边引用了不存在的节点（仅显示前 5 条）")
    if ghost_count > 0:
        print(f"  INFO: 推断边校验完成：{len(valid_edges)}/{len(inferred_edges)} 条有效")
    return valid_edges

def _get_edge_color(e: dict) -> str:
    if e.get("relation") == "contradicts":
        return EDGE_COLORS["contradicts"]
    if e.get("type") == "INFERRED":
        return EDGE_COLORS["INFERRED"]
    return EDGE_COLORS["default"]

def _generate_html(nodes: list, edges: list, inferred_edges: list) -> str:
    all_edges = edges + inferred_edges
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps([
        {
            "from": e["from"],
            "to": e["to"],
            "color": {"color": _get_edge_color(e)},
            "dashes": e.get("type") == "INFERRED",
            "title": e.get("relation", ""),
        }
        for e in all_edges
    ], ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>LLM Wiki 知识图谱</title>
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin: 0; background: #1a1a2e; }}
  #graph {{ width: 100vw; height: 100vh; }}
  #info {{ position: fixed; top: 10px; left: 10px; color: #eee;
    background: rgba(0,0,0,.6); padding: 8px 14px; border-radius: 6px;
    font-family: sans-serif; font-size: 13px; }}
  .legend {{ margin-top: 8px; }}
  .legend span {{ display: inline-block; width: 20px; height: 3px;
    vertical-align: middle; margin-right: 4px; }}
</style>
</head>
<body>
<div id="info">
  LLM Wiki 知识图谱 | 节点: {len(nodes)} | 边: {len(all_edges)}
  <div class="legend">
    <span style="background:#ff4444"></span>contradicts
    <span style="background:#aaaaaa"></span>inferred
  </div>
</div>
<div id="graph"></div>
<script>
var nodes = new vis.DataSet({nodes_json});
var edges = new vis.DataSet({edges_json});
var container = document.getElementById('graph');
var options = {{
  nodes: {{ shape: 'dot', size: 8,
    color: {{ background: '#4a9eff', border: '#2176c4' }},
    font: {{ color: '#fff', size: 12 }} }},
  edges: {{ arrows: 'to', smooth: {{ type: 'dynamic' }} }},
  physics: {{ stabilization: {{ iterations: 200 }} }},
}};
new vis.Network(container, {{ nodes: nodes, edges: edges }}, options);
</script>
</body>
</html>"""

def _generate_report(nodes: list, edges: list, inferred_edges: list) -> str:
    today = date.today().isoformat()
    all_edges = edges + inferred_edges

    root_special = WIKI_ROOT_SPECIAL_FILES
    active_nodes = [n for n in nodes if n["id"] not in root_special]
    degrees = {n["id"]: n["degree"] for n in active_nodes}
    deg_values = list(degrees.values())
    mu = statistics.mean(deg_values) if deg_values else 0
    sigma = statistics.stdev(deg_values) if len(deg_values) >= 2 else 0
    threshold = mu + 2 * sigma

    god_nodes = [n for n in active_nodes if n["degree"] > threshold]
    orphan_nodes = [n for n in active_nodes if n["degree"] == 0]
    contradicts = [e for e in all_edges if e.get("relation") == "contradicts"]

    density = len(all_edges) / max(len(active_nodes), 1)
    orphan_ratio = len(orphan_nodes) / max(len(active_nodes), 1)

    lines = [
        f"# 图谱健康报告 {today}\n\n",
        "## 健康摘要\n\n",
        f"| 指标 | 数值 |\n|------|------|\n",
        f"| 活跃节点数 | {len(active_nodes)} |\n",
        f"| 边数（含推断边）| {len(all_edges)} |\n",
        f"| 边/节点比 | {density:.2f} |\n",
        f"| 孤儿占比 | {orphan_ratio:.1%} |\n",
        f"| contradicts 边占比 | {len(contradicts)/max(len(all_edges),1):.1%} |\n\n",
        "## 上帝节点（God Nodes）\n\n",
    ]
    if god_nodes:
        for n in god_nodes:
            lines.append(f"- {n['id']}（度数 {n['degree']}，mu+2sigma={threshold:.1f}）\n")
    else:
        lines.append("无上帝节点。\n")

    lines.append("\n## 孤儿节点\n\n")
    if orphan_nodes:
        for n in orphan_nodes[:20]:
            lines.append(f"- {n['id']}\n")
    else:
        lines.append("无孤儿节点。\n")

    return "".join(lines)

def run_build_graph(
    open_browser: bool = False,
    report: bool = False,
    save: bool = False,
    no_infer: bool = False,
    apply_inferred: bool = False,
) -> int:
    today = date.today().isoformat()
    GRAPH_DIR.mkdir(exist_ok=True)

    inferred_edges: list = []

    if apply_inferred:
        if not INFER_RES.exists():
            print("WARN: 未找到 Graph/.infer-results.json，无法应用推断边。")
            return 1
        inferred_data = json.loads(INFER_RES.read_text(encoding="utf-8"))
        print("Pass 1（重新提取）：从磁盘重新提取显式双链...")
        nodes, edges = _extract_nodes_edges()
        # 合并前校验推断边 [Bug C 修复]
        node_ids = {n["id"] for n in nodes}
        inferred_edges = _validate_inferred_edges(
            [e for e in inferred_data.get("inferred_edges", []) if e.get("type") == "INFERRED"],
            node_ids
        )
        print(f"OK: 重新提取完成，合并 {len(inferred_edges)} 条推断边。")
    elif GRAPH_JSON.exists():
        existing = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
        nodes = existing.get("nodes", [])
        edges = existing.get("edges", [])
        print("INFO: 已加载现有 graph.json，如需要请使用 --apply-inferred 合并推断边。")
    else:
        print("Pass 1：提取显式双链...")
        nodes, edges = _extract_nodes_edges()
        print(f"  完成：{len(nodes)} 个节点，{len(edges)} 条边。")

        base_graph = {
            "nodes": nodes,
            "edges": edges,
            "inferred_edges": [],
            "built": today,
        }
        write_file(GRAPH_JSON, json.dumps(base_graph, ensure_ascii=False, indent=2))
        print("OK: 基础 graph.json 已写入（Pass 1 结果，尚无推断边）。")

    if not no_infer:
        context_items = []
        for n in nodes:
            page = resolve_wikilink(n["id"])
            if not page:
                continue
            content = read_file(page)
            core_def = ""
            m = re.search(r"## 核心定义\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
            if m:
                core_def = m.group(1).strip()[:500]
            context_items.append({
                "id": n["id"],
                "label": n["label"],
                "domain": n["domain"],
                "core_def": core_def,
            })
        INFER_CTX.write_text(
            json.dumps({"nodes": context_items}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        infer_prompt = (
            f"请阅读以下 {len(context_items)} 个知识库词条的摘要（见 Graph/.infer-context.json），"
            f"推断词条之间潜在的语义关联边。\n\n"
            f"输出格式（严格 JSON，不含任何 Markdown 包装）：\n"
            f'{{"inferred_edges": [{{"from": "词条A.md", "to": "词条B.md", '
            f'"confidence": 0.8, "relation": "supports|contradicts|extends|depends_on|related", '
            f'"type": "INFERRED"}}]}}\n\n'
            f"关系类型：supports=支持/印证, contradicts=矛盾/否定, "
            f"extends=扩展/细化, depends_on=依赖/前提, related=一般关联\n\n"
            f"节点列表见 Graph/.infer-context.json"
        )
        result = agent_llm(infer_prompt, output_var="INFERRED_EDGES")

        if result and result != "[AGENT_PENDING]":
            try:
                clean = result.replace("```json", "").replace("```", "").strip()
                inferred_data = json.loads(clean)
                inferred_edges = inferred_data.get("inferred_edges", [])
                for e in inferred_edges:
                    e["type"] = "INFERRED"

                # 校验推断边
                node_ids = {n["id"] for n in nodes}
                inferred_edges = _validate_inferred_edges(inferred_edges, node_ids)

                INFER_RES.write_text(
                    json.dumps({"inferred_edges": inferred_edges}, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"OK: Pass 2 完成，生成 {len(inferred_edges)} 条推断边。")
            except Exception as e:
                print(f"WARN: Pass 2 结果解析失败: {e}，跳过推断边（基础图谱已保存）。")
                inferred_edges = []
        elif result == "[AGENT_PENDING]":
            print(
                f"\nPass 2（语义推断）：已生成 Graph/.infer-context.json（{len(context_items)} 个节点）。\n"
                f"当前 Agent 请完成推断任务，将 JSON 结果写入 Graph/.infer-results.json，\n"
                f"再运行：python -m Tools.build_graph --apply-inferred\n"
                f"（基础图谱 Pass 1 结果已保存至 Graph/graph.json）"
            )
            html = _generate_html(nodes, edges, [])
            write_file(GRAPH_HTML, html)
            print("OK: 基础 graph.html 已写入（不含推断边）。")
            git_add_commit([GRAPH_DIR], f"graph: Pass 1 基础图谱 ({len(nodes)} 节点)")
            append_log(f"## [{today}] graph | Pass 1 基础图谱 ({len(nodes)} 节点, {len(edges)} 边)")
            return 0
    else:
        print("INFO: Pass 2 跳过（--no-infer 指定）。")

    graph_data = {
        "nodes": nodes,
        "edges": edges,
        "inferred_edges": inferred_edges,
        "built": today,
    }
    write_file(GRAPH_JSON, json.dumps(graph_data, ensure_ascii=False, indent=2))
    html = _generate_html(nodes, edges, inferred_edges)
    write_file(GRAPH_HTML, html)
    print(f"OK: graph.json 和 graph.html 已写入（{len(nodes)} 节点，{len(edges)} 边，{len(inferred_edges)} 推断边）。")

    if report:
        report_text = _generate_report(nodes, edges, inferred_edges)
        if save:
            write_file(GRAPH_REPORT, report_text)
            print("OK: 图谱健康报告已保存至 Graph/graph-report.md")
        else:
            print("\n" + report_text)

    git_add_commit([GRAPH_DIR], f"graph: rebuild ({len(nodes)} 节点, {len(edges)+len(inferred_edges)} 边)")
    append_log(f"## [{today}] graph | 重建图谱 ({len(nodes)} 节点, {len(edges)+len(inferred_edges)} 边)")

    if open_browser:
        try:
            import webbrowser
            webbrowser.open(str(GRAPH_HTML))
        except Exception:
            print(f"请手动打开: {GRAPH_HTML}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Wiki 知识图谱生成工具")
    parser.add_argument("--open", action="store_true", help="生成后在浏览器中打开 graph.html")
    parser.add_argument("--report", action="store_true", help="生成图谱健康报告")
    parser.add_argument("--save", action="store_true", help="将报告保存至 Graph/graph-report.md")
    parser.add_argument("--no-infer", action="store_true", help="跳过 Pass 2 语义推断")
    parser.add_argument("--apply-inferred", action="store_true", help="重新提取基础边并合并推断结果（防止重复累积）")
    args = parser.parse_args()
    sys.exit(run_build_graph(
        open_browser=args.open,
        report=args.report,
        save=args.save,
        no_infer=args.no_infer,
        apply_inferred=args.apply_inferred,
    ))
```

---

### 1.10 初始化 Git 仓库

```bash
git init
git branch -M main
git config user.name 2>/dev/null | grep -q . || git config --local user.name "LLM Wiki Agent"
git config user.email 2>/dev/null | grep -q . || git config --local user.email "llm-wiki@local"
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
find . -type f | sort
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

## §2 AGENTS.md 模板

Agent 请将以下内容**原样写入**目标库的 `AGENTS.md` 文件。  
**不要写入本节最外层的 ` ```markdown ` 起始行和结尾的 ` ``` ` 行**（它们是本提示词的边界标记）。  
AGENTS.md 内部词条模板（§3.1–§3.5）中的 ` ```markdown ` 代码块标记**应原样保留**，它们是用于向 Agent 展示格式的示例。

```markdown
# AGENTS.md（最高操作契约）

<!-- version: v1.0 | created: <YYYY-MM-DD> -->

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
| `query: <问题>` | 查询工作流（Step 1） | `qmd query "<问题>" --collection wiki --format json -n 8 > .qmd-hits.json` | 必须先执行，将结果传给 Step 2 |
| （接上）查询工作流（Step 2） | | `python -m Tools.query "<问题>" --qmd-hits .qmd-hits.json` | qmd 不可用时直接执行 Step 2（脚本自动降级） |
| `query: <问题> --save --slug <slug>` | 查询并归档 | 同上两步，Step 2 附加 `--save --slug <slug>` | — |
| `query --apply --slug <slug> --answer "<答案>"` | 完成归档 | `python -m Tools.query "<问题>" --apply --slug <slug> --answer "<答案>"` | Agent 完成 LLM 推理后继续保存（建议带上原始问题文本） |
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
sources: [""]
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

domain 字段应使用单行 YAML 标量格式（如 `domain: "哲学"`）。若使用多行块标量写法，health 会以 INFO 级别提示使用单行格式，不会阻断。

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
sources: [""]
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
（向 Wiki/concepts/ 建立辐射双链）
[[概念]]：一句话说明关联（据文献）

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

WARN: 审计守则：若原始笔记未明确指明流派或语境，默认不写入任何消歧专页，输出警告，挂起等待研究者人工确认后分配。
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
- 若来源确实不含可提取概念（纯数据表、日程、个人记录等），在对应文件的 `--finalize` 中传入 `--no-concept --no-concept-reason "<原因>"` 豁免该文件；豁免记录写入 log.md
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

检查项：空文件/存根页、索引同步、日志覆盖（区分 ingest 和 query-synthesis 来源）、Overview 占位、断链、Assets 断链、Raw 目录合规、哈希一致性（含 move/delete 追踪，当关联词条已标记 pending_review 时不再重复报告）、pending_review 扫描、Domain 合规（块标量格式及非法值以 INFO 级别提示）、qmd 集合初始化状态、摄入批次残留。

**退出码**：仅当阻塞项（非 INFO 类别）存在问题时返回 1；日志覆盖、Overview 占位、摄入批次残留、Domain 合规等非阻塞提示不影响退出码。

## 八、质量审计工作流（Lint Workflow）

触发：`lint` → `python -m Tools.lint [--save]`

频率：每次摄入批次（`[STOP] 批次已全部完成`）后，若本批次摄入了 3 个以上文件，立即运行一次 lint；否则可累积到下次较大批次或研究者显式要求时运行。lint 是幂等的，不确定时直接运行即可。

检查项：孤儿页（豁免 sources/ 和 syntheses/）、过时综述、缺失实体页（Raw 源文件链接已被排除）、稀疏页（仅统计 Wiki 内部出站双链）、Slug 冲突、图谱感知检查（可选）、加注缺失（LLM 辅助，检查所有来源目录的加注合规性）、知识盲区推荐（LLM 辅助）。

LLM 依赖项：加注缺失和知识盲区检查需要 Agent LLM 推理。首次运行时，lint 会将推理请求以 `[AGENT_LLM_REQUEST]` 形式输出并挂起（exit code 2）。Agent 完成推理后，应使用 `--apply-annotation-check` 或 `--apply-blind-spots` 参数回传结果，或将结果直接写入 `Wiki/_annotation_check_result.md` / `Wiki/_blind_spot_result.md` 文件，然后重新运行 lint 即可完成审计。缓存基于待检查词条集合的内容哈希自动刷新，确保条目变化时重新评估。

## 九、知识图谱工作流（Graph Workflow）【可选扩展】

适用时机：知识库积累到 50+ 词条后再考虑启用。

触发：`build graph` → `python -m Tools.build_graph [--open] [--report] [--save] [--no-infer]`

- Pass 1：提取显式双链，零 LLM 调用，已自动过滤 Raw 链接
- Pass 2：语义推断隐性关联边，通过 Agent LLM 协议完成
- `--apply-inferred`：重新提取基础边后合并推断结果，防止多次运行导致推断边重复累积

**Pass 2 挂起后的恢复路径**：若首次运行时 Pass 2 返回 `[AGENT_PENDING]`，Agent 完成推断并将结果写入 `Graph/.infer-results.json` 后，**必须使用 `--apply-inferred` 参数**而非直接重新运行 `build_graph`。直接重新运行会触发完整的 Pass 1+Pass 2 流程，覆盖已有的 `graph.json` 基础边结果。

## 十、命名规范与索引格式

命名规范见 §三【命名规范】表格。所有 slug 全局唯一。

log.md 格式：
```
## [YYYY-MM-DD] ingest | <标题> | [[<Raw相对路径>]] | sha256:<前32位> | slug:<词条文件名>
## [YYYY-MM-DD] query-synthesis | <问题关键词> | slug:<词条文件名>
## [YYYY-MM-DD] query-synthesis-update | <问题关键词> | slug:<词条文件名>
## [YYYY-MM-DD] health | <通过/N项阻塞问题>
## [YYYY-MM-DD] lint | <通过/N项严重问题>
## [YYYY-MM-DD] graph | 重建图谱 (<节点数> 节点, <边数> 边)
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

- （设计简化） domain 字段使用多行块标量写法时，health 会以 INFO 级别提示使用单行格式，不会影响功能。
- （设计边界） lint 的加注缺失检查已针对所有来源目录全量检查；仍存在语义误判的可能，Agent 在词条写入时应人工确保加注合规。
- （操作提示） `query --apply` 时强烈建议提供原始问题文本，防止 pending 文件丢失导致综述标题降级。若遇到已存在综述，需显式追加 `--update`。
- （设计简化） LLM 推理完全依赖外部 Agent 捕获 `[AGENT_LLM_REQUEST]` 块并回传结果；非 Agent 环境暂不支持。
- （操作提示） `glob` 工具在 Windows 上不支持中文通配符。搜索含中文的文件时，改用 bash + Get-ChildItem：`[Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8; Get-ChildItem -Recurse -Filter "*中文*"`
```
