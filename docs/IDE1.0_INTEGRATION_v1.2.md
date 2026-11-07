# IDE1.0 对接 .NEMA v1.2 — 基本设计与详细设计

依据已检查的公开 IDE1.0 仓库结构（`crates/ide-kernel-core`, `ide-kernel`, `ide-shell`, `ide-shell-web`, `ide-shell-desktop`, `ide-cli`），以下是**拟开发方案**而不是已经合入仓库的功能。

## 权责

IDE 默认仅实时解析与展示 `.nema`，可以切换“原始空格 / ·/⇥ 可视化”但复制保持真实字符。Graph Node/Edge 支持悬停 X2、点击详情、无向/正反向箭头、键盘/触屏。用户手动点击“压缩转换”按钮时 IDE 才取得转换权；否则由 IME1.0 在提交稳定文本后自动转换。模型通信优先传输自适应 `.nemat`，但**文件磁盘上仍以 `.nema` 为权威**。

## 分层与模块建议

`crates/nema-core/`：独立 Rust crate `NemaParser`, `NemaView`, `NemaCodec`, `NemaMetrics`、`NemaDiff`；由 `ide-kernel-core` 调度。`ide-shell-web` 和 `ide-shell-desktop` 复用相同的结构 JSON；`ide-cli` 提供 `nema render/encode/decode/verify/bench` 子命令。前端或 WebView 不重新实现语法，避免 JS/Rust 不一致。参考 Python `codec` 为唯一黄金向量来源。

## 状态/仲裁

`SourceDoc{uri,version,sha256,mode,writer,source_bytes,wire_bytes}`。持有者通过原子 `acquire(docUri,baseVersion,mode)` 申请；两端均在线时 IME 为自动转换 owner，IDE 为 manual-only。用户点击 IDE 转换，申请一次性 manual owner；IDE 生成后做 roundtrip + SHA256 + compare-and-swap 写入新版本；如果版本已更新则显示冲突，并提供重新计算按钮。**不能由 IDE 在 IME 正在组合输入时触发二次转码**。

## 编写与可视化

TextPane 使用 `font-variant-ligatures:none`,`white-space:pre`,`letter-spacing:0`,`tab-size:2`。Node 原文行首单空格；Edge 顶格，续写两空格。显示空格开关只作用于渲染副本。应用代码和 Git Diff 不进入 `.NEMA` 语法，必须保持原生 Rust/TS/JSON 文件独立。

## UT/IT/ST 验收

UT：全部 Golden vectors、双向/反向 Edge、X2 Tooltip、原始字节还原、转义和冲突；IT：IDE/IME owner handoff、断线恢复、权限拒绝；ST：Windows / Tauri / CLI、模型供应商 Tokenizer 插件、100k Edge 懒加载、撤销和性能回归。测试不通过禁止默认写入。


## R7 语义一致性门禁

- 必须使用同一参考 `.NEMA` 原生解析器 / 无损 Codec 的 golden vectors。`parse`、`view`、Graph 悬停检查器、JSON 导出不得丢失 X3+ 扩展属性；X3 的 `APIKey`、`HTTP401` 保留字面拼写。
- 只在 Graph 的 X2 显示悬停说明。点击可展开 X3+，但不改变 Node/Edge 方向与文件数据；复制源码始终保留真实空格。
- IME1.0 默认提交后执行自动压缩；IDE1.0 仅在用户主动点击转换时覆盖自动触发。压缩前后通过逐字节解码往返校验，并对含 `\^`、普通数字和 `\ ` 的输入做对抗性测试。
- 产品集成仍是开发要求，不因本 R7 审查而宣称已经安装到两个仓库。
