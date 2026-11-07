# .NEMA v1.5 · TRANSPORT

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

原生 `.nema` 与传输 `.nemat` 是不同协议。共通字典可选，用于降低重复片段的传输体积；传输控制字与原生字段不可混淆。必须校验 `decode(encode(source)) == source`（严格逐字节），不同字典与前缀压缩收益需要基准实验。

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

旧版详细推导与研究见 [TRANSPORT v1.3](TRANSPORT_v1.3.md)，但此处所有语法规则以 v1.5 为准。
