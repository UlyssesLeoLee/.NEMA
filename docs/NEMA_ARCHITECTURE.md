# NEMA v1.1 基本设计（IPA 风格 / BD）

## 目的和职责

- NEMA：AI Agent 之间交换文本任务、普通表格及带说明的 Node–Edge 关系。
- IDE1.0：原生 `.nema` 文本编辑、可视化、手动压缩、导出、审查与回滚。
- IME1.0：在已授权 `.nema` 编辑上下文中自动提炼词典并在组合输入稳定提交后生成 `.nemat` 传输缓存；双端同时使用时拥有默认自动转换权。
- 共用库：Rust `nema-codec` (待实现)，单一确定性协议；本交付包中的 Python `codec` 是可执行参考模型与一致性金样例。

## 数据流

`IME 组合提交 / IDE 人工编辑 → 原生 .nema 快照 → 语法校验 → 自动词典候选 / 数字前缀 → tokenizer 真实计数或字节代理 → 无损往返校验 → .nemat sidecar 或 native fallback → Agent API / 本地交付`。

所有自动转换仅写传输 sidecar/cache，不直接将压缩数据回写到用户编辑的原文。输入阶段的 PascalCase 改写属于编辑器可见的语义编辑，须在 commit 前取得用户授权；压缩层不能私自进行类似改写。

## 容错与兼容

- 版本协商必须明确；v0.9 / v1.0 的 Tab-X 文件先走专用迁移器，不能做字符串全量 Tab→Space 替换。
- 解析器必须严格区分：领域 header 的 Tab，Table 标题入口的 Tab，`.nemat` 的 Tab `$` 与 Tab 数字，正文普通空格分列。
- 失败时回退原生文件；保存前比对快照 hash；冲突退出而不是猜测合并。
- 敏感值不自动入字典；不经授权不上传至云端 tokenizer 服务；推荐仅本地计数。

## 性能口径

主指标 = 相同语义与相同 payload 上，目标 tokenizer 对**完整请求**的 Token 总计数；还需要检查模型输出 Token、提示词学习费用、纠错次数和延迟。当前固定 SentencePiece 仅是分词代理，不代表用户商业 API 账单。

## 渲染层的 Hover/Inspector 分离（Website R3）

Graph AST 是唯一数据源：`X0 -> id+direction`、`X1 -> name`、`X2 -> optional description`。浏览器前端提供一层只读 HoverViewModel，Pointer/Focus 事件展示短卡片，Click/Enter/Space 更改 Inspector 选择状态。Hover 不触发数据修改、字典重算、IME 抢占或 AI 调用。参考 `GRAPH_HOVER_RENDERER_DESIGN.md`。
