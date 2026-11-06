# NEMA/2 v0.3 · 人工书写与 IDE1.0 渲染指南（简体中文）

## 定位与边界

NEMA `.nema` 是 AI 优先的二维位置数据格式，**一段完整的顶格领域块就是一个 Agent 作业领域**。人类通常通过 IDE1.0 风格的表单/卡片查看内容，不应将 `.nema` 理解为普通 Markdown、YAML 或可执行脚本。v0.3 是实验性参考规范。

## 最小可用样品

以下字段之间使用 **Tab（U+0009）**。如果你的工具会把 Tab 替换成空格，请直接使用仓库中的 `downloads/sample.nema`，不要手工复制排版过的文档代码块。

```text
n2
%T	who	what	when	where	why	how
%I	method	path	req	res	auth:b
%F	path	lang	owner
T/a7 1
 argo	limit	now	I/login	abuse	60/min/ip
  I/login
   F/auth
    T/design
     cargo test
T/design 1
 claude	design	now	I/login	contract	review
I/login 1
 POST	/v1/login	credentials	token	1
  F/auth
F/auth 1
 src/auth.rs	rust	argo
```

## 六条书写规则

1. **声明版本**：第一行是 `n2`，确定协议版本；无效版本必须拒绝解析。
2. **Schema 只声明一次**：例如 `%T` 后面按顺序写 `who / what / when / where / why / how`，列之间是 *真正的 Tab*。Schema 决定字段含义，不能把顺序修改当作格式化。
3. **顶格领域头**：`T/a7 1` 表示稳定领域号 `T/a7`，revision 为 `1`；与文件行号完全无关。
4. **一个空格的数据行**：领域头下一行前置一个 ASCII 空格，各字段值按已声明的 Schema 顺序水平排列。
5. **2–6 个空格的关系行**：行首空格的数量是精确协议字段，不是可随意变化的视觉缩进。
6. **补丁提交必须验证**：`.npatch` 除了目标领域与原始版本，还必须携带 Schema 的真实 SHA-256 指纹。真实文件变更还需要资源级哈希或锁。

## 纵向位置规则

| 行首空格 | 含义 | 示例 |
|---:|---|---|
| 0 | 新领域 ID + 版本 | `T/a7 1` |
| 1 | 字段数据（横向 Tab 分隔） | ` argo<TAB>limit<TAB>...` |
| 2 | 读取/引用的领域 | `  I/login` |
| 3 | 计划写入的领域 | `   F/auth` |
| 4 | 依赖领域 | `    T/design` |
| 5 | 验收/检查文本（**不可自动执行**） | `     cargo test` |
| 6 | 扩展关系：`目标<TAB>关系类型` | `      I/login<TAB>documents` |

**注意：** 不能把 4 个空格替换成 Tab，也不能把行内的 Tab 替换成多个空格。不可凭自然语言猜测缺失字段。

## 横向位置与 IDE1.0 渲染

对 `%T` 声明六个字段 `who / what / when / where / why / how` 后：

` argo<TAB>limit<TAB>now<TAB>I/login<TAB>abuse<TAB>60/min/ip`

渲染为：

| 谁 | 做什么 | 何时 | 哪里 | 为什么 | 如何 |
|---|---|---|---|---|---|
| argo | limit | now | I/login | abuse | 60/min/ip |

同时展示关系：读取 `I/login`、写入 `F/auth`、前置依赖 `T/design`、验收声明 `cargo test`。任何一个字段或关系行的原始位置都应可被 IDE1.0 追踪并无损回写。

## 类型、转义与压缩

- 未声明类型的字段是字符串；`:n` 整数，`:b` 布尔（`0/1`）。
- 字段内的字面 Tab、新行、回车、反斜杠分别编码为 `\\t`、`\\n`、`\\r`、`\\\\`；起始空格用 `\\s`。
- `$code<TAB>literal` 可以在头部声明字典，数据中的 `^code` 为复用引用。
- `:GROUP<TAB>prefix` 允许压缩同一分组的 ID 公共前缀；应交由参考序列化器生成，避免手写歧义。
- 这些机制可能减小字节数，不保证对所有 tokenizer 都节省 Token。生产中的编码选择应以目标模型实测为准。

## 协作与冲突

- **分配单位：** 完整领域块；Agent 可分别准备各自 `.npatch`。
- **版本验证：** 提交时比较原 revision（CAS），拒绝过期写入。
- **Schema 验证：** 防止重排后旧位置补丁错误更新其他字段。
- **资源验证：** 两个领域即使不同，也可能都修改 `src/auth.rs`，必须由执行器另做文件级冲突控制。
- **执行权限：** `cargo test` 等只是一段声明，不代表授权执行命令。外部执行器需按自身权限策略执行。

## 推荐工作流

IDE1.0 打开 `.nema` → 依据头部 Schema 构造域卡片 → 选择一个稳定领域号 → 编辑字段或关系 → 生成对应 `.npatch` → 本地验证 → 调度器审核依赖与资源冲突 → 存储层原子提交 → 刷新视图。

源文件与语言规范：`prototype/v0.3/SPEC.md`；性能与对抗性记录：`prototype/v0.3/REPORT.md`；可执行参考测试：`prototype/v0.3/test_nema2.py`。
