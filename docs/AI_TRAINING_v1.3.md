> v1.3 authoritative Graph delta: `docs/GRAPH_V13_MIGRATION.md`. Node and Edge both start at X0; one leading space continues X2, two X3; domain header still begins with a literal Tab and is unchanged. Historical R7 text below, if quoted, is non-normative.

# .NEMA v1.3 · 大模型学习/训练和评测指南

## 模型任务与语法边界

训练目标是使 Agent 能在正确信任边界内输出/解释 5W1H、Table、Graph：默认 What-first；横向一个 ASCII space 一列，纵向必要时 LF 意群；Graph Node 必须以**一个真实空格**开头；Edge **零空格**；两空格继续 X2。领域头以 Tab 开始，Table 首行以 Tab 开始，尾标记双空行。

不要将 NEMA 当成 Python/Rust 源码压缩器，别把 Graph X2 文本当做可执行路由或自动创建的 node。英文 `HTTPItIs` 可拆成 HTTP it is，但 Graph X1 `LoginAPI` 始终按字面展示。中文和日文不强制拆词；特殊指令/秘钥必须原样保留且避免在字典里收集。

## 训练文件

- `training/sft_train_v12.jsonl`: SFT 正例，使用 messages 数组，正文中含合法 `.nema` 原文（包括两个空白尾行）。
- `training/sft_eval_v12.jsonl`: 独立保留的评测集。不能从训练集把预期答案泄漏到 prompt。
- `training/adversarial_v12.jsonl`: 解析应拒绝的例子（多空格声明、非法箭头、悬空引用、CRLF、缺终止符、重复域等）。拒绝是通过 Python parser 判断而非模型主观打分。
- `training/GOLDEN_CASES.md`: 人类可审查的合法、非法和语义渲染用例。

## 模型指令（示意）

“只输出合法 UTF-8 .nema 文本，不输出 Markdown 围栏。使用 What → Why → How → Who → When → Where，单空格定位列。Graph 节点首空格，Edge 顶格，描述写 X2。所有领域都要有 ID/版本，末尾连续两行完全空白。遇到不确定字段不要猜测凭空补齐。”

## 验收准则

Parse success rate, strict topology validity, graph direction exact-match, X2 provenance fidelity, byte-exact `.nemat` decode roundtrip, English / Chinese / Japanese render equivalence, false-positive structural markers, domain ID consistency。必须计入提示词说明成本、输出 Token、纠错重试、tokenizer 版本和测试集污染。离线编码 Token 不等于实际模型费用。

## R7 补充必测

包含 Graph X3+ 的正例以及不允许跨语义字段丢弃属性的负例：`A LoginAPI Authentication APIKey` 生成节点 X3=`APIKey`；`A>X>B Reads VerifySession HTTP401` 生成边 X3=`HTTP401`。检查 `/docs/REVIEW_R7_FIVE_ROUNDS.md` 所列测试。训练目标不得在 `Graph` 模式生成旧版 `A \=LoginAPI`。JSON 对照应分别报告对象式 JSON、依赖外部模式的极简位置式 JSON、包含 `w/t/g` 模式标签的独立位置式 JSON。
