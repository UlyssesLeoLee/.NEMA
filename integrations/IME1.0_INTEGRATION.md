# IME1.0 — NEMA v1.1 智能编码接入设计（目标仓库 docs/）

目标：`https://github.com/UlyssesLeoLee/IME1.0`。已核对其仓库存在 `01_Source/crates/pime-core`、`pime-tsf`、`pime-ipc`、`pime-ai-worker` 与 `01_Source/editor-bridges/vscode`。该项目目前的实际 Windows TSF 激活/注册尚不能当作已通过，本设计不宣称真实用户环境已完成集成。

## 要件

- 在用户授权、文件类型 `.nema` 或编辑器明确声明 NEMA 场景时，IME1.0 **默认负责自动转换**：仅在一次组合输入 IME Commit 完成、文本稳定并且编辑器版本可确认后触发去抖任务；候选编辑态、Composition Start/Update 时禁止转换。
- 书写阶段采用原生 v1.1 SPACE-X 规则：What-first；完整中文、日文不插入强制空格；英文可在可见候选中建议 PascalCase，只有多缩写等歧义处选择纵向断行。**不得私自把用户已有代码/APIKey 改成大小写推断结果**。
- 按稳定文档快照执行自动完整词条字典提炼（`TAB+$N`）、数字前缀（`TAB+数字`），并将字面 `^` 转义为 `\^`。本地建立候选 `.nemat` 侧车缓存，原生 `.nema` 保持编辑真相；失败或无收益回退原文。
- IDE1.0 同时工作时 IME 为 `IME_AUTO` 默认 owner。**IDE 的人工点击优先**，转换 Broker 原子发放 `IDE_MANUAL` 一次性令牌，IME 暂停当前自动转换并在手动任务完成/取消时恢复。
- IME 自动转换不在每次按键触发，不阻塞 TSF 候选或键盘响应。只有 `.nema` 语义上下文允许触发，不在 Rust/Python/TS/PowerShell 等源码正文中进行结构转换。

## 实施模块及数据流

`pime-tsf Composition Commit` → `pime-core` 本地输入状态机 → `pime-ipc` 授权及 `(document_id,revision,content_hash)` 快照 → Rust `nema-codec`（建议复用 IDE 相同 crate 的同一版本）→ 自动候选和 Token 成本评估 → 无损往返断言 → sidecar `.nemat` / Agent API send（需用户授权）。`pime-ai-worker` 可在用户允许时提供推荐断词/字典候选，但最终编码必须由确定性 Rust 实现。

## 和 IDE1.0 的双端优先权协议

- Broker 枚举 `IME_AUTO`, `IDE_MANUAL`, `NONE`。授权同时存在时默认 `IME_AUTO`。
- 用户手点 IDE Convert 时发起 `AcquireManual(document_id, expected_hash, request_id)`；若 IME 正在 Compose，则直到 Commit 之后才接受或提示重试。原子切换至 `IDE_MANUAL`，IME 挂起正在排队的编码任务。
- 手动结束/失败/撤销后 `ReleaseManual`，Broker 恢复 `IME_AUTO`。所有写缓存操作必须有 request-id 幂等及 revision-CAS；进程死亡用租约/TTL 或会话重建机制恢复。
- 失去编辑器 NEMA 上下文、断线、明确关闭自动转换或用户撤销授权立即停止自动任务，清理未提交的临时数据。

## 测试

- UT：IME 半组合、提交、撤销、长按、标点、特殊字符 `^`, `\`, `$`, 数字和字段空格状态机。
- IT：IME-IDE 锁交接、两个 Agent 并发编辑相同领域时的版本冲突、候选词典隐私与本地 Token 计数。
- ST：高频输入、屏幕锁定、光标跳转、断网、应用切换、重启缓存恢复。
- UAT：Windows 11 TSF + VS Code 实际书写 What-first NEMA；IDE 不手点时由 IME 自动生成 sidecar；IDE 手点后转换权临时转移；源码输入完全不受影响。

**尚未实施到真实 IME1.0 仓库或真实 Windows TSF。** 以本包参考解析器与 JSONL 金样例作为跨语言兼容的第一步。

## Graph Hover 与 IME 自动转换互不冲突（R3）

Graph Tooltip 属于 IDE1.0 或网站的**只读渲染事件**，不能调用 IME 的自动压缩流程，也不能抢占单写入者锁；IME1.0 默认自动转换的既有优先级保持不变。若 IME1.0 将来提供 Graph 候选视图，优先复用规范化 AST 的 `GraphHoverVM`，描述仅来自 X2，绝不根据鼠标经过触发编码或云端请求。详见 `docs/GRAPH_HOVER_RENDERER_DESIGN.md`。
