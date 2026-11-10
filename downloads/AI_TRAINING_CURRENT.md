# .NEMA · AI 训练与解析契约（当前审查候选规范）

> 本文面向模型、解析器和 IDE 集成。其语法属于审查候选，不得与历史 v1.5 解释器混淆。需要按随包 `interpreter/nema_strict.py` 和 `website/strict-parser.js` 的实际实现核验。

## 第一优先级：确定性和正确性

- 只用 ASCII 半角空格 U+0020 表达语法分隔、坐标和领域前缀。不要使用原始 Tab 或全角空格。
- 领域头整个物理行严格匹配：` \N REV` (Table)、` \?N REV` (5W1H)、` \>N REV` (Graph)。N 和 REV 是没有前导 0 的正整数。
- 在正文中使用 `\ ` 表示同一字段内部的字面空格，`\\` 表示字面反斜杠。未知转义必须报错。
- `~` 是 Null，`\e` 是空字符串，`\_` 是缺失；这三种 AST 状态不可混用。
- Table 显式表头必须以顶格 `\# ` 明确声明，不能靠首行前置空格推断；省略表头时自动生成 column1、column2……
- 5W1H 的六列固定为 What、Why、How、Who、When、Where，缺失中间字段必须显式占位。
- Graph 顶格 Node/Edge，`A>X>B` 等关系表达式必须完整。Node 和 Edge ID 应稳定唯一，引用应在领域结束前有效。
- 续写按当前模式与前导空格数量定位；不存在的记录或字段不可被静默创建。
- 新旧版本迁移必须显式进行，禁止“猜测着解释”。

## 基础例子（ASCII 原文）

```nema
 \1 1
\# Name Status Detail
Claude Ready Verified
~ Running Build
 \?2 1
BuildLogin PreventLeak VerifyToken AuthAgent OnRequest API
  RetryOnTimeout
 \>3 1
A LoginAPI Authentication
B TokenStore SessionStorage
A>X>B Reads VerifySession
 CacheExpiredRetryOnce
```

## 压缩层

`.nema` 是源语义格式；`.nemat` 具有独立的可逆传输头，文件级字典引用在 `.nemat` 中才生效。对源文件的 `^`、换行和空白应逐字节往返；压缩需要以实际目标 tokenizer 加上解码协议成本验证，不可凭字符减少直接认定降低 Token。

## 训练与验收

1. 学习领域头、显式空值、转义、Graph ID、三模式独立解释。
2. 使用 `bench/RULE_MATRIX.json` 覆盖合法、非法和待定规则；待定不冒充支持。
3. 将每个生成样本送入严格解释器，输出 AST 或准确的错误定位。
4. 用相同语义比较 .NEMA / .nemat / 紧凑 JSON / 紧凑 YAML，附上目标 tokenizer、编码文本、解码说明和总成本。
5. 不把文档中未实现的候选语法当成生产能力。
