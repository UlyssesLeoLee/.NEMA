# .NEMA 统一候选语法规范 · 2026-11-07

本规范与历史 `SPEC_v1.2_zh.md` 分离，所有新实现以 `bench/RULE_MATRIX.json` 与 `interpreter/nema_strict.py` 为审查基线。

## 基本不变量
- 只有 U+0020 半角空格承担语法分隔及前置；原始 Tab、全角空格、CR 不允许。
- 领域头完整匹配：` \N REV`（Table）、` \?N REV`（5W1H）、` \>N REV`（Graph），N 和 REV 是非零无前导零十进制整数。
- 字段分隔为一个 ASCII 空格；连续分隔、尾随分隔均报错。字段内部字面空格写 `\ `。
- `~` = Null；`\e` = 空字符串；`\_` = Missing，三者不等价。转义支持 `\ `、`\\`、`\?`、`\>`、`\<`、`\=`、`\~`、`\^`、`\n`、`\r`、`\t` 等；未知转义报错。

## Table
- 显式表头为 `\# Name Status`，不能以行首空格猜测是否表头。
- 不提供表头时自动使用 column1…columnN。第一条数据（包括所有 Missing）确定列宽。
- 可先声明 `\%N` 指定列宽，允许无数据表格；不允许隐式扩列。
- 顶格数据行新建记录，前导 N 个空格续写第 N 列；无目标、Null、Missing 续写报错。

## 5W1H
- X0..X5 依次为 What、Why、How、Who、When、Where。
- 顶格写新记录，最多六列；前导 N 个空格续写 XN（N >= 1）。
- X0 当前无专用续写符；顶格下一行始终新记录。不能由解释器猜测。

## Node–Edge
- 顶格 Node: `A LoginAPI Authentication`；顶格 Edge: `A>X>B Reads VerifySession`。支持 `>`、`<`、`=`，左右运算符必须一致。
- Node 和 Edge ID 在图内唯一，允许关系前向引用，但必须在领域结束前定义端点。
- 前导一个空格续写 X2，两个空格续写 X3，以此类推；不能用此方式续写 X1。

## 共通字典及传输
- ` \!NEMAT1`、` $N`、` @N <JSON 字符串>`、` \!DATA`；压缩数据区允许 `^N` 调用文件字典。
- 不支持递归定义；原文的 `^` 转义为 `\^`，还原时保留原始字节。
- 压缩可能增加 Token，必须与原文及紧凑 JSON/YAML 用同一语义比较；不把局部 BPE 当作模型 API 计费结果。

## 关键边界
- 第一列 Null、空字符串、Missing、第一行全 Missing、空列宽、续写未定义字段、重复 ID、非法关系均已列入独立案例。
- 未冻结事项：5W1H X0 和 Graph X1 的原位追加语法，以及未来是否增加低 Token 的自由文本末列编码。
- R7/v1.5 是历史协议，需显式迁移，禁止混用。

## 执行与验证
`python interpreter/nema_strict.py examples/review_candidate/complete_review.nema`
`python -m unittest discover -s tests -p test_review_matrix.py`
`python bench/compare_review.py`
