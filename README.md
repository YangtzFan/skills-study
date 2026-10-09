# skills-study

`skills-study` 是一组面向支持 Agent Skills 规范的编码代理（Pi、Codex CLI 等）的技能，主要用于研究任务路由、网页检索、本地文档处理、证据问答以及图片分析。

本仓库既可以**全局安装**，作为所有工作区通用的技能包；也可以作为 **Git 子模块**挂载到某个仓库，只在该仓库内生效。

所有技能之间的引用都使用相对于技能目录的路径，工件写入当前工作区，因此安装路径和安装方式都不需要修改仓库内容。

## 技能列表

| 技能 | 作用 |
| --- | --- |
| `research-browser` | 统一入口，负责判断任务类型、选择其他技能并执行工件存储约束。 |
| `critical-reasoning` | 检查错误前提、证据强度、不确定性、风险和方案权衡。 |
| `web-search` | 搜索公开网络并返回经过排序的候选来源。 |
| `web-reader` | 读取指定网页，提取正文、元数据和可引用原文。 |
| `document-ingest` | 将本地文档转换为带来源定位信息的 Markdown 工件。 |
| `document-qa` | 基于已处理的本地文档回答问题并提供精确证据。 |
| `image-analysis` | 结合本地 OCR 与经授权的中转站视觉模型分析图片。 |

## 路由关系

```text
AGENTS.md
`-- research-browser
    |-- critical-reasoning
    |-- web-search
    |   `-- web-reader
    |       `-- image-analysis
    `-- document-ingest
        |-- image-analysis
        `-- document-qa
```

`critical-reasoning` 对所有请求生效。其他技能只在任务需要对应能力时加载。

路由按任务意图选择：代码、配置、提示词和技能审查直接读取文件；指定 URL 直接交给 `web-reader`，仅在需要发现额外来源时搜索；独立图片直接交给 `image-analysis`，不要求先生成 `doc_id`。显式加入知识库的请求优先走知识库维护流程。

文档处理有两种模式：一次性问答默认使用 `immediate`，在内存中交接抽取内容、定位信息和覆盖限制，产物路径为 `null`；需要复用的结果使用 `persistent`，写入三份 Markdown 工件并登记索引。知识库始终使用持久化模式。`document-qa` 同时支持即时交接和已有工件。

所有子技能共用 `research-browser` 的外部调用预算：默认每个逻辑操作最多 3 次请求、每个任务最多 20 次，每次超时 30 秒，外部流程总时限 300 秒。重试、改写查询、能力探测和切换供应商都消耗同一预算；认证失败不重复使用相同凭据重试。费用遵循用户已授权额度，不自动增加付费探测或切换到更贵的供应商。用户可明确指定其他预算。

## 安装

### 全局安装（推荐）

把仓库克隆到 Agent Skills 的全局目录：

```bash
git clone git@github.com:YangtzFan/skills-study.git ~/.agents/skills
```

Pi 会自动发现 `~/.agents/skills/` 下的全部技能，不需要额外配置技能路径。然后在 Pi 的用户级指令文件 `~/.pi/agent/AGENTS.md` 中添加入口路由：

```markdown
Before handling any request, read and follow @~/.agents/skills/research-browser/SKILL.md.
```

该文件对所有工作目录生效，因此全局安装的技能包会自动参与每一个会话。

### 项目内子模块

只需要在单个仓库中生效时，把本仓库作为子模块挂载：

```bash
git submodule add git@github.com:YangtzFan/skills-study.git skills-study
```

`git submodule add` 会同时完成克隆和登记，不需要再执行 `submodule update --init`（本仓库没有嵌套子模块）。子模块可以挂载到任意路径和任意目录名，因为技能内部引用全部相对于技能目录解析。

与普通子模块不同，挂载后的技能包**不会被自动发现**：代理只扫描 `.pi/skills/`、`.pi/extensions/` 等项目目录，以及 `.agents/skills/`（从工作目录向上找到仓库根）。`skills-study/web-search/SKILL.md` 不属于其中任何一个，所以需要下面两种方式之一。

**方式一：AGENTS.md 路由**（不需要项目信任）

```markdown
Before handling any request in this repository, read and follow [skills-study/research-browser/SKILL.md](skills-study/research-browser/SKILL.md).
```

模型把 `AGENTS.md` 当作上下文读入，再按其中的相对路径读取技能文件。实测项目未被信任时该文件依然加载。代价是技能不会注册成 `/skill:<name>` 命令，效果完全依赖模型遵守这条指令。

**方式二：显式注册**（需要项目信任，会注册 `/skill:<name>`）

在项目 `.pi/settings.json` 中登记挂载目录：

```json
{
  "skills": ["../skills-study"]
}
```

指向目录会递归注册其中全部 `SKILL.md`。注意项目设置里的路径**相对于 `.pi/` 解析**，所以要写 `../skills-study` 而不是 `skills-study`，也可以使用绝对路径或 `~` 开头的路径。`.pi/settings.json` 属于受项目信任保护的资源，未授予信任时整个文件被忽略，技能也就不会注册。

## 路径约定

- 跨技能引用使用相对于技能目录的路径，例如 `../web-search/SKILL.md` 指向同级的 `web-search` 技能。
- 技能包根目录是 `research-browser/SKILL.md` 所在目录的上一级目录。
- 新增或修改技能时不要写死绝对路径，也不要假设技能包的目录名。

## 工件目录

需要持久化的证据、抽取结果和中间工件统一写入当前工作区的任务目录：

```text
<workspace>/.agents-work/<task-id>/
```

`<workspace>` 是当前工作目录。该目录遵循以下约束：

- 只允许持久化 UTF-8 Markdown 文件。
- 每个任务使用独立的 `<task-id>` 目录，并通过 `index.md` 登记工件来源、用途和相对路径。
- `.agents-work/knowledge/` 是保留目录名，用于跨任务的项目知识库（见下一节），不会与 `<task-id>` 冲突，因为任务目录名始终以日期开头。
- JSON、HTML、PDF、图片、数据库和其他非 Markdown 文件不得持久化到该目录。
- 工具必须使用非 Markdown 文件时，应将其放入操作系统临时目录，并在完成 Markdown 转换后清理。
- 用户提供的源文件保持原位且只读。
- 不要把工件写进技能包目录，以保证技能包可以随时更新或重新克隆而不丢失证据。

工件位于宿主项目内，建议在宿主项目的 `.gitignore` 中添加：

```gitignore
.agents-work/
```

## 项目知识库

全局安装的技能包对所有项目共享，但背景资料通常只对某个项目有意义，因此每个工作区可以有自己的知识库：

```text
<workspace>/.agents-work/knowledge/
├── index.md                     # 登记每个文档的 doc_id、原始路径、主题、摘要、入库时间
└── documents/<doc_id>/
    ├── content.md
    ├── chunks.md
    └── metadata.md
