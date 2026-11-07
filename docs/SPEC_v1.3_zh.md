# .NEMA v1.3 — 统一规范（现行版）

- 文档状态：候选协议 / 参考解释器已执行测试；未成为标准化组织发布的行业规范。
- 本版兼容性：v1.3 Graph 节点改为**X0 顶格声明**。旧版 `A \=LoginAPI` 必须经迁移处理，不可当成 v1.3 Node。
- 此文档定义 `.nema` **编辑层**；`.nemat` 是可逆的压缩传输层。源码（Rust、TS 等）保持原格式，`.NEMA` 只存储协作和图拓扑元数据。

## 1. 核心语义

**横向不规则、纵向按需延展**。ASCII 空格（U+0020）定位 X 列；换行 LF 定义 Y 意群。语义上没有必要时不强制拆句。中日文可以直接横向连写；英文推荐 `BuildLoginFlow`、`HTTPItIs`，多段无法区分的全大写缩写应换行。`HTTPItIs` 展示为 HTTP it is，但不保证逆向恢复原始空格与大小写。

一个领域头总是 `Tab + 领域ID + 空格 + 正整数修订号`。Graph 头是 `Tab + > + 领域ID + 空格 + 修订号`。Tab 不再充当正文列分隔。领域之间**无空行**。整个文档以连续两个完全空白的物理行结束（最后正文行后 3 个 LF）。不允许 CRLF 或额外的空行。

### 2. 三模式

| 模式 | 判定 | X0、X1、X2 |
|---|---|---|
| 5W1H（默认） | 领域头后第一条正文行顶格 | What、Why、How；X3=Who、X4=When、X5=Where |
| Table | 领域头后第一条正文行以单个 Tab 开始 | 该行是一组自定义列名；记录首列非空则开新记录 |
| Graph | 领域头带 `>` | Graph 内部的 Node、Edge 均从 X0 开始，以关系符识别 Edge |

### 3. 5W1H / 纯文本

```text
⇥Ttext1 1
What
HTTPItIs
⇥Tzh1 1
审核认证流程 防止泄密 验证令牌


```

其中 `⇥` **仅在文档说明中代替一个真实 Tab**；可执行文件必须使用 ASCII Tab。字段顺序永远是 **What → Why → How → Who → When → Where**。空格分列；如果只有一个字段就是 What 文本。`What` 与 `HTTPItIs` 是同一 What 的两个纵向意群，可渲染为 `What HTTP it is`。

### 4. Table

```text
⇥Tab1 1
⇥Agent Status Note
Claude Ready 校验完成
  等待再次复核
Codex Blocked HTTP401


```

`⇥` 是真实 Tab 的可视替身；`␠` 在文中可用于强调两个空格。`  等待再次复核` 从 X2 纵向续写到上一条 Claude 的 Note。普通数据行首列非空，才是新行。数据的自然语言空格不能直接与分列空格混淆；可使用 PascalCase、合适的纵向意群或 `\ ` 表示精确单元格内字面空格。

### 5. Graph / Node–Edge（v1.3）

以下 `⇥` / `␠` **只为在文档中展示不可见字符**，实际 `.nema` 文件分别使用真正的 Tab 和 ASCII 空格：

```text
⇥>Gauth1 1
A LoginAPI Authentication
B TokenStore SessionStorage
```

注意：上一示意仅用于说明领域头，不是可执行样例。实际可执行示例为：

```text
⇥>Gauth1 1
A LoginAPI Authentication
B TokenStore SessionStorage
A>X>B Reads VerifySession
␠CacheExpiredRetryOnce
B<Y<A Responds SessionReady
A=U=B Shares SecurityPolicy
A>P>A Retry Maximum3Attempts
```

