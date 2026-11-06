# NEMA v1.5 · 当前统一语法规范

状态：可执行参考规范（2026-11-06）。此文件是本包当前版本唯一权威语法。**v1.4 与更早版本中的字母领域 ID 不可直接混用。**

## 1. 定位

NEMA 是面向 AI Agent 的纵向不规则二维语义格式：**行首一个 Tab 用于控制行；横向 ASCII 空格用于字段；纵向 LF 用于必要的意群续写**。默认表格；5W1H 与 Node–Edge 图显式选择。它不替换 Rust、TS、Python、SQL 或 Git Diff 源码。

`.nema` 是可编辑的原生文本，`.nemat` 是可选无损压缩传输层。压缩并不等于加密；实际 API Key、密码不允许进入普通字典。

## 2. 领域头：本次破坏性更新

三个领域头的**首字符是真实 Tab（U+0009）**，仅在下面的例子中用 `⇥` 可视化：

| 示例 | 真实语法 | 含义 |
|---|---|---|
| `⇥\1` | `Tab + \ + 1` | 领域 1，**默认 Table**，修订版本隐含 1 |
| `⇥?2` | `Tab + ? + 2` | 领域 2，固定 5W1H |
| `⇥>3` | `Tab + > + 3` | 领域 3，Node–Edge Graph |
| `⇥\1 2` | `Tab + \ + 1 + space + 2` | 领域 1，修订版本 2 |

ID 是从 1 开始的十进制正整数，作用域为当前 `.nema` 文档，必须唯一且稳定。修订号同样为正整数；省略即 1。形式化定义：

```regex
^\t([\\?>])([1-9][0-9]*)(?: ([1-9][0-9]*))?$
```

**为什么必须是 `⇥\1` 而不是 `⇥1`？** 因为 `Tab+number` 已被压缩格式预留为前缀选择；另有正文空格坐标体系。一个显式 `\` 将 Table 领域头与其他控制及续行隔离。`?` 和 `>` 自带模式区分，故不另加 `\`。旧的 `⇥T1 1`、`⇥?T2 1`、`⇥>G3 1` 在本版是非法头，必须迁移。

## 3. 表格：默认且表头可选

第一行正文只有以字面 `\ `（反斜杠 + 一个 ASCII 空格）开头才视为表头，否则直接作为第一条记录；无表头字段自动生成 `column1` 到 `columnN`。表头多列按单个 ASCII 空格分隔，需为唯一、单词型名称。

```text
⇥\1
\ Agent Status Note
Claude Ready CheckSession
   BeforeRelease.
Codex Blocked InvalidToken
```

不写表头时：

```text
⇥\1
Claude Ready CheckSession
Codex Blocked InvalidToken
```

后者三列名称为 `column1`、`column2`、`column3`，而不是将 `Claude` 错当列名。`\^`、`\.` 与 `\\` 开头的普通数据不是表头。

## 4. 纵向意群及空字段

正文使用**恰好一个 ASCII 空格**分割相邻单元。新行顶格为新记录；新行前导 N 个空格（N≥1）将内容追加到上一记录的第 N 列（X=N−1）。例如 1/2/3 个空格分别续写 What/Why/How，或表格的第 1/2/3 列；Graph 第三列续写 Edge 说明。

英文优先 PascalCase、缩写与确认过的字典引用，`HTTPItIs` 可以渲染为 `HTTP It Is`；中文与日文无需强制插空格。不可准确拆词的 `APIKey` 等标识符由共享字典不透明保留。纵向续写是**必要时使用**的语义功能，不强制按英语每个词换行。末尾独立的 ` .` 表示尚未输出的剩余字段显式为空；字面句点可写 `\.`。

文件只使用 LF；两个连续空物理行作为结束，编码为正文末尾恰好 3 个 LF。领域之间无需空行，正文内部不允许 Tab。

## 5. 5W1H：What 优先

模式 `⇥?2`，固定六列：**What / Why / How / Who / When / Where**。单句仅写 What 合法，其余列为未提供；使用 ` .` 才表示尾部字段显式空。

```text
⇥?2
Validate^0BeforeAccess PreventLeaks Rust .
 ContinueAfterReview
