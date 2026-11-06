# NEMA v1.5 · 后续实现 WBS（可分派给 Agent）

| WBS | 事项 | 交付物 | 依赖 | 完成标准 |
|---|---|---|---|---|
| 01 | Rust `nema-codec` crate，v1.5 原生 AST | Rust API、UT | 规范 v1.5 | 与 Python 参考数据对齐 |
| 02 | 原生 Table/5W1H/Graph 无损语法测试 | JSON golden、property tests | 01 | 不丢表格首行、Graph 方向正确 |
| 03 | `.nemat` 字典/RLE转换 | Rust codec + fuzz | 01 | byte-exact 往返，溢出安全 |
| 04 | 多 tokenizer 成本选择与回退 | scorer 插件 | 03 | 全部结构成本计入 |
| 05 | IDE1.0 原生视图、手动按钮、Undo | UI + IPC | 02–04 | 默认不自动抢写 |
| 06 | IME1.0 composition commit 自动转换 | Rust pime-core Adapter | 02–04 | 非 NEMA 文件不改写 |
| 07 | 双产品单写入者协调 | Lease / generation | 05–06 | 并行场景不双写、不丢数据 |
| 08 | Windows TSF / VS Code 实机 UAT | 执行记录 | 06–07 | 真实设备证据 |
| 09 | 三家商业模型 tokenizer 实测 | 分模型 Token 报告 | 04 | 输入+输出+重试全成本 |
| 10 | 模型生成可靠性训练/评测 | SFT/holdout 报告 | 09 | 语法有效率与字节正确率量化 |
| 11 | 网站 Token 专页与训练资料同步发布 | 静态站、CSV/JSON、ZIP | 01–10 | 每一数字有可复现来源 |

工作流先完成设计/测试设计并进行设计专用提交，然后实现与测试；跨项目各仓库自行执行准入和 Git 工作树审查。此包没有擅自修改 IDE1.0 或 IME1.0 仓库。
