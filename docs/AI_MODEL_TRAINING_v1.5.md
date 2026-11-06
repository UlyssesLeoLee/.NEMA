# NEMA v1.5 · AI 模型学习、微调与评测指南

## 训练目标
让模型原生输出 NEMA v1.5 的确定性结构，必要时直接输出合法 `.nemat` 压缩文本，用户前端/IDE/IME 无需再次调用模型即可无损解压。训练不是重新训练 tokenizer，**无法凭空改变一个文本串在目标 tokenizer 下的 Token 数量**；训练的主要贡献是减少每次传协议提示及生成格式错误和重试。

## 必学规则
默认 Table；显式 `?` 5W1H（What/Why/How/Who/When/Where）；显式 `>` Graph；Table 仅首行 `\\ ` 声明表头，否则首行为内容，列自动 `column1...`；正文单 ASCII 空格横向分列，N 个行首空格续写 X(N−1)；英文 `HTTPItIs` 断为 HTTP It Is，中日文连写；`Tab+$N` 字典与 `^N`，字典项不可拆分；`Tab+\数字` 为默认表格领域头，`Tab+?数字` / `Tab+>数字` 为另两种模式；`.nemat` 额外词典与 RLE（旧前缀编码暂不生成）必须通过解码恢复完整 `.nema`。

## SFT 数据约定
`training/nema_v1.5_train.jsonl` 使用 ChatML 风格 `messages`；`nema_v1.5_holdout.jsonl` 必须保持不与训练集完全相同的源示例。将 `NEMA_SPEC_v1.5_zh.md` 的关键规则作为 system/task 指令，输入自然语言或完整已校验样品，输出 NEMA 或人类渲染 JSON。训练前以解析器检查所有目标 `.nema`，保证领域头、字典下标、序列化和终止符完整。

## 评测必须包括的对抗样本
1. 无表头默认 Table（首行不能丢）；2. `\\ ` 有表头；3. `\\^0` 表格首行不误认；4. X0..X5 纵向续写；5. ` .` 尾部空字段及 `\\.`；6. `A>X>B`、`A<X<B`、`A=X=B`、自环和同点多条边；7. `HTTPItIs`；8. `Validate^0BeforeAccess`；9. CJK 紧凑连续文本；10. 高熵数据强制原文回退；11. 未定义字典编号必须拒绝；12. 被恶意注入的超长 RLE 和异常 Header 必须拒绝。

## 正式模型验收口径
单独记录模型原始输入 Token、原始输出 Token、总协议说明 Token、修复/重试次数、格式正确率、语义一致率、端到端耗时。所有结果按具体模型及 tokenizer 版本标记。**本项目的本地 SentencePiece BPE/Unigram 实测不等于任何商业模型实际节省率**；压缩输出可由模型生成是待检验的假设，不可仅凭编解码器无损往返证明模型已学会。
