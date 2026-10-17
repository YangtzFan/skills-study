# skills-study

面向研究任务的一组 Agent Skills：公开网络检索、机构认证浏览器访问、本地文档处理、证据问答和图片分析。技能是否自动发现、如何注册及何时重载，由宿主代理决定；安装目录本身不保证启用。

## 技能与职责

| 技能 | 职责 |
| --- | --- |
| [critical-reasoning](critical-reasoning/SKILL.md) | 每个请求的前提、证据、不确定性与回答质量检查。 |
| [research-browser](research-browser/SKILL.md) | 研究路由、跨来源综合、工件与外部调用预算的唯一规则来源。 |
| [web-search](web-search/SKILL.md) | 公开网络发现候选来源，不把搜索摘要当成正文证据。 |
| [web-reader](web-reader/SKILL.md) | 指定网页的正文、元数据、原文引用和来源交接。 |
| [edge-browser-research](edge-browser-research/SKILL.md)（[使用说明](edge-browser-research/README.md)） | 本地 Edge/Chromium 认证检索、论文下载验证、全局配置复用与按任务恢复窗口。 |
| [document-ingest](document-ingest/SKILL.md) | 文档抽取、结构与定位信息、即时或持久化交接。 |
| [document-qa](document-qa/SKILL.md) | 基于抽取结果检索、回答、引用，并核对覆盖范围。 |
| [image-analysis](image-analysis/SKILL.md) | 图片证据的 OCR、宿主视觉或经授权的中转模型分析。 |

`.system/` 中的宿主技能提供技能创建/安装、官方产品文档、图片生成等能力，不属于上述研究流水线。图片生成制作素材，图片分析解释证据；普通技能文件审查不因提及 Codex 而要求在线产品文档检索。

## 路由与交接

[AGENTS.md](AGENTS.md) 是全局轻量入口：所有请求应用 `critical-reasoning`；研究、文档证据、图片证据和知识库维护才加载 `research-browser`。代码、配置、提示词和技能审查直接读取文件；已有证据足够的后续问题不重复检索或抽取。

```text
AGENTS.md -> critical-reasoning（所有请求）
         -> research-browser（需要研究或证据处理时）
              公开发现：web-search -> web-reader
              机构数据库：edge-browser-research -> 候选/页面证据/下载记录
              页面正文：web-reader -> 必要时 image-analysis
              文档问答：document-ingest -> document-qa
              独立图片：image-analysis
              混合来源：research-browser 综合各项证据
```

指定 URL 直接读取，只有需要发现额外来源时才搜索。机构数据库通过本地浏览器检索；需要网页正文时交给 `web-reader`，需要论文内容时交给 `document-ingest` 和 `document-qa`。仅验证下载无需全文抽取。所有交接延续任务 ID、预算与已有证据；回读共享规则不重新启动路由。

文档一次性问答默认 `immediate`：内容、定位与覆盖限制在内存中交接，工件路径为 `null`。需要复用时使用 `persistent`，生成 `content.md`、`chunks.md`、`metadata.md`。内部结构化交接不要求最终回复输出 JSON。

## 安装与启用

将各技能目录放入宿主支持的技能位置，或将仓库挂载为项目子模块并按宿主文档注册。不要覆盖已有技能目录，也不要假设所有宿主支持相同的扫描路径、信任机制、设置字段或 `/skill:`、`/reload` 命令。

全局或项目指令可使用以下路由模板；将占位符替换为实际路径：

```markdown
Before handling any request, read and follow <pack-root>/AGENTS.md.
Resolve relative paths in that file against <pack-root>/.
```

`<pack-root>` 指技能包的实际安装或检出目录；技能内部保持相对路径。`AGENTS.md` 不是技能，不会仅因存在而自动注册；必须由宿主上下文或明确路由指令加载。Git 子模块也只完成获取与版本登记，不保证技能发现。

启用后检查宿主实际列出的技能和加载诊断，并确认入口文件可读。若需新增安装配置，按对应宿主的当前官方文档操作；本 README 不把某个宿主的发现行为推广到其他宿主。

