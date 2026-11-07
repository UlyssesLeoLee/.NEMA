# NEMA v1.1 — 纵向不规则语义格式（实验规范）

**状态：设计候选 / 参考解析器可执行，不是经标准化机构批准的最终标准。** 版本 1.1 取代 v0.9、v1.0 的 Tab-X 正文语法；历史示例不可直接交给新版解析器。所有控制字符示例中的 `⇥` 表示**一个真实 Tab**，用于文档说明；实际源文件必须写真实 Tab。

## 1. 设计原则

NEMA 是**纵向不规则数据格式**：X 方向用一个 ASCII 空格 `U+0020` 确定列，Y 方向用一个 LF `U+000A` 追加意群。无需换行就不换行；中文和日文可直接连续横向书写，英文优先使用 PascalCase 将常规词合并；遇到相邻多字母缩写等无法确定断词时才另起一行。字面代码、JSON、SQL 和其他已有数据格式保留原文件，不强行转换为 NEMA。

**5W1H 固定字段顺序**：X0 What、X1 Why、X2 How、X3 Who、X4 When、X5 Where。What 是唯一必有列；仅提供 What 的单列领域就是纯文本。不强求 Who。无额外文件版本头，外部通过 MIME / `.nema` 和协议版本协商。领域头保留一个真实 Tab，以免与普通正文首列冲突。

## 2. 三种模式

| 入口 | 识别条件 | 内容 |
|---|---|---|
| `⇥Task001 1` 后首正文顶格 | 默认 5W1H | 普通文本、任务语义 |
| `⇥Table1 1` 后首正文以 Tab 开始 | Table | 第一行去掉 1 Tab 后是以空格分列的任意表头 |
| `⇥>G1 1` | Graph | Node + 有 ID、方向和说明的 Edge |

普通领域头的严格语法：`TAB + [A-Za-z][A-Za-z0-9_.-]* + SPACE + [1-9][0-9]*`。Graph 仅在领域 ID 前额外放 `>`。任何领域只在专用头部状态识别，首列普通内容永远不能冒充；正文禁止原始 Tab（字面 Tab 记为 `\t`），唯一例外是 Table 的首行模式标记。两条连续完全空白物理行结束文档；输出以三个 LF 结束。领域之间**不插空行**。

## 3. What-first 与二维意群

5W1H 实际原文示例（代码围栏内的首行有一个真实 Tab）：

```text
	Tauth1 1
BuildLoginFlow PreventDataLeak ValidateHTTP Codex Today AuthService
 CheckAPIKey
```

用户视图为 What=`Build login flow`；Why=`Prevent data leak check API key`；How=`Validate HTTP`；Who=`Codex`；When=`Today`；Where=`Auth service`。第二行以 1 空格起始，X0 为空，只向 X1 Why 追加一个意群。**连续两个空格代表中间有一个空列**，不能将它们合并。

```text
	Tplain1 1
今天完成测试。
```

只存在 What=`今天完成测试。`。如 `What` 换行后写 `HTTPItIs`，英文显示为 `What HTTP it is`：`HTTP` 是连续大写缩写，`It` 中的 `I` 是新单词起始；而 `APIHTTP` 这类相邻纯大写缩写无法仅根据大小写正确切分，必须分成两个纵向意群。不得凭猜测在大写串中插入词边界。

## 4. 英、中、日的书写

- **英文**：使用 `BuildLoginFlow` 而非每一个单词换行；句首大小写在渲染时可标准化。`HTTPItIs` → `HTTP it is`，`I'm` 等缩写保留英文直撇号 `'`。`APIKey`、`OpenAI`、URI、代码符号和大小写敏感名称必须加精确字面量标记 `\=APIKey`，或由编辑器记录其非语义转换属性。
- **中文 / 日文**：完整文字片段可连续书写，不要求人工切词；纵向意群自动按自然语言的无空格黏着规则拼接。代码点、大小写、标点在原生 AST 中始终原样保存。
- **ASCII 空格属于结构**：普通单元格不能有未经转义的原始空格；确需字面空格时用 `\ `，原样反斜杠 `\\`，原样 Tab `\t`。这些逃逸不应被转为额外字段。

**注意：语义展示不是无损反变换。** `BuildLoginFlow` 展示为 `Build login flow` 后，不能根据这串展示文字推定源文件原来的大小写和换行。可逆性只对 `.nema` ↔ `.nemat` 原文字节成立。

## 5. Table 模式

```text
	Ttable1 1
	Agent Status Note
Claude Ready 已完成审核
  下一轮检查权限
Codex Review 等待最终验收
```

