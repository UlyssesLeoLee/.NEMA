> v1.3 authoritative Graph delta: `docs/GRAPH_V13_MIGRATION.md`. Node and Edge both start at X0; one leading space continues X2, two X3; domain header still begins with a literal Tab and is unchanged. Historical R7 text below, if quoted, is non-normative.

# .NEMA v1.3 — `.nemat` 可逆传输协议

编码器位于 `codec/nemat.py`；参考 CLI 在 `codec/cli.py`。`.nema` 是唯一可信的编辑态；`.nemat` 仅为 AI 传输或缓存，不替代 Git、AST、语言服务器或源代码。

- 单独一行 `Tab + $N` 声明 N 个字典值，后续 N 行依次为词典内容。文字 `$` 在普通 `.nema` 的 What 字段中不影响语义；词典声明只在 `.nemat` 最前的协议状态有效。
- `^0`, `^1` 等只在传输中引用词典条目，字面量 `^` 在传输中转义为 `\^`；字面量 `\\` 应由 native 编码器正确保留。
- `Tab + 0`、`Tab + 1` 等只在 `.nemat` 使用，表示自动发现的领域 ID 公共前缀组；不要求人为声明 `:TaskLogin0` 等冗余装饰。
- 领域短头使用 `Tab + 数字后缀 + 空格 + 版本`，解码时用当前前缀组还原原始头部。
- **压缩器不能把 Graph 续写的前导空格当作可替换的空字段或词典引用。** Graph Node 的 ID（X0）和 Edge 关系表达式（X0）必须保持原始结构。词典只替换可变内容格。
- 自动从原始文本提炼重复候选，逐候选比较目标 tokenizer 的实际 Token 开销；没有收益时回退原始 `.nema`。
- 回写时必须 `decode(encode(original)) == original` **逐字节一致**，包括换行、空格、原始标点。禁止把语义拆分结果当作无损输出。
- 有大小限制、字典条数限制、秘密扫描以及损坏词典拒绝，参阅参考实现。Tokenizer 训练文件仅供离线基准，不可宣称为商业模型官方 Tokenizer。

## CLI

```powershell
python -m codec.cli render examples/graph_3n_4e.nema
python -m codec.cli encode examples/graph_3n_4e.nema --output sample.nemat
python -m codec.cli decode sample.nemat --output restored.nema
python -m codec.cli inspect examples/graph_3n_4e.nema
```

使用 `--cost bpe` 或 `--cost unigram` 时可选安装 `sentencepiece` 并加载随包本地参考模型。实际部署须使用目标 AI 提供商的 tokenizer 进行最终计费校验，包含 prompt/response/retry。