```

上例第一个字段（What）纵向续写；与 Table 的规则完全相同。

## 6. Graph：方向唯一，Edge 有正文

Graph 以 `⇥>3` 开始。X0 为 Node ID 或 Edge 表达式：

| 语句 | 真实方向 | 图渲染约束 |
|---|---|---|
| `A>X>B` | A → B，Edge ID=X | 目标 B 的节点边界上必须有箭头 |
| `A<X<B` | B → A，Edge ID=X | 目标 A 的节点边界上必须有箭头 |
| `A=U=B` | A — B，Edge ID=U | 无向关系无箭头 |
| `A>R>A` | A ↻ A | 自循环箭头回到 A 自身边界 |
| `A>X>B`、`A>Y>B` | 两条平行 A → B | 两条不同曲线，Edge ID 不重复 |

Node ID/Edge ID 是区分大小写的标识符；图领域内两类 ID 各自不得重复；所有边端点须引用该图领域内声明的 Node。Graph X1 为名称/关系类型，X2 为说明，X3+ 为附加属性。纵向以三个空格续写 X2，无需重复 Edge ID。

```text
⇥>3
A LoginAPI
B TokenStore
C AuditService
A>X>B Reads ValidateSession
   WhenTokenIsValid
B<Z<C Notifies TokenExpired
A=U=C Shares AuthPolicy
B>R>A Responds Accepted
```

解析结果 X: A→B；Z: C→B；U: A—C；R: B→A。**绘图算法不能通过字符串中 `<` 或 DOM 节点显示顺序判断方向，而必须使用解析器输出的 `edge.from`、`edge.to`。** 坐标仅是视觉效果，不作为数据语义存储。自循环、双向独立边、平行边不得合并。IDE/网页显示 Edge ID、关系名和纵向说明，可点击检查。

## 7. 共享字典、转义与 RLE

文档可在第一行声明 `Tab+$N`，之后恰好 N 行是编号 0..N-1 的不透明词条。`

```text
⇥$1
APIKey
⇥?2
Validate^0BeforeAccess PreventLeaks Rust .
```

`^0` 引用整段 `APIKey`，渲染时不会将其拆为 API Key。字面量 `^` 用 `\^`，反斜杠用 `\\`，字面句点可用 `\.`。中文日文中不引起歧义的直接混合标识符允许连续书写。真实机密必须引用 SecretRef，不写入字典。

独立 `.nemat` 传输层有自动共享字典和 `\N字` 的 RLE（N≥4，不能编码空格/Tab/LF）；**所有压缩候选必须先解码并做字节完全一致检查，再根据目标 tokenizer 的完整成本决策**。无收益直接传 `.nema`。

### 关于数字前缀

旧版 `.nemat` 的 `Tab+数字` 用于已协商的前缀组选择，现仍作为传输保留语法，**不再可与数字型原生领域头混用**。v1.5 的参考编码器暂不发出旧版基于字母 ID 的前缀选择器；未协商的旧前缀编码必须拒绝，而不是猜测恢复。压缩能力仍包含字典/RLE/原文回退。保留旧前缀功能需单独的后续兼容版本协商。

## 8. 兼容性、IDE/IME、验证

从 v1.4 升级，需把字母领域头映射到**稳定的数字 ID**，并更新所有领域引用。迁移器应先按旧规范完整解析，再分配新 ID，而不是以字符串批量盲替换。由于 Graph 节点与 Edge ID 独立于领域 ID，图元素可保留其原标识。

IDE1.0 / IME1.0 共用未来的 Rust Codec；当前 Python 为可运行参考实现。两者同时启用时 IME1.0 在 composition commit 后优先执行自动转换，IDE1.0 除用户手动点击外只预览/校验；共享字典必须由确定性规则与确认过的标识符来源提炼，不能让模型臆造精确凭证。

本包的本地 BPE/Unigram 基准**并非真实 GPT、Claude、Gemini 计费或训练可靠性验证**。测试设计、图箭头几何/点击验收与实际日志见 `NEMA_GRAPH_RENDER_DESIGN_v1.5.md`、`NEMA_TEST_DESIGN_UT_IT_ST_UAT.md` 和 `bench/results.json`。
