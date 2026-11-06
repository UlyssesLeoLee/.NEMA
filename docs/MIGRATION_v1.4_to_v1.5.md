# v1.4 → v1.5 覆盖更新与迁移

本版本为**破坏性头部语法更新**：`⇥T1 1` / `⇥?T2 1` / `⇥>G3 1` 不再合法；分别用 `⇥\1` / `⇥?2` / `⇥>3`。`⇥` 只表示实际 Tab。版本 1 可省略；例如 `⇥\1 2` 为版本 2。

不要直接全仓查找替换字母 ID：旧领域 ID 可能被关联、脚本、测试或存储记录引用。推荐先用旧解析器读取语义，再分配唯一且稳定的数字领域 ID，输出 v1.5 文件，校验 Table、5W1H 和 Graph 均不丢数据。Node/Edge 自身 A/X/B 标识不用迁移。

如果项目已有原生 `.nema` 文件，先备份。下载本包后可将 `website/`、`codec/`、`docs/`、`training/`、`tests/`、`examples/`、`bench/`、`brand/` 和根 `index.html` 按目录覆盖到 NEMA 仓库；请勿混用旧版 `.nemat` 缓存，重新生成传输内容。IDE1.0 和 IME1.0 的设计资料仅供两个项目后续实现，不会自动修改它们的仓库。

具体回归步骤：`python -m unittest discover -s tests -v`、`python training/validate_corpus.py`、`node tests/graph_renderer.test.js`、`python scripts/release_check.py`。本地分词复现：`python bench/reproduce.py`。