表头第一字符为模式标记 Tab，之后所有表格列由一个空格分隔；数据行 X0 非空开始新记录，X0 为空即续写上一记录。`  下一轮检查权限` 的两个空格表示 X2 Note 追加意群。若业务的第一列可能为空，必须增加稳定记录 ID 列，不可依赖 AI 猜记录边界。

## 6. Graph 模式

```text
	>Gauth1 1
A \=LoginAPI 接收请求
B \=TokenStore 存储会话
A>X>B Reads 校验登录令牌
  过期时重新读取
A<Y<B Notifies 反向通知
A=U=B Shares 共用安全策略
A>P>A Retry 最多重试三次
```

X0 是 Node ID 或 `起点 > 边ID > 终点`、`起点 < 边ID < 终点`、`起点 = 边ID = 终点`；X1 是名称、X2 是自然语言说明、X3+ 是可选属性。`A>X>B` 是 A→B；`A<Y<B` 是 B→A；`A=U=B` 是无向关联；`A>P>A` 是自循环。两条不同 ID 的边可连接同一对节点。不能把 `<` 形的反向边误读为 A→B。

纵向续行可对指定列追加说明。Node / Edge ID 在同一 Graph 作用域内唯一；引用的节点必须存在。普通关系图允许环；只有专门声明为依赖 DAG 时才需要无环约束。图形布局、SVG 坐标不属于文件语法。

### 6.1 Graph 列解释（网站审查补充）

| 字段 | Node 原文 `A \=LoginAPI Authentication` | Edge 原文 `A>X>B Reads VerifySession` |
|---|---|---|
| X0 | `A`：Node ID | `A>X>B`：源 A、Edge ID X、目标 B |
| X1 | `\=LoginAPI`：名称；以 `\=` 精确保留名称大小写 | `Reads`：关系名称 |
| X2 | `Authentication`：可选职责说明 | `VerifySession`：可选行为说明 |
| X3+ | 可选扩展属性 | 可选扩展属性 |

X2 的说明只用于 AI 理解、查找与人类视图，不得被解析为 Node/Edge、箭头或必填类型标签。`A LoginAPI Authentication` 同样是合法的三个空格分隔字段，但在语义渲染中 X1 可能由 `LoginAPI` 拆读成 `Login API`；需要原始拼写时用 `\=LoginAPI`。完整三语说明见 `GRAPH_FIELD_GUIDE_*.md` 和网站 `website/graph-guide.html`。

## 7. 传输格式与安全

`.nemat` 是可选的、确定性解码的传输层；不能当成原生 `.nema` 解析。参见 `NEMA_TRANSPORT_v1.1.md`。`.nemat` 的字典声明使用 `TAB+$N`，前缀组使用 `TAB+数字`，完整单元格引用 `^N`，字面 `^` 必须转义成 `\^`。换回 `.nema` 后需逐字节比较并复验 AST；无获益自动回退原生文件。文档与样本不得包含真实 API 密钥，敏感值默认排除字典。

## 8. 无法回避的歧义及限制

`HTTPAPI` 两段大写缩写、品牌名称中的大小写、真正的多词字面字符串、多个空格、保留结尾空行等无法仅靠 PascalCase 无歧义编码。用户的“仅必要时换行”是一项**编码建议**而不是对所有自然语言都可无损的数学保证。必须以明确转义/不透明字面量或纵向意群边界处理。无损 `.nemat` 不能补偿原生作者输入阶段已经丢失的信息。

## 9. 实验结果

见 `../bench/REPORT.md` 与网站独立 `token-benchmark.html`。BPE 和 Unigram 均为本地固定 SentencePiece 实际测试，包含 Tab 与 LF 字节；不代表 GPT/Claude/Gemini 官方 Token 消耗，亦不包含指令学习、纠错重试、网络请求及本地压缩解压的总体成本。


## Graph 人类渲染器：悬停与说明（R3，非协议变更）

Graph X0 决定身份和方向，X1 是名称，X2 是可选说明。渲染器鼠标悬停 Node / Edge 时显示 X2；Edge 同时显示解析后的真实方向。X2 的纵向续行属于原始元素，不创建新 Edge。空说明显示可选占位，不从名称臆造。单击或 Enter/Space 打开固定详情，Tab 焦点可预览，Escape 关闭。触屏点击进入详情。该交互完全在应用展示层，**不增加第四种模式、不改变 `.nema` / `.nemat` 语法或 Token 基准**。参见 `GRAPH_HOVER_RENDERER_DESIGN.md`。
