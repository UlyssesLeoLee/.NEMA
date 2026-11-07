# NEMA v1.1 — AI 训练与评测手册

此包的训练集必须搭配 **v1.1** 解析规则。所有早期 `Who What When Where Why How` + Tab-X 语料均为历史版本，不能与新版混合训练。

## 训练任务

**输入**：原生 `.nema` 文本，具有 `TAB + DOMAIN-ID + SPACE + REV` 头、ASCII 空格横向分列、LF 纵向意群。5W1H 顺序是 `What, Why, How, Who, When, Where`。Table 首行以额外一个 Tab 表示模式，Graph 领域头使用 `TAB + >ID REV`。`.nemat` 不能当成原生文件直接阅读，先用解码器恢复原文。

**目标**：识别三模式，按列准确归属纵向意群，正确解析 `HTTPItIs` 的 `HTTP | It | Is`，中文/日文连续书写，不臆测缩写之间的词界，不改写包含 `\=...` 的大小写敏感内容。Graph 的 `<` 表示真正反向边，Edge 名称和说明都属于边本身。

训练语料：`sft_train.jsonl` 包含 273 条样例，`sft_eval.jsonl` 包含 91 条留出样例。每条含 `instruction`、`input`（真实原文）、`output`（确定性渲染 JSON）和 `meta`。训练/评测按领域序号分割，同类词汇与模板重复；因此这只是**协议一致性**验收，不代表独立的未知分布泛化能力或实际 API 费用下降。

## 正例

```text
	T1 1
What
HTTPItIs
```

渲染 What = `What HTTP it is`。

```text
	T2 1
处理登录流程 防止数据泄露 验证访问令牌
```

渲染 What=`处理登录流程`、Why=`防止数据泄露`、How=`验证访问令牌`，其余列为空。

```text
	>G1 1
A \=LoginAPI 接收请求
B \=TokenStore 保存会话
A<X<B Notifies 反向消息
```

`X` 的方向是 B→A，不是 A→B。

## 必须拒绝/标记歧义

1. 原生正文中以 Tab 随意分隔列，或用两个空格表示一个空格的视觉排版；两个空格实际上表示跳过一列。
2. `APIHTTP` 被静默拆成两个缩写；`OpenAI` 被静默转为 `Open AI` 作为原文字节等价。
3. 在代码文件（`.rs`、`.ts`、`.py`）上执行 NEMA 结构转换。
4. 未识别压缩内容却把 `^0` 当作字面普通文本；`.nemat` 必须先 decode。
5. 用“字节减少 69%”冒充任何实际模型 tokenizer 的 Token 节省率。

## 训练/评测运行

```bash
python -m unittest discover -s tests -v
python bench/reproduce.py
python -m codec.cli render examples/en_60_compact.nema
python -m codec.cli encode examples/en_60_compact.nema --cost bpe --output examples/tmp.nemat
python -m codec.cli decode examples/tmp.nemat --output examples/tmp-restored.nema
```

`--cost bpe` / `unigram` 为本包固定离线 SentencePiece 代理；未接入 GPT、Claude、Gemini 的官方 tokenizer。训练文档不应该鼓励模型自己猜字典索引：**字典提炼、压缩编码和无损比对交给确定性 Codec**，Agent 只生成语义规范的 `.nema`。

## Graph Hover 语义与模型训练边界（网站 R3）

模型应理解 `A \=LoginAPI Authentication` 的 `Authentication` 是 Node A 的 **X2 可选说明**，`A>X>B Reads VerifySession` 的 `VerifySession` 是 Edge X 的 **X2 可选说明**；后续同列纵向意群继续属于该对象。训练渲染输出应暴露 `description` 字段，并正确处理 `B<Y<C` 为 C→B。模型**不需要输出任何 hover 标记、弹窗坐标或 UI 代码**；Hover 由 IDE / 网站从确定性解析结果生成，不增加训练语言的语法形式。

负例：将 X2 `Authentication` 当作自动创建的节点、把 X2 当 Edge 方向、或者在没有 X2 时由模型生成未经用户确认的描述。
