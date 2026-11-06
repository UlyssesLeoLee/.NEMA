# NEMA v1.4 · Full Project Package

NEMA 是一种 **AI 原生的纵向不规则二维数据格式**：表格为默认；正文中 ASCII 空格分列、LF 承载纵向意群；特殊领域头有 5W1H (`?`) 和 Graph (`>`)；共享字典与 `.nemat` 传输压缩可由 IDE1.0 / IME1.0 自动应用。

**2026-11-06 · v1.4 RC**。此包以 `docs/NEMA_SPEC_v1.4_zh.md` 为唯一权威规范。`archive/` 全部是旧版本历史文件，不可当作 v1.4 训练素材。

## 最重要的 v1.4 更新：默认 Table 表头**可选**

**真实 `.nema` 原文**（下例 `⇥` 仅为显示真正 Tab 的图形替身）：

有表头：

```text
⇥T1 1
\ Agent State Note
Claude Ready CheckSession
   AccessGranted
```

无表头：

```text
⇥T1 1
Claude Ready CheckSession
Codex Blocked InvalidToken
```

后一种输出字段名 `column1`、`column2`、`column3`。只有默认 Table 的**第一个内容行**以精确 `\ ` 起始才声明表头，其他以反斜杠开头的原文（例如 `\^`）绝不触发表头。

- 默认 Table；显式 `\t?ID REV` = 5W1H，顺序 **What / Why / How / Who / When / Where**；` .` 标识后续明确为空。
- `\t>ID REV` = Graph。`A>X>B` 表示 Edge X 的 A→B；`A<X<B` 表示 B→A，关系也有独立名称、属性与纵向说明。
- 正文列之间使用**一个 ASCII 空格**；行首 N 个空格延伸 X(N−1) 列，没有任何必要时不用强制换行。英文优先 PascalCase，中日文可直接连接；`HTTPItIs` → HTTP It Is。
- `\t$N` 声明文档共享字典；`^N` 是可嵌入英文意群的原子引用。`Validate^0BeforeAccess` 保留 `APIKey` 不拆分；字面 `^` 用 `\^` 逃逸。
- `.nemat` 压缩层：字典提炼、可发现的数字前缀、RLE，前端无损恢复。格式选择须计入所有控制符与词典 Token，无收益原文回退。真实机密用 SecretRef。
- IDE1.0 与 IME1.0 同时存在时，**IME1.0 默认在 composition commit 后自动转换**，IDE1.0 仅在手工点击“转换”后临时接管。两个产品未来共享同一 Rust codec，当前仍是待实现设计。

## 文件目录

| 路径 | 内容 |
|---|---|
| `index.html` / `website/` | 离线三语品牌网站、Graph 箭头视图与独立 `token-bench.html` 实测专页 |
| `docs/` | v1.4 语法、IPA 风格要件/基本/详细设计、UT/IT/ST/UAT、迁移及 WBS；英文/日文入门指南 |
| `docs/IDE1.0/` | IDE Rust Codec、Web/Shell、手动转换按钮、租约仲裁与测试设计 |
| `docs/IME1.0/` | IME Rust/TSF/VS Code composition、自动字典提炼、默认转换与测试设计 |
| `codec/` | Python v1.4 原生解析／渲染、无损 `.nemat` 自适应压缩与 CLI |
| `examples/` | 15 组真实 `.nema`（含无表头/有表头）以及渲染 JSON |
| `tests/` | Python 回归、无损往返、非法控制输入及 Graph 方向用例 |
| `bench/` | 2 个本地 SentencePiece 模型、BPE+Unigram 实测 JSON/CSV、原文/压缩/YAML 对照、复现脚本 |
| `training/` | 300 条 SFT、80 条不重叠留出、6 条 codec 示范、生成与静态验证脚本 |
| `brand/` | NEMA Logo、SVG、PNG、Graph 设计资产 |
| `archive/` | 单独隔离的 v1.0 完整历史资料 |

## 命令（从项目根目录执行）

```bash
# Python 3.11+；核心 Codec 不依赖外部包
python -m unittest discover -s tests -v
python training/validate_corpus.py
python -m codec.cli render examples/01_explicit_table_header.nema
python -m codec.cli render examples/00_default_table_no_header.nema
python -m codec.cli check examples/03_graph_complex.nema
python -m codec.cli encode examples/bench_en_60.nema --cost bpe --output demo.nemat
python -m codec.cli decode demo.nemat --output restored.nema

# benchmark 需 pip install sentencepiece；本包已经提供 BPE/Unigram 模型文件
python bench/reproduce.py
```

⚠️ `encode` **可能自动回退到原生 `.nema`**，因此不能无条件把输出命名 `.nemat`：脚本会打印实际 `format`，正式调用端应以 MIME/format 决定扩展名。以上示范的重复英文 60 领域在当前本地 BPE 测试会选择 `.nemat`。网站主页可直接打开根 `index.html`，性能专页 `website/token-bench.html`。

## 当前可核实的实测结果

在**本地 SentencePiece BPE（保留 Tab/空格/LF）** 下，同一 `.nema` 源与其最优无损传输候选：

| 数据 | 原生 Token | 最优 Token | 节省率 |
|---|---:|---:|---:|
| 英文 60 领域 | 3909 | 1818 | 53.49% |
| 中文 60 领域 | 5402 | 2652 | 50.91% |
| 日文 60 领域 | 7922 | 1930 | 75.64% |
| 表格 300 行 | 4712 | 3833 | 18.65% |
| Graph 120 Node + 600 Edge | 15655 | 12560 | 19.77% |
| 高熵随机表 120 行 | 5279 | 5279 | 0%（原文回退） |

这是重复程度较高的**合成数据**测试，只证明该本地 tokenizer 下的**文本压缩候选成本**，**不等于实际模型 API 的账单节省率**。真实模型是否能自己准确生成 `.nemat`、训练开销、提示词成本及纠错开销尚未测试。

## 实际完成与未完成

完成：Python v1.4 参考核心、回归测试、合成基准、三语网站、训练数据生成/验证、IDE/IME 接入文档。未完成：真正 Rust crate、IME TSF/Windows 实机运行、IDE/IME 源码集成、商业模型训练及官方 tokenizer 的完整端到端测量。该包不直接修改远程 GitHub 仓库。
