# .NEMA v1.5 · INTERPRETER USAGE

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

Python 参考解释器位于 `codec/native.py`。`parse(text)` 返回领域语法对象，`view(text)` 返回语义视图；输入必须恰好三个 LF 结束。显式 Table 表头正文首字符为 U+0020 SPACE，无表头则为 `table_implicit`。跨版本必须先迁移。

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

旧版详细推导与研究见 [INTERPRETER_USAGE v1.3](INTERPRETER_USAGE_v1.3.md)，但此处所有语法规则以 v1.5 为准。
