# .NEMA v1.5 · TEST DESIGN

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

强制检查：三类领域头、显式/隐式表格表头、5W1H 六列、Graph 顶格、X2/X3+、字面转义、全角空格拒绝、CRLF 拒绝、末尾 3 LF、重复域、重复 Node/Edge ID、悬空 Edge、.nemat 无损往返、迁移语义等价、网页链接和弹窗 Esc/遮罩/× 退出。

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

旧版详细推导与研究见 [TEST_DESIGN v1.3](TEST_DESIGN_v1.3.md)，但此处所有语法规则以 v1.5 为准。
