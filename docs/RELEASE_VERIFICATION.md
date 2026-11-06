# NEMA v1.4 · 本次交付验证记录

- 语法：默认 Table（有/无表头）、What-first 5W1H、带说明/方向的 Graph、内联共享字典。
- 自动单元与往返：`python -m unittest discover -s tests -v`：**41 项通过**（包含随机化往返、非法字典索引、控制符冲突和高熵回退）。
- 语料：`python training/validate_corpus.py`：300 条 SFT、80 条独立 holdout、6 条 transport 演示，**全部可被 v1.4 参考解析器解析**。
- benchmark：`python bench/reproduce.py`，本地 SentencePiece BPE / Unigram **16 组模型×场景**，随包 `bench/results.json` 和 `bench/results.csv`。
- JS：Node.js `node --check website/app.js && node --check website/bench.js` 通过。
- 浏览器：本机 Chromium Playwright 将最新静态 HTML、CSS 与打包 JS 注入 `about:blank` 进行实际交互验证；1365×900 与 390×844 都无页面横向溢出；示例模式切换、Graph 方向、三语、Token 页面切换和高熵原文回退显示正常。由于容器浏览器限制直接访问 localhost/file://，未宣称部署 URL 与全部链接跳转已经验证。
- `scripts/release_check.py`：核实 15 个原生样本、表头分支、Graph 正反方向、共享词典和网页数据。
- 文件完整性：`MANIFEST_SHA256.txt`，逐项计算 SHA-256；ZIP 将经过 zipfile CRC 检查。

**未完成**：IDE1.0 与 IME1.0 实际 Rust 生产功能集成、Windows TSF 真机、API 提供商官方 tokenizer、真实模型微调后压缩文本生成可靠性测试；这些不应标记为已经通过。
