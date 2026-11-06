# NEMA v1.4 · 详细设计 / API

## 参考接口

```python
codec.core.parse(source: str) -> Document
codec.core.render(source: str) -> dict
codec.transport.encode(source: str, token_cost: Callable | None) -> Choice
codec.transport.decode(text: str) -> str
```

`Choice` 暴露 `format`, `method`, `score`, `baseline_score`, `saving_percent`，必须先看 `format` 再决定扩展名。`token_cost` 接受**完整**候选字符串，不允许只计算变更片段。若没有给 tokenizer，参考程序以 UTF-8 字节数作为选择启发，并不代表真实 Token 效果。

## 字符级解析顺序

1. 检查 UTF-8、LF、结尾三 LF 和大小限制。
2. 可选第一行 `\t$N` → 读取 N 条不透明字典值（不能将随后的 Tab 头解析为字典）。
3. 严格识别 `\t[?>]?ID REV` → 建领域；不带模式符号即 Table。
4. Table 第一个内容行仅当以字面 `\\ ` 起始时读表头，后续任何 `\\^` 等转义不改变模式。
5. 非缩进行：按**单个 ASCII 空格**分出 X 坐标；尾部 ` .` 标识剩余明确空列。缩进行：统计前导空格，N→X(N−1)，并保留原意群和分隔符。
6. Graph X0 验证 `Node` 或 `A>X>B` / `A<X<B` / `A=X=B`，记录稳定边身份和方向；渲染层才生成 SVG 箭头。
7. 将文本与字典原子分别渲染；非原子英文 PascalCase 分词，中文/日文可连接，句末标点黏着。仅渲染结果不作为字节无损依据。

## .nemat 编码器

候选生成：保留源文；字典/前缀/RLE/组合。字典只提炼重复的**非密钥**词素；前缀由领域头的首次完整 ID 发现；RLE 只处理普通内容中连续 >=4 的单个字符。对每个候选 `decode(candidate) == source` 必须完全成立，方可参与实际 Token 成本选择；不节省时返回源文。字典清单也必须计入成本，不能对不受支持的模型猜测 Tokenizer 统计值。

解码算法受以下条件约束：词条数 <= 2048（参考模型）、输入和输出 <= 16MiB；RLE 计数 4..100000，拒绝非法字典下标、未定义的数字前缀组、非法转义及领域语法。前端绝不使用 `eval()`、动态脚本注入或不受控 HTML。

## 双产品的单写入者协议

```json
{"document_hash":"sha256:...","revision":13,"owner":"IME1.0","generation":42,"idempotency_key":"nema:doc:42","action":"auto-encode"}
```

只有 commit 后的稳定 IME composition 才能触发 `auto-encode`；IDE 初始为只读预览。当用户主动点击 IDE 的“转换”按钮，IDE 请求短暂租约，IME 暂停当前版本写入，校验并提交；旧 generation 的结果必须丢弃。出现任意冲突，展示差异，保持原生 `.nema` 不变。以上 JSON 是 IPC 控制接口，不是 NEMA 文本编码。

## 源代码处理边界
源码、AST、Diff、SQL 和第三方结构化文件原样由对应工具维护。NEMA 仅放 `path#symbol`, `PatchRef`, `TestRunRef` 等定位引用；拒绝擅自压缩源码源文件。
