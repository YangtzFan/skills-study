# skills-study

面向研究任务的一组 Agent Skills：公开网络检索、机构认证浏览器访问、本地文档处理、证据问答和图片分析。技能是否自动发现、如何注册及何时重载，由宿主代理决定；安装目录本身不保证启用。

## 技能与职责

| 技能 | 职责 |
| --- | --- |
| [critical-reasoning](critical-reasoning/SKILL.md) | 按任务影响与不确定性检查前提、证据、逻辑、数值和决策取舍；校准结论并随证据修正。 |
| [research-browser](research-browser/SKILL.md) | 研究路由、跨来源综合、工件与外部调用预算的唯一规则来源。 |
| [web-research](web-research/SKILL.md) | 公开网络搜索、指定网页读取、多轮研究与证据核验；按问题选择研究深度，无 Edge 前置依赖。 |
| [edge-browser-research](edge-browser-research/SKILL.md)（[使用说明](edge-browser-research/README.md)） | 仅在有可用 Edge 的环境下进行网页认证、学术数据库论文检索和论文下载；复用全局配置并按任务恢复窗口。 |
| [document-ingest](document-ingest/SKILL.md) | 文档抽取、结构与定位信息、即时或持久化交接。 |
| [document-qa](document-qa/SKILL.md) | 基于抽取结果检索、回答、引用，并核对覆盖范围。 |
| [image-analysis](image-analysis/SKILL.md) | 图片证据的 OCR、宿主视觉或经授权的中转模型分析。 |

`.system/` 中的宿主技能提供技能创建/安装、官方产品文档、图片生成等能力，不属于上述研究流水线。图片生成制作素材，图片分析解释证据；普通技能文件审查不因提及 Codex 而要求在线产品文档检索。

宿主专用技能保留各自的操作流程和来源选择；官方文档工具无需替换成强制的通用搜索流程，生成的产品素材也不自动成为研究工件。

## 路由与交接

[AGENTS.md](AGENTS.md) 是全局轻量入口：所有请求应用 `critical-reasoning`；研究、文档证据、图片证据和知识库维护才加载 `research-browser`。代码、配置、提示词和技能审查直接读取文件；已有证据足够的后续问题不重复检索或抽取。

