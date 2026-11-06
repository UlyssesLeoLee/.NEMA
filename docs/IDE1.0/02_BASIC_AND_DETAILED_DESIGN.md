# IDE1.0 × NEMA v1.5 · 基本设计／详细设计

## 技术落点
在 IDE1.0 Rust workspace 中建议增加 `crates/nema-codec`（与 IME1.0 的同源 crate 共享版本），暴露以下 trait：

```rust
pub trait NemaCodec {
    fn parse(&self, source: &str) -> Result<NemaDocument, NemaError>;
    fn encode(&self, source: &str, profile: &TokenProfile) -> Result<EncodedChoice, NemaError>;
    fn decode(&self, source: &str) -> Result<String, NemaError>;
}
```

`TokenProfile` 可选 BPE/Unigram/各商业模型官方 tokenizer，分词器缺失时按字节启发且标注不等同于 Token。`NemaDocument` 保存原始 span、column 和每列 `Vec<Vec<SemanticChunk>>`，不能直接保存拼接后句子。Rust crate 的算法、字典编号、RLE 上限和错误码必须与本包 Python 参考实现的测试向量一一对应。

## UI
- `.nema` 文件打开：左侧原文编辑，右侧切换 `Table / 5W1H / Graph` 可视化；原文表格表头精确 `\\ ` 判断。
- 表格默认列名 `column1...`；“设置为表头”操作在首行前插入 `\\ `，撤销操作能恢复字节。
- 提供“字典候选”“字典锁定”“显示复用位置”“Token 对照”以及**手动转换**按钮。按钮执行共享 Codec，并执行字节往返校验；原生文件是持久化的权威源。
- Graph 的 Edge 名称与说明可单击；Edge 保有独立 ID，不能把标签误作为节点。

## 与 IME1.0 的所有权仲裁
默认 IDE 进入 `observer`，只读取 IME 最新版本，绝不按键后自动抢转换。只有用户按转换按钮时：`request_lease(source_hash, revision) → pause_ime_same_epoch → encode/validate → atomic_commit → release_lease`。IME 在收到释放并确认版本一致后继续自动转换。过时 epoch 的计算结果全部丢弃；同一 hash 和 revision 的重复请求必须幂等。

## 码流和安全
`.nemat` 必须先解码并校验，再交给 renderer；不允许让压缩内容直接经过 HTML eval。对用户提供的 Token key 等实际密钥只使用 SecretRef。`diff`、`*.rs`、`*.ts`、`*.py` 仍由对应工具链处理。

## 实施顺序
先共享 Rust 核心与 Python 兼容测试 → 再 CLI/Web/桌面 UI 接入 → 再与 IME 通过 IPC 协调 → 最后 Windows 性能及真实 tokenizer 接入。尚未实际提交到 IDE1.0 仓库。
