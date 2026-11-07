> v1.3 authoritative Graph delta: `docs/GRAPH_V13_MIGRATION.md`. Node and Edge both start at X0; one leading space continues X2, two X3; domain header still begins with a literal Tab and is unchanged. Historical R7 text below, if quoted, is non-normative.

# IME1.0 对接 .NEMA v1.3 — 基本设计与详细设计

依据公开 IME1.0 的 `01_Source/crates/pime-core/`, `pime-ipc/`, `pime-tsf/`, `editor-bridges/vscode/` 布局，此方案为**拟开发工作**。Windows 系统 TSF 实机运行验证尚未被本交付覆盖。

## 默认工作流

编辑器焦点进入 `.nema` 或 Agent NEMA 字段，IME 将输入作为原生 `.nema` 语义意群收集；在 **TSF composition commit / editor buffer stable** 后请求共享 Codec 异步分析，自动提炼可复用词典，识别短 ID 公共前缀，估算 Token 成本并选择最优 `.nemat`。编辑器永远保留 `.nema` 原文，压缩只更新传输缓存或 agent request payload。

## 优先级（两端并用）

`IME.auto > IDE.auto (disabled)`, `IDE.manual > IME.auto`（仅这一次转换任务）。IME 通过 IPC 提供 `document_uri`,`editor_version`,`content_sha256`,`owner_token`,`operation=encode/decode`, `variant`, `dictionary_proposal`, `tokenizer`, `result_hash`；IDE 手动按钮抢占权限必须发出 cancel/relinquish 请求，且在 commit 版本回收旧 owner。不能让两个应用对同一个可编辑 buffer 重复提交。

## 字典算法

以重复字串频次、长度和 token 真成本构造候选；秘密扫描（API Key、JWT、private path）排除进字典与日志；只在 `candidate.score + protocol_cost < native.score` 时使用压缩，输入不稳定时不进行分析。所有 `\^`、`Tab+$N`、`Tab+数字` 的实际转义/语义遵照 `TRANSPORT_v1.3.md`，不让用户手动编造前缀。无收益原文回退。

## 安全、候选、撤销

组合输入期间不得将逐字变化发送云端，不得改变日中英普通输入行为。状态窗只展示“自动 / 原文回退 / 已压缩”的细粒度状态，详情可选；F1 AI 任务仍需现有授权/秘密扫描。AI 输出必须先过语法/版本/授权检查和事务提交，再可见，撤销恢复原编辑缓冲区。不自动修改 `.rs`、`.ts`、JSON、SQL 文件内容。

## 测试

UT：Graph Node 顶格识别、英文 `HTTPItIs`、中文/日文连写、多字母缩写边界、`\^`、词典碰撞、重试回退；IT：VS Code 提交/撤销、IPC 版本检查、IDE 手动抢占；ST：Windows 11 TSF IME 激活、焦点跨程序、失联恢复、500ms 内延迟预算、无权限回退。**这些真实产品集成测试尚未执行。**


## R7 语义一致性门禁

- 必须使用同一参考 `.NEMA` 原生解析器 / 无损 Codec 的 golden vectors。`parse`、`view`、Graph 悬停检查器、JSON 导出不得丢失 X3+ 扩展属性；X3 的 `APIKey`、`HTTP401` 保留字面拼写。
- 只在 Graph 的 X2 显示悬停说明。点击可展开 X3+，但不改变 Node/Edge 方向与文件数据；复制源码始终保留真实空格。
- IME1.0 默认提交后执行自动压缩；IDE1.0 仅在用户主动点击转换时覆盖自动触发。压缩前后通过逐字节解码往返校验，并对含 `\^`、普通数字和 `\ ` 的输入做对抗性测试。
- 产品集成仍是开发要求，不因本 R7 审查而宣称已经安装到两个仓库。
