# NEMA v1.5 · 当前可覆盖发布包

NEMA 是面向多 Agent 的**纵向不规则二维文本格式**：正文以 ASCII 空格分列、LF 续写意群，Table 默认，另有显式 5W1H 和带内容的 Graph。`.nema` 原生可编辑；`.nemat` 可选无损传输压缩。**本次的重点是纯数字领域头和 Graph 真箭头。**

本目录包含最新的**三语静态网站、Token 实测专页、品牌素材、解析器、无损编解码器、300/80/6 AI 语料、IDE1.0 和 IME1.0 设计、测试、迁移脚本及可复现基准**。唯一权威语法文件：`docs/NEMA_SPEC_v1.5_zh.md`。

## 最新语法速览

以下 `⇥` 是说明用符号，真实 `.nema` 里是一个 Tab：

```text
⇥\1
\ Agent Status Note
Claude Ready CheckHTTPStatus
   BeforeRelease.
⇥?2
ValidateLogin PreventAbuse Rust .
⇥>3
A LoginAPI
B TokenStore
C AuditService
A>X>B Reads ValidateSession
   WhenTokenIsValid
B<Z<C Notifies TokenExpired
A=U=C Shares AuthPolicy
```

- `⇥\1`：默认 Table，数字领域 ID=1，revision 默认 1。
- `⇥?2`：5W1H（What / Why / How / Who / When / Where）。
- `⇥>3`：Graph。`A>X>B` 是 A→B；`B<Z<C` 是 C→B；`A=U=C` 无向。Edge 自带独立 ID、标签、说明及纵向续写。
- `⇥\1 2`：领域 1 的版本 2。旧 `⇥T1 1`、`⇥?T2 1`、`⇥>G3 1` 已废止。
- 表格首条正文 `\ ` 声明显式表头；不写则首行就是数据，列名自动为 `column1`…`columnN`。
- 行首 1 / 2 / 3 个空格分别续写上一行第 1 / 2 / 3 列。末尾 ` .` 表示剩余列显式为空。
- `Tab+$N` 文档共享字典，`^N` 内联原子引用。`\^` 是字面 `^`；中日文可以连写，英文优先 PascalCase。真实机密必须使用 SecretRef。
- `.nemat` 当前选择字典、RLE 或回退原文。**数字域头已使字母域名前缀压缩过时，旧式 Tab+数字前缀选择器本版不再生成。**

## 覆盖与本地运行

直接将此包解压到你的 NEMA 项目根目录，按目录覆盖 `website/`、`docs/`、`codec/`、`training/`、`bench/`、`examples/`、`tests/`、`brand/`、`scripts/` 和根 `index.html`；建议先备份并删除仓库中旧版 `v1.4` 文件，避免将历史训练集混用。`website/index.html` 是主页，`website/token-bench.html` 是独立 Token 基准页面。

```bash
python -m unittest discover -s tests -v
node tests/graph_renderer.test.js
python training/validate_corpus.py
python scripts/release_check.py
python bench/reproduce.py  # 需 pip install sentencepiece
# 可选：本地已安装 Playwright 和 Chromium 时
python tests/browser_smoke.py
# 迁移旧单文件（会生成旧 ID 到新数字 ID 的映射）
python scripts/migrate_v14_to_v15.py old.nema migrated.nema
```

旧 `.nemat` 缓存必须重新生成；不要把此覆盖包当作自动修改 IDE1.0 / IME1.0 仓库的工具。两者的 Rust 产品集成仍需开发，设计资料分别在 `docs/IDE1.0/` 与 `docs/IME1.0/`。两者共用时**IME1.0 默认自动转换，IDE1.0 手动点击才接管**。

## 本地 BPE 实测（重跑）

| 场景 | 原生 NEMA | 最优无损传输 | 节省 |
|---|---:|---:|---:|
| 英文 60 领域 | 3789 | 1813 | **52.15%** |
| 中文 60 领域 | 5282 | 2647 | **49.89%** |
| 日文 60 领域 | 7802 | 1925 | **75.33%** |
| 表格 300 行 | 4709 | 3830 | **18.67%** |
| 120 Node / 600 Edge | 15651 | 12556 | **19.78%** |
| 高熵表格 | 5275 | 5275 | **0%（原文回退）** |

计数来自随包的本地 SentencePiece BPE，包含候选头部和字典成本，**不等于实际 GPT/Claude/Gemini 账单或经过训练后模型的正确生成率**。数据为合成样例，部分高度重复。重跑脚本、JSON/CSV 与完整原文在 `bench/`。

## 图渲染修复和验证

当前 SVG 箭头以解析器 `edge.from`、`edge.to` 为唯一依据，锚在目标节点边界，支持反向边、平行边、无向边、自循环和点击查看说明。具体算法在 `website/graph.js`；验收见 `tests/graph_renderer.test.js`、`tests/browser_smoke.py`、`docs/NEMA_GRAPH_RENDER_DESIGN_v1.5.md`。Node/Edge 的源语义没有任何布局依赖。

当前参考实现为 Python + 静态 HTML/CSS/JS；未把 Rust Codec 或 Windows TSF/IDE 集成宣称为已交付生产代码。
