# .NEMA / JSON / YAML 本地 Token 实测方法

本次脚本 `bench/reproduce_v12.py` 使用完全相同的一组语义领域，分别输出可执行 `.nema`、无损 `.nemat`、**完整 JSON 对象形式**、**位置式 JSON（去重复字段名）**和位置式 YAML。它们保留域 ID、修订、5W1H、表格列名、Node/Edge 的 ID、方向以及文本说明。对于强对照，位置式格式的字段顺序按 `.NEMA` schema 外部约定，不能误称 JSON 通用自描述格式。

Token 数来自本地附带的保留空白的 SentencePiece BPE 和 Unigram，亦计算 UTF-8 bytes。不得宣称商业模型账单节省率或拿旧版 69% 的字节率当作最新 Token 率。

公式：`saving=(baseline_tokens - candidate_tokens)/baseline_tokens*100%`。允许出现负值。字节大小并非 Token 开销。所有样本、.nemat 字典首部、脚本及结果 JSON/CSV 在包内可复现。

样本覆盖英语/中文/日语各 60 领域、200 行 Table、40 Node+160 Edge、60 领域高随机性、短文本以及小 Graph。**高随机性弱点必须报告**。即使 `.nemat` 优势较大，真实 LLM 端到端比较也需要语法说明、返工、重试、模型训练与接口费用。

**环境：** Python 标准库 + 第三方 `sentencepiece` 用于 benchmark；编解码器默认纯 Python 标准库。模型文件来自此前 NEMA 本地实验，不是 GPT 或 Claude/Gemini 官方词表。

## R7 类型标记校正

旧版位置式 JSON 直接使用 `[id,rev,columns,rows]` 表示 Table、`[id,rev,nodes,edges]` 表示 Graph；两者的最外形状相同，**独立文件并不能自描述地判定模式**。旧版数字仍可作为外部模式注册表已提前协商的极限成本基线，但不能与完全自描述 JSON 混为一谈。

新增 `bench/tagged_json_audit_r7.json` / `.csv` 和 `examples/*.positional-tagged.json`：第一项使用 `w`（5W1H）、`t`（Table）、`g`（Graph），在同一行带上模式标签，从而独立判型。所有数值由当前捆绑 SentencePiece 模型重新计算；不更新/覆盖 R6 原始 8 组数据。它仍依赖位置式字段顺序的版本化 schema，真实模型费用不能据此推断。
