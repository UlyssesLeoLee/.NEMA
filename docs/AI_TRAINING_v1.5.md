# .NEMA v1.5 · AI TRAINING

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

训练 Agent 时必须用真实 U+0020 首字符，三种领域头模式不可混淆。Graph Node、Edge 均 X0 顶格，隐式表格列名 columnN 自动生成。样本须分别覆盖正常、边界与错误示例。训练与评估数据需记录 tokenization 模型、token 用量、版本指纹以及 parser 语义一致率。

## 标准语法示例

```text
 ?Task1 1
BuildLoginFlow PreventLeak VerifyToken Owner Today AuthService
 Tauto1 1
A Ready First
B Blocked Second
 >Gauth1 1
A LoginAPI Authentication
B TokenStore SessionStorage
A>X>B Reads VerifySession


```

## 历史细节与继承资料

旧版详细推导与研究见 [AI_TRAINING v1.3](AI_TRAINING_v1.3.md)，但此处所有语法规则以 v1.5 为准。