- **领域头完全不变**：首字符为真实 Tab，紧接 `>Gauth1 1`；正则 `^\t>?ID REV$`。领域 ID 与修订号之间一个空格，Graph 前缀 `>` 保留。
- **Node / Edge 均顶格**，即 X0 无前导空格。X0 满足 `NODE` ID 语法时是节点，例如 `A`；含 `>`、`<`、`=` 时必须严格满足 `EDGE` 表达式，否则报错，**不得当成 Node**。
- `A>X>B` 表示 A 到 B 的独立关系 X；`B<Y<A` 是 A 到 B 的反向书写；`A=U=B` 无向；`A>P>A` 自循环。两段关系符必须一致。
- **续写**：一前导空格（`␠`）续写 X2，两个续写 X3，三个续写 X4，依此类推。Graph X1 不允许纵向续写。纵向续写的列编号比旧 R7 左移一个，但语义列 X2、X3 不变。
- X0 身份、X1 精确名称、X2 可选描述、X3+ 原样扩展；各 ID 在领域内唯一，所有关系端点都必须是已定义 Node。
- 此为**不向后自动兼容的 Graph 语法升级**。旧 R7 Graph 必须经显式迁移；不自动猜测版本。5W1H 与 Table 不受影响。

### 6. 源文本的空格与转义

- 原文件中的 U+0020 空格要真实保留，禁止通过 CSS 字体/布局伪造多个空格；示例 `<pre>` 必须使用等宽字体、`white-space:pre`、`letter-spacing:0`，禁用连字。
- UI 的 `·` / `⇥` 可视化开关仅改变**显示副本**。复制/保存必须使用原始原文。
- 原始精确空格需写 `\ `，反斜杠为 `\\`，原始 Tab 作为正文值用 `\t`。5W1H/Table 中的 `\=literal` 可提示按字面保留；Graph X1 默认按字面保留。
- 无法从 `LoginAPI` 推断是否应变成 `Login API`；Graph 名称默认不拆。普通英文 PascalCase 只用于人类语义显示。
- 若需要保留人类原文的每一个空格/大小写/换行，使用已经准确记录的 `.nema` 原文，不要从语义视图倒推原文。

### 7. 领域头保留与边界

`^\t>?ID REV$`（详见 `codec/native.py` 的严格正则）永远优先于正文，防止无空行时丢失边界。这是**保留的结构形状**，普通文本如果恰巧长成领域头，需要由编辑器提示/修改。不能靠 LLM 猜测。一个 Graph 领域与另一个 Table 领域无需空行分隔。

### 8. 语义不等于字节无损

人类渲染 `BuildLoginFlow` → “Build login flow” 是展示策略；AI 生成的原生格式不保证原自然语言的 byte-exact roundtrip。而 `.nemat` 编码—解码对**已存在的 `.nema` 原始 UTF-8 字节**提供完全无损保护。在 API 调用前应通过同一解释器验码，不能只依赖模型学习。

### 9. 最低兼容规则

编码版本 `v1.3`、UTF-8、LF、三模式、WHAT-first、Graph unindented Node/Edge、Edge 方向与悬停 X2、无损 `.nemat` 必须明确标记。旧版 Graph 原文不能混进当前训练集。在转换失败时回退原文，显示语法错误，不自动“修正”代码文件。

### 10. Graph X3+ 扩展属性的语义输出（R7 勘误）

Graph 的 X3、X4… 不是仅供解释器内部存储：`codec.native.parse()` 保留列原子；`codec.native.view()` **必须**将有值的扩展列输出为可选 `extensions` 映射（例如 `{"X3":"APIKey"}`）。无扩展列时不生成该键，以保证现有 JSON 语义输出兼容。X3+ 使用精确字面量拼接，不自动拆分 `HTTP401`、`SHA256` 或 `APIKey`。纵向续写 X3 是两个前导空格，X4 是三个，依此类推；X2 的一个前导空格规则不变。

```text
⇥>G1 1
A LoginAPI Authentication APIKey
B TokenStore SessionStorage
A>X>B Reads VerifySession HTTP401
␠␠RetryOnTimeout


```

`⇥`/`␠` 在文档中是**展示用标识**；真实 `.nema` 使用 Tab 与 ASCII 空格。Graph A 节点 X3 保留 `APIKey`，Edge X 的 X3 呈现 `HTTP401 RetryOnTimeout`。其 X2 始终只用于说明和悬停，不改变关系方向。

注意：Graph 旧式 `A \=LoginAPI` 只可在迁移指南和历史对比中出现，当前原生 Graph 节点必须以 **恰好一个 ASCII 空格**起始。
