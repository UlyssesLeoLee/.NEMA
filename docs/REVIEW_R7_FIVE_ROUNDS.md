# .NEMA v1.2 R7 · 五轮对抗式自审与修复

**状态：协议本体与解释器已实装修订；原有三模式语法不变。本报告记录真实问题，不以 UI 演示冒充编码成本。**

## 第一轮：格式与语义完整性（高）

**复现：** ` A LoginAPI Authentication APIKey` 的四列在 `parse()` 中存在，但原版 `view()` 只返回 X0/X1/X2，直接丢弃 X3=`APIKey`。Edge 的 X3 `HTTP401` 同样被遗漏，造成 JSON 语义视图和 IDE/IME 开发接口的信息缺失。

**修复：** Graph 语义输出增加可选 `extensions`，按 `X3`、`X4`… 归档非空扩展列；机器标识符保留完整拼写，纵向 X3 续写继续以 3 个行首空格定位。X2 仍只负责描述，不影响 Edge 方向。不存在 X3 时不输出额外键，原有数据兼容。

## 第二轮：压缩与边界攻击（高）

测试 `\^`、`^`、反斜杠、纯数字、字典索引、`Tab+$` 字典声明、前缀组索引、Graph X3 的无损 encode/decode。新增固定随机种子压力样例，保证经过 .nemat 往返恢复的是整个 `.nema` 的 UTF-8 字符串，而非仅渲染后的内容。

**限制：** 当前是 Python 标准库参考 Codec，尚无 Rust ABI、Windows IME TSF 实际回归。高熵文本节省不足时应回退原文，不能因为压缩技术存在就宣称正收益。

## 第三轮：网站三语、Graph、可访问性（中）

**复现：** 网站首页残留旧 Graph 用法 `\=LoginAPI` 的提示；日文首页指标声称对比位置式 YAML，但实际 `renderBench()` 使用 JSON 对象式数据计算。

**修复：** 当前 Graph 名称 `LoginAPI` 默认原样保留、不再需要旧标识；中日英说明同步修正。日文标签明确对应对象式 JSON。主页 Graph Inspector 支持显示 X3+（点击固定详情）；悬停仍聚焦 X2，降低认知负荷。新建三语 `website/audit-r7.html`。代码区域使用实际 ASCII 空格、等宽字体、`letter-spacing:0` 和 `white-space:pre`；可视空格开关仅改变显示副本，不改变复制文本。

**浏览器核验方式：** 使用系统 Chromium 对离线注入的 HTML + JS/CSS 进行 DOM/交互断言；环境阻止 file:// 和 localhost 导航，故不声明正式 HTTP 浏览器端到端验收。

## 第四轮：Token 口径与 JSON 对照（中）

**复现：** 原“位置式 JSON”中 Table 与 Graph 都是 `[id,revision,array,array]` 形状，必须事先从外部约定每个领域的模式，否则不能独立判型。

**修复：** 保留 R6 8 组对象 JSON 与极简位置式 JSON 原始测量，新增**有 w/t/g 类型标记**的可独立判型位置式 JSON，并以同一套本地 SentencePiece BPE/Unigram 真实重新计数。原报告数字不覆盖、也不把编码层压缩率说成 GPT/Claude/Gemini 账单节省。

参见 `bench/tagged_json_audit_r7.json`、`bench/tagged_json_audit_r7.csv`、`examples/*.positional-tagged.json` 和网站审查页面。额外模式标签仅改善自描述，不改变字段顺序仍需版本化 schema 这一事实。

## 第五轮：测试、解释器下载、文档与发布（中）

- 同步独立解释器 ZIP 内的 `codec/native.py` 与主版本；增加 X3 自检用例，防止网站下载的是旧解释器。
- AI 训练黄金集新增 Graph 扩展属性；IDE1.0/IME1.0 设计增加无损/字段一致性验收。
- 检查全部站内相对引用、JS 语法、文件 SHA-256、两个 ZIP 的 CRC 和内容一致性。

## 实测结果与适用边界

本次新增的 tagged JSON 数据在本地 BPE 下（`nema` vs **可独立判型的位置式 JSON**）：

| 场景 | .nema BPE | 带标签位置 JSON BPE | .nema 节省率 |
|---|---:|---:|---:|
| 英文 60 领域 | 3,012 | 3,971 | 24.15% |
| 中文 60 领域 | 5,532 | 6,131 | 9.77% |
| 日文 60 领域 | 7,062 | 7,661 | 7.82% |
| 表格 200 行 | 4,899 | 5,892 | 16.85% |
| Graph 40 Node / 160 Edge | 6,952 | 7,553 | 7.96% |

这些是**八组有限的合成数据**之一部分，不代表生产业务数据分布，也不包含训练提示、纠错、输出与重试。与 JSON 对象式比较的百分比更大，但不等于对最强对照的优势。

**剩余待办：** GPT/Claude/Gemini 官方 Token/账单评估、真实 Agent 端到端任务、Safari/Firefox、正式网站部署、Rust Codec 和 Windows IME/IDE 插件实装。它们都未宣称通过。


## 实际执行记录（R7）

- 标准库单元、扩展语义、Codec、安全与网站/基准一致性：**52 / 52 PASS**，命令 `python -m unittest discover -s tests -p 'test*.py' -q`。
- 1800 个固定种子随机化生成尝试（仅统计语法有效的样本）中的字节往返检查：`python tests/stress_r7.py` PASS。包含 Graph/Table/5W1H 及多种控制字符。
- Chromium **离线 DOM 注入**：1440/800/390 三宽度主页，Graph Node/Edge 检查器及 X3、源码空格切换、三语和审查页 8 组 BPE/Unigram，断言全部通过。执行 `python tests/browser_r7.py`（须本机 Playwright + Chromium）。环境限制已明确列出，不能推断正式域名的网络访问通过。
- **完整 JSON 基准数据不被改写**：本轮复核读取当前 `latest_results.json` 的 8 组 BPE/Unigram 数值，直接对 `examples/*.nema`, `.json`, `.positional.json`, `.positional.yaml` 本地重新分词。新标签基线见独立文件。