```

在该项目的工作区里直接提出请求即可：

- `把 docs/architecture.pdf 加入本项目知识库`
- `把 ~/specs/api-v3.docx 和 ./manual/ 目录下的文档都加入知识库`
- `列出本项目知识库`
- `把已过期的 x.pdf 从知识库移除`

处理时走 `document-ingest` 的知识库模式：原始文件保持在原位且只读，知识库只保存 Markdown 派生件，并更新 `index.md`。`doc_id` 取自文件内容的哈希，因此源文件改动后会产生新的 `doc_id`，重新入库即可，不会错误复用旧内容。

之后该项目内的每次任务都会先读取 `knowledge/index.md`，只在相关时加载具体文档，所以背景知识不必反复提供，也不会无条件占用上下文。

知识库始终属于当前工作区，**不存在全局知识库**：全局安装只决定技能文件放在哪里，不会把技能包目录、agent 目录或其他用户级位置变成数据存放处；不同工作区的背景文档互不共享，也不会被提升到共享位置。如果某个工作区没有 `.agents-work/knowledge/`，就视为没有背景文档。

知识库是项目级证据而非普遍真理：当它与更新的权威来源冲突时，应同时报告两者并说明时效，而不是静默取舍。

## 图片分析与隐私

`image-analysis` 在本地 OCR 可用时使用它作为独立基线，并可使用宿主已有的图像理解能力，或在配置和授权均满足时请求中转站中的 `Image 2` 等支持图片输入的模型。OCR 不可用或失败时必须明确报告，不能把视觉模型输出标记为 OCR，也不会自动安装依赖。

中转配置来自当前用户明确提供的设置或宿主指定的配置位置，至少包含 `endpoint`、`protocol`、`credential_ref` 和有图片输入能力依据的有序 `models` 列表；匿名接口需明确标记。凭据引用只能是宿主密钥引用或环境变量名，不能写入字面密钥。没有配置时不扫描无关文件寻找密钥，也不猜测接口。

- 上传本地、私有或需要认证的图片前，必须获得用户明确许可。
- 不得猜测中转站地址、密钥、协议或模型标识。
- OCR、宿主视觉能力和中转模型结果必须分别标注来源，不能用模型输出静默覆盖 OCR。
- 中转站请求失败时，即使 OCR 成功，也必须报告经过脱敏的失败信息。
- 凭据、认证头、签名 URL 和敏感请求内容不得写入日志或工件。

## 维护约定

- 每个技能位于独立目录中，入口文件固定为 `SKILL.md`。
- `SKILL.md` 必须包含标准 YAML frontmatter，并至少提供 `name` 和 `description`。
- 所有 `SKILL.md` 使用英语；中文说明集中在本 README 中。
- 不要在英文句子中间进行硬换行。
- 跨技能引用统一使用 `../<skill>/SKILL.md` 形式，不要引入绝对路径或依赖安装目录名。
- 新增或修改技能后，在技能可被发现的位置启动代理，检查启动诊断是否有加载告警，并确认 `/skill:<name>` 命令可用；同时检查 Markdown 代码围栏、内部路径和工作目录约束。

技能自带的参考材料放在该技能目录内部（例如 `<skill>/references/`），随仓库提交。包根目录不再保留 `references/` 约定，因为按 Agent Skills 规范 `references/` 是单个技能的附属目录，包根目录下的同名目录没有实际用途。
