# .NEMA v1.5 · IME1.0 INTEGRATION

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

IME 根据语法域提供候选。领域头候选必须生成真实 U+0020，5W1H 加 ?，Graph 加 >，Table 直接接 ID。IME 输入法候选避免自动缩进与 Tab 替换；在 X0 与 X2/X3+ 语义坐标上分别提示 Node、Edge 与扩展字段。

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

旧版详细推导与研究见 [IME1.0_INTEGRATION v1.3](IME1.0_INTEGRATION_v1.3.md)，但此处所有语法规则以 v1.5 为准。
