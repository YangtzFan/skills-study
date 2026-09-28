# skills-study

`skills-study` 是一组面向 Codex CLI 的仓库级技能，主要用于研究任务路由、网页检索、本地文档处理、证据问答以及图片分析。

本仓库可以作为 Git 子模块使用，只需在父仓库通过 `AGENTS.md` 将所有请求路由到 `research-browser`，再由该技能根据任务类型加载其他技能。

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

## 作为子模块使用

将本仓库挂载到父仓库根目录的 `skills-study`：

```bash
git submodule add git@github.com:YangtzFan/skills-study.git skills-study
git submodule update --init --recursive
```

在父仓库的 `AGENTS.md` 中添加路由：

```markdown
Before handling any request in this repository, read and follow [skills-study/research-browser/SKILL.md](skills-study/research-browser/SKILL.md).
```

当前技能文件使用 `skills-study/...` 形式的仓库相对路径，因此子模块应保持该目录名。如果挂载到其他路径，需要同步修改所有内部引用和父仓库路由。

## 工件目录

需要持久化的证据、抽取结果和中间工件统一写入：

```text
skills-study/work-dir/<task-id>/
```

该目录遵循以下约束：

- 只允许持久化 UTF-8 Markdown 文件。
- 每个任务使用独立的 `<task-id>` 目录，并通过 `index.md` 登记工件来源、用途和相对路径。
- JSON、HTML、PDF、图片、数据库和其他非 Markdown 文件不得持久化到该目录。
- 工具必须使用非 Markdown 文件时，应将其放入操作系统临时目录，并在完成 Markdown 转换后清理。
- 用户提供的源文件保持原位且只读。

`work-dir/` 和 `references/` 默认由本仓库的 `.gitignore` 排除，不会随正常提交进入版本库。

## 图片分析与隐私

`image-analysis` 始终使用本地 OCR 作为独立基线，并可在配置和授权均满足时请求中转站中的 `Image 2` 或其他支持图片输入的模型。

- 上传本地、私有或需要认证的图片前，必须获得用户明确许可。
- 不得猜测中转站地址、密钥、协议或模型标识。
- OCR 结果与模型结果必须分别保留，不能用模型输出静默覆盖 OCR。
- 中转站请求失败时，即使 OCR 成功，也必须报告经过脱敏的失败信息。
- 凭据、认证头、签名 URL 和敏感请求内容不得写入日志或工件。

## 维护约定

- 每个技能位于独立目录中，入口文件固定为 `SKILL.md`。
- `SKILL.md` 必须包含标准 YAML frontmatter，并至少提供 `name` 和 `description`。
- 所有 `SKILL.md` 使用英语；中文说明集中在本 README 中。
- 不要在英文句子中间进行硬换行。
- 新增或修改技能后，应运行 Codex 的 skill 校验器，并检查 Markdown 代码围栏、内部路径和工作目录约束。
