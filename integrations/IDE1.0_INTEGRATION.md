# IDE1.0 — NEMA v1.1 自动转换接入设计（目标仓库 docs/）

目标：`https://github.com/UlyssesLeoLee/IDE1.0`。已核对其 GitHub 仓库具有 `crates/ide-kernel-core`、`crates/ide-shell`、`crates/ide-shell-web`、`crates/ide-shell-desktop`、`crates/editcore`。以下路径为**实施建议**，本包不修改用户 GitHub 仓库。

## 要件

- 支持新版 What / Why / How / Who / When / Where；正文 ASCII 空格为横向列，LF 为纵向意群。Table 第一个正文行前一个 Tab 表示模式；Graph 领域头 `\t>G1 1`，箭头方向必须严格由表达式生成。
- 自动**提炼**高频完整单元格、避开敏感内容/Graph X0，自动分配 `TAB+$N` 字典和 `TAB+数字` 前缀组，支持 `\^` 字面字符并以编码前后源文件 SHA-256 验证。
- 提供三视图：原生 `.nema`（编辑）、`.nemat`（只读/下载）、人类渲染（5W1H/Table/Graph）；有候选字典查看、排除词条、模型 tokenizer 成本与原文回退标识。
- **当 IME1.0 存在时默认绝不自动抢占**：IDE 仅渲染/校验，用户明确点击“转换”才获取一次性写权限；操作期间通过 IPC 暂停 IME 自动转换，结束后权归 IME。IME 不存在时 IDE 仍默认手动，除非用户专门配置 IDE 自动模式。
- 任何自动或手动转换只更新独立 sidecar/cache/API payload，不将压缩数据覆盖用户原生文档；支持撤销、幂等 ID、版本比对及 CAS。

## 基本设计与模块规划

1. 新增建议 crate `crates/nema-codec`，提供纯 Rust `parse`, `render`, `encode`, `decode`, `optimize`, `validate`, `estimate_tokens`，与本包 Python 金样例逐字节一致。
2. 在 `ide-kernel-core` 提供文档快照、域 Revision、内容 SHA-256、IME 所属状态与转换锁的适配接口。
3. 在 `ide-shell-web` 和 `ide-shell-desktop` 引入三视图和“手动转换”按钮；UI 必须明确分区显示“相对原生 .nema”“相对位置式 YAML”两种百分比。
4. `editcore` 只在版本校验通过后以事务方式修改源文档；`.nemat` 是导出缓存，不是原文缓冲区。

## 详细接口建议

`NemaCodec::parse(&[u8]) -> Result<Document,ParseError>`；`NemaCodec::optimize(snapshot,score_kind) -> Result<Candidate>`；`NemaCodec::decode(candidate) -> Result<NativeBytes>`；`ConversionBroker::request(document_id,revision,sha256,owner=IDE_MANUAL)` 返回一次性令牌；`ConversionBroker::release(token)`。

**只可将无损验证通过的结果写入 sidecar**。若正在 IME 组合中、IME 持有自动 token、源 hash 变化或候选收益≤0，手动按钮必须提示冲突/回退原因而非覆盖文件。

## UT/IT/ST/UAT

- UT：解析三模式、What-first、Space-X 空列、PascalCase、字面 API/URL、`TAB+$`、`TAB+digit`、`\^`、Graph 指向与反向。
- IT：Web/Desktop/UI 与 Rust codec 的一致性，双端读取同一文档的锁与快照边界，词典选择与原文一致。
- ST：大图、10k 行表格、低性能设备、内存限制、离线 Token 模型不可用时回退字节代理。
- UAT：Windows/Web 实际点击转换→独立缓存生成→人工选择 Edge→反向箭头正确→撤销不改源。

**尚未实施至 IDE1.0 仓库。** 详见 `docs/NEMA_SPEC_v1.1_zh.md` 与 `docs/NEMA_TEST_DESIGN.md`。源代码语言正文不参与 NEMA 自动改写。

## Graph Hover 人类渲染扩展（R3）

新增 `GraphHoverVM`：`kind,id,name,description,source,target,directed`。其中 `description` 直接取 AST X2（包含纵向续写），不能根据节点名称自动生成。`ide-shell-web`、`ide-shell-desktop` 均需要 Node/Edge 悬停即时显示说明、键盘焦点预览、Escape 关闭、点击固定详情、触屏点击进入详情。Graph SVG 保留宽透明命中线，防止狭窄 Edge 难以悬停；悬停绝不变更源文件、字典、选择或转换的所有权。

在 IDE 渲染 API 上建议拆为 `hover(item_id)->GraphHoverVM`（只读）与 `select(item_id)->InspectorState`（UI 选择操作），两者不触发 IME1.0 自动转换。方向从 AST 取得（反向边 `B<Y<C` 必须 C→B），空 X2 明示可选。屏幕阅读器要读到关系方向及说明。完整规范：`docs/GRAPH_HOVER_RENDERER_DESIGN.md`。

### R4 Graph 渲染可访问性交付约束

实现 Node/Edge 悬停、点击查看 X2 时，不得在重建 Graph DOM 后丢失键盘焦点；必须通过 `(kind,id)` 将焦点恢复至最新视图。复杂多重边使用固定端点对的通道分离，不能根据画面方向猜测 Edge 方向；当端点在布局中交换时，箭头语义仍由 Graph AST 决定。三语标签和 ARIA 名称一起更新。对应网站审查证据：`docs/WEBSITE_REVIEW_R4_FIVE_ROUNDS.md`，可复现浏览器用例：`tests/test_browser_r4_five_rounds.py`。
