# skills-study

用于研究与证据处理的 Agent Skills。每个技能可按其能力独立调用；需要多项能力协作时，统一遵循 [AGENTS.md](AGENTS.md) 和 [research-browser](research-browser/SKILL.md)。本 README 提供导航和安装说明，不另设路由、预算或执行规则。

## 技能入口

- [critical-reasoning](critical-reasoning/SKILL.md)：前提、证据、逻辑、数值和决策质量检查。
- [research-browser](research-browser/SKILL.md)：跨技能衔接、证据综合、工件、知识库和共享预算。
- [web-research](web-research/SKILL.md)：公开检索、网页读取、公开下载和研究综合。
- [edge-browser-research](edge-browser-research/SKILL.md)：获授权的本地 Edge 认证、论文检索、任务会话和下载；另见[使用说明](edge-browser-research/README.md)。
- [document-ingest](document-ingest/SKILL.md)：本地文档抽取、结构与出处定位、即时或持久化交接。
- [document-qa](document-qa/SKILL.md)：从已提供的文本或抽取工件检索、回答和核对覆盖。
- [image-analysis](image-analysis/SKILL.md)：图片 OCR、宿主视觉和经授权配置的中转分析。

独立调用仍需满足实际输入和工具条件。例如文档问答需要可读证据，但不要求先运行抽取技能；图片分析不要求文档 ID；下载验证可以在确认文件后结束。共享政策引用不会自动启动整个研究流程。详细选择和交接以两个路由入口为准。

## 安装与启用

将技能目录放入宿主支持的位置，或将仓库作为项目子模块并按宿主文档注册。安装位置不保证自动发现；不要假设宿主具有相同的扫描路径、信任机制、设置字段或重载命令，也不要覆盖已有技能目录。

全局或项目指令可使用以下入口，替换为实际路径：

```markdown
Before handling a request, read and follow <pack-root>/AGENTS.md.
Resolve relative paths in that file against <pack-root>/.
Reuse loaded instructions until they change.
```

`AGENTS.md` 不是技能，需要宿主上下文或明确入口加载。启用后检查宿主实际列出的技能与加载诊断。仓库内引用按所在文件的目录解析，无需随安装位置改写。

宿主提供的工具技能、安装技能和官方文档技能保留各自协议；它们不属于本仓库。宿主管理或包管理器安装的技能可能在升级时覆盖本地修改。

## 使用示例

```text
使用 document-qa，根据下面提供的文档文本回答问题，标注章节出处。
```

```text
使用 document-ingest 抽取这份本地 PDF，返回即时结果及未覆盖页面。
```

```text
使用 web-research 读取这个公开 URL，核实指定说法并给出原文依据。
```

```text
使用 image-analysis 分析这张图的表格；优先使用现有宿主视觉或本地 OCR。
```

```text
使用 research-browser，将本地报告与最新公开证据比较，说明差异与证据限制。
```

## 工件导航

完整政策由 [research-browser](research-browser/SKILL.md#work-directory-contract) 维护。以下仅说明常见路径：

```text
<workspace>/.agents-work/
├── <YYYY-MM-DD-task-slug>/
│   ├── index.md
│   ├── downloads/
│   ├── intermediates/
│   ├── documents/<doc_id>/
│   ├── images/<image-id>/
│   ├── search/
│   ├── web/
│   └── browser/session.json
└── knowledge/
    ├── index.md
    └── documents/<doc_id>/
```

一次性文档处理可使用 `immediate`，在内存交接文本、出处和覆盖限制；`persistent` 生成 `content.md`、`chunks.md`、`metadata.md`。知识库布局、维护授权与有效条目选择见[知识库政策](research-browser/SKILL.md#project-knowledge-base)。内部结构化交接不要求最终回复输出 JSON。

浏览器任务记录的字段和窗口生命周期见[任务会话参考](edge-browser-research/references/task-sessions.md)。公开浏览器会话机制见[公开浏览器参考](web-research/references/public-browser.md)。搜索、读取和多轮研究的内部参考分别位于 [search.md](web-research/references/search.md)、[reading.md](web-research/references/reading.md)、[research.md](web-research/references/research.md)，它们不是单独注册的技能。

## 维护与验证

- 技能入口包含 `name`、`description` frontmatter；技能执行正文用英语，用户说明可使用中文。
- 路由和跨技能调用顺序只在 AGENTS 与 research-browser 维护；其他文件引用规则，不复制另一套路由。
- 技能保留本能力的输入、操作、出处、错误处理和完成边界。新增限制应说明适用条件，避免把可选服务写成必需前提。
- 修改后检查 frontmatter、相对文件链接、标题锚点和 `git diff --check`。按代表性场景核对独立调用、缺失输入和协作衔接。
- 结构检查不证明真实站点权限、浏览器会话或模型能力。只有在相关执行逻辑改变且具备授权时，才运行所需的实际验证。