## 工件与知识库

完整约束以 [research-browser 的 Work Directory Contract、Project Knowledge Base 和 Shared External Call Budget](research-browser/SKILL.md) 为准；下列为布局说明，不另设规则。

```text
<workspace>/.agents-work/
├── <YYYY-MM-DD-task-slug>/
│   ├── index.md           # 来源、用途、路径、状态
│   ├── browser/
│   │   └── session.json  # 经过筛选的任务页面恢复信息与检索进度
│   ├── downloads/         # 下载的 PDF、CAJ/KDH、图片等原始来源
│   ├── intermediates/     # 必要的渲染页、裁剪、处理缓存等
│   └── .../*.md           # 抽取正文、引用、研究记录
└── knowledge/
    ├── index.md
    └── documents/<doc_id>/
        ├── content.md
        ├── chunks.md
        └── metadata.md
```

工作区为任务的当前工作目录，任务内复用同一目录。证据记录与索引使用 UTF-8 Markdown；原始下载、必要处理文件和经过筛选的 `browser/session.json` 是明确例外。会话记录不是浏览器配置副本或原始 CDP 响应。用户原件保持原位只读。应用代码、技能实现和用户指定的产品素材遵循各自目标位置。

不创建无用途的目录或占位文件，不在研究工件中保存凭据、浏览器配置档、认证参数或原始服务响应。浏览器认证由操作系统上的专用全局配置保留，具体路径见 Edge 使用说明。宿主项目可在 `.gitignore` 中加入 `.agents-work/`；不自动修改用户忽略规则，任务会话记录不随技能代码提交。

知识库仅属于当前工作区，没有全局知识库。用户明确要求新增或更新背景资料时才入库；相关研究/文档任务读取索引，索引未变则复用，普通工程任务无需读取。`doc_id` 来自内容哈希，源文件改变后生成新 ID，并登记替代关系。知识库不是普遍真理，冲突保留来源和时效。

## 浏览器、预算与隐私

本地认证访问流程见 [Edge 技能](edge-browser-research/SKILL.md)，下载机制与现有 Python helper 接口见 [浏览器参考](web-reader/references/local-browser.md)。远程读取器不继承校园 IP、浏览器登录或本机代理路由；机构标识、文件下载、格式验证和全文可读性分别核验。

Edge 的[使用说明](edge-browser-research/README.md)覆盖 Windows/Linux 配置位置、新任务空白窗口、同一任务恢复和认证失效处理。各任务窗口共享登录与站点存储；任务记录保存在各自工作区。此技能提供代理执行规则，不是自动运行的浏览器扩展或独立会话管理程序。

网络检索、导航、下载、中转分析和远程检索共用一个任务预算，重试与供应商切换不重置。默认阈值、超时、计数方式和停止条件只在 `research-browser` 中维护。本地 DOM 检查和文件处理不消耗外部调用次数；费用遵循已有授权。

本地文档、私有/认证图片向第三方传输须获得明确授权；读取文件或已有密钥不等于上传许可。图片分析保留 OCR、宿主视觉与中转结果的来源区别；配置、能力和错误处理由 `image-analysis` 维护。用户在浏览器内完成密码、MFA 和 CAPTCHA，不导出认证会话。

## 维护与验证

- 每个技能入口为带 `name`、`description` 的 `SKILL.md`，技能正文用英语；中文用户说明由本 README 导航至相应技能的 README。
- 相对路径按包含该引用的文件所在目录解析；AGENTS 的路径按包根目录解析。安装位置改变无需改写跨技能引用。
- 共享规则维护单一来源，子技能保留能力特有的证据、覆盖与权限边界；详细浏览器机制不复制到多个入口。
- 修改后检查 frontmatter、实际引用路径、路由场景与 `git diff --check`；脚本行为改变时运行相应测试。结构验证不能证明真实站点权限或模型能力。
- `.system/` 是宿主管理的技能，更新可能覆盖本地改动；先区分包内协作问题与宿主技能本身的问题。