跨技能职责分配与调用顺序以 [AGENTS.md](AGENTS.md) 和 [research-browser 的职责边界](research-browser/SKILL.md#worker-boundaries-and-direct-use) 为准；各技能保留自身的输入、操作、输出和能力约束，可按职责直接使用。读取共享约定不会强制重启路由或串联其他技能，只在目标需要额外能力或缺失输入证据时交接。

`critical-reasoning` 按任务需要分配检查力度：简单编辑、翻译与创作侧重意图和约束，不强制联网或套用论证模板；复杂或后果重大的问题核查关键假设、替代解释及可能改变结论的证据。缺失信息会实质影响结果且没有合理默认值时才澄清，否则按必要的明确假设继续。

推理检查区分事实、假设、推断与预测，关注因果解释、样本外推、单位、分母和比较基线；未检索到或无法读取不自动意味着不存在。建议依据用户目标和偏好权衡，并说明会改变建议的条件；新证据出现时修正具体结论，执行任务按可观察的完成标准核验。核验力度与任务相称，不另设研究预算，也不把结构校验通过当作实际行为保证。

```text
AGENTS.md -> critical-reasoning（所有请求）
         -> research-browser（需要研究或证据处理时）
              公开搜索、网页读取与多轮研究：web-research
              网页认证、数据库论文检索和论文下载：edge-browser-research（需 Edge）
              页面正文：web-research 读取模式
              文档抽取：document-ingest
              文档问答：document-qa（缺少抽取证据时才先抽取）
              独立图片：image-analysis
              混合来源：research-browser 综合各项证据
```

指定 URL 直接使用 `web-research` 的读取模式，只有需要发现额外来源时才搜索；仅搜索请求可返回候选来源而不逐页读取。公开文件直接下载由 `web-research` 完成；用户要求通过浏览器会话或机构访问下载论文时使用 Edge，公开下载不能替代机构权限验证。学术数据库论文检索通过获授权的 Edge 环境进行；需要网页正文时交给 `web-research`，需要文档抽取时交给 `document-ingest`，针对内容提问时才使用 `document-qa`。仅验证下载无需全文抽取。所有交接延续任务 ID、预算与已有证据；回读共享规则不重新启动路由。

仅抽取文档可在抽取结果处结束；已有抽取证据的问答无需重复抽取，独立图片分析无需文档 ID 或文档问答。文档抽取可使用本地 OCR 获取文字；页面或文档中的图表解读、宿主视觉和中转模型能力检查由 `image-analysis` 负责，抽取流程保留其来源标记和未覆盖内容。

`web-research` 合并了原 `web-search` 和 `web-reader` 的技能入口，规则见[搜索](web-research/references/search.md)、[读取](web-research/references/reading.md)和[多轮研究](web-research/references/research.md)。快速查询聚焦检索和核实；比较、争议问题和明确研究请求按子问题检索、读取原始来源，再针对重要证据缺口继续追查。研究深度不会自动增加共享预算；后续问题复用证据和计数。

搜索支持按问题选用多语言词、日期范围和相反证据，区分独立来源与转载；读取支持长网页定点查找，并明确摘要、局部正文与全文的覆盖范围。重要结论逐项对应已检查的证据，保留可用的工具原生引用，否则使用经核验的来源链接；不将搜索摘要或未打开的链接当作全文证据。

技能规范研究行为，不会自动安装搜索服务，也不保证与其他产品功能完全一致。接入模型 API 不代表已有搜索能力；实际能力取决于宿主暴露的工具或已配置且获授权的供应商。缺少搜索工具时如实说明，仍可按能力读取已知 URL，不用记忆模拟检索结果。没有 Edge 的机器仍可通过可用工具执行公开搜索、静态网页读取和公开文件下载。

通用网页搜索始终由 `web-research` 执行，禁止在 Edge 中操作搜索引擎，包括回退搜索。`edge-browser-research` 仅用于网页认证、学术数据库论文检索和论文下载，必须有可用且获授权的 Microsoft Edge，不以 Chromium 替代。公开页面需要 JavaScript 渲染本身不构成转入 Edge 的理由。旧 `web-reader` helper、测试及本地浏览器参考已删除，不再作为兼容资源调用。

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

本地认证与论文检索下载流程见 [Edge 技能](edge-browser-research/SKILL.md)，适用范围以 [AGENTS.md](AGENTS.md) 和 [research-browser](research-browser/SKILL.md) 为准。浏览器控制需要宿主提供的工具或可用 CDP 能力，本仓库不再提供旧 Python helper。远程读取器不继承校园 IP、浏览器登录或本机代理路由；机构标识、文件下载、格式验证和全文可读性分别核验。读取外部论文全文前须在任务 `downloads/` 中保留并验证获授权的全文文件，优先 PDF；仅有元数据或摘要不能称为全文审阅。

Edge 的[使用说明](edge-browser-research/README.md)覆盖 Windows/Linux 配置位置、新任务空白窗口、同一任务恢复和认证失效处理。各任务窗口共享登录与站点存储；任务记录保存在各自工作区。此技能提供代理执行规则，不是自动运行的浏览器扩展或独立会话管理程序。

网络检索、导航、下载、中转分析和远程检索共用一个任务预算，重试与供应商切换不重置。默认阈值、超时、计数方式和停止条件只在 `research-browser` 中维护。本地 DOM 检查和文件处理不消耗外部调用次数；费用遵循已有授权。

本地文档、私有/认证图片向第三方传输须获得明确授权；读取文件或已有密钥不等于上传许可。图片分析保留 OCR、宿主视觉与中转结果的来源区别；配置、能力和错误处理由 `image-analysis` 维护。用户在浏览器内完成密码、MFA 和 CAPTCHA，不导出认证会话。

## 维护与验证

- 每个技能入口为带 `name`、`description` 的 `SKILL.md`，技能正文用英语；中文用户说明由本 README 导航至相应技能的 README。
- 相对路径按包含该引用的文件所在目录解析；AGENTS 的路径按包根目录解析。安装位置改变无需改写跨技能引用。
- 共享规则维护单一来源，子技能保留能力特有的证据、覆盖与权限边界；详细浏览器机制不复制到多个入口。
- 修改后检查 frontmatter、实际引用路径、路由场景与 `git diff --check`；脚本行为改变时运行相应测试。结构验证不能证明真实站点权限或模型能力。
- `.system/` 是宿主管理的技能，更新可能覆盖本地改动；先区分包内协作问题与宿主技能本身的问题。
