# .NEMA 解释器 / 编码器使用说明

解释器与压缩器采用独立 Python 参考实现，无须 Node 或 Rust；支持 Windows PowerShell、macOS 和 Linux。项目主要入口：`python -m codec.cli`。

```powershell
python -m codec.cli render examples/complete_v12.nema
python -m codec.cli inspect examples/graph_3n_4e.nema
python -m codec.cli encode examples/graph_3n_4e.nema --output graph.nemat
python -m codec.cli decode graph.nemat --output restored.nema
```

输出文件为 `.nema` 或 `.nemat`，`render` 提供 JSON 语义视图。默认转换不需要 `sentencepiece`，只在 `--cost bpe/unigram` 或复现实测时使用本地参考模型并安装 `pip install sentencepiece`。

**Windows:** PowerShell 读取/写入必须选 UTF-8，换行必须为 LF。解释器拒绝不完整尾标记、无域头、混淆的 Graph Node/Edge、悬空节点、重复 ID 和非法转义。发布前应进一步补充超大文件流式解析、真实 IDE/IME 插件集成的安全审计。
