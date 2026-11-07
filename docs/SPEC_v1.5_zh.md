# .NEMA v1.5 — 正式语法规范（当前版）

> 2026-11-07。此为项目协议规范，不代表国际/行业标准。编辑层是 `.nema`，可逆传输层 `.nemat` 须独立协商。旧版文档保留为历史版本。

## 1. 统一字符规则

所有领域头**恰好一个半角 ASCII 空格 U+0020**，不再使用 Tab：5W1H ` ?Ttask1 1`、Table ` Ttable1 1`、Graph ` >Gauth1 1`。修订号是正整数。领域之间无空行。字段分隔为 U+0020 单个半角空格；列的意群可在后续行延伸。原生正文不能包含未转义的 Tab；**拒绝 U+3000 全角空格**。整份 `.nema` 文件必须使用 LF 并以三个 LF 结束（最后两行为空）。

模式来自领域头，而不是根据正文猜测：` ?` 是 5W1H、` ` 后直接 ID 是 Table、` >` 是 Graph。表格是否有自定义表头，由它的第一条正文是否以真实 ASCII 空格开始决定；此处一个前导半角空格 U+0020 是**显式表格表头正文标记**，与没有前导空格的无表头 Table 第一条数据明确区分。原生 `.nema` 不再需要真实 Tab。没有表头，则产生 `column1` 到 `columnN`。

## 2. 三种领域头

| 写法 | 简明描述 | 例子 |
|---|---|---|
| ` ?ID REV` | 5W1H 领域，首个字符是半角空格 | ` ?Ttask1 1` |
| ` ID REV` | 表格领域，支持显式或自动表头 | ` Ttable1 1` |
| ` >ID REV` | Graph / Node–Edge 领域 | ` >Gauth1 1` |

## 3. 5W1H 模式

字段从左到右固定为 What、Why、How、Who、When、Where；不强求写满六列，纵向续写按列坐标添加语义片段。**问号只在领域头 ` ?ID REV`，不是正文前缀。**

```text
 ?Ttask1 1
BuildLoginFlow PreventLeak VerifyToken Owner Today AuthService
 SecondDetail


```

## 4. Table 模式——显式表头

领域头是单个半角空格 + ID，第一条正文使用**一个真实半角空格 U+0020**开头，后面是半角空格分隔的列名。一个半角空格只作用于表头正文第一行。数据行 X0 非空创建新行、X0 为空续写上一条记录。

```text
 Ttable1 1
 Agent Status Note
Claude Ready CheckComplete
Codex Blocked HTTP401


```

## 5. Table 模式——无表头自动列

第一条正文直接给出数据，不需要任何列名行；解释器自动生成 `column1`、`column2` ……，如果后续出现更多列则扩展。行首 X0 为空表示续写上一行；多空格不是装饰，而是列坐标。

```text
 Tauto1 1
A Ready First
B Blocked Second
  MoreDetail
C Done


```

## 6. Node–Edge 模式

Graph 中 Node 和 Edge 都从 X0 顶格。Node 的 X0 是稳定 ID，X1 名称，X2 描述；Edge 的 `A>X>B` 表示从 A 经关系 X 指向 B，`A<Y<B` 反向，`A=Z=B` 无向。同一 Graph 内 Node ID、Edge ID 不得碰撞；不能引用不存在的端点。以关系符判别 Edge，并严格拒绝畸形 Edge，不能降级为 Node。

```text
 >Gauth1 1
A LoginAPI Authentication
B TokenStore SessionStorage
A>X>B Reads VerifySession
 CacheExpiredRetryOnce
A=U=B Shares SecurityPolicy


```

X2 纵向续写用一个半角空格；X3 用两个半角空格。Edge 和 Node 的 X1 保留机器命名标识，X2 正常语义化；X3+ 保留精确扩展数据。

## 7. 共通字典

共通字典是**传输层 `.nemat`** 的可选机制，不是原生 `.nema` 的新领域类型。发送端与接收端必须使用一致的字典和协议版本；字典入口可复用常见字段片段以降低传输体积，但必须保持原文逐字节可逆。参见 [共通字典完整案例](COMMON_DICTIONARY_v1.5.md)：包含 `.nema` 原文、真实 `.nemat` 传输流、`^0`/`^1` 字典指令与数字前缀重建。请通过随包提供的 `codec/nemat.py`、`codec/cli.py` 和测试验证实际支持的字典控制形式。不得把字典符号写入普通 `.nema` 并误认为原生语法，也不得假定压缩一定节省 Token。

## 8. 转义、准确性和限制

正文 ASCII 空格承担分列作用；字面空格可写 `\ `；字面反斜线 `\\`；原生字面 Tab `\t`；需要保持显式精确标识可用 `\=`。具体取决于所在字段的语义；不要把自然语言语义还原当作字节无损过程。`.nemat` 的端到端往返另行校验。

## 9. 版本迁移与兼容

v1.3 的 Tab 领域头、未显式区分 5W1H 的写法均不直接兼容；通过 `python -m tools.migrate_v13_to_v15 input.nema output.nema` 显式转换。历史基准不得改名成为新版本的真实 Token 结果；需重新以目标模型 tokenizer、完整提示词与解析消耗计费口径实测。

## 10. 测试与部署

参考解释器：`codec/native.py`；可逆传输 Codec：`codec/nemat.py`；最小示例：`examples/`；网站首页：`website/index.html`；语法列表：`website/syntax.html`；统一文档中心：`website/docs/index.html`。生产环境须对超长输入设置大小上限，并针对错误域头、全角空格、孤立续写、重复 ID、悬空边做负例测试。
