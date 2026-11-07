# .NEMA v1.5 · JSON COMPARISON METHOD

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

以相同 5W1H、Graph 节点/边、显式/隐式 Table 的语义树导出结构等价 JSON/YAML 后比较长度与目标 tokenizer Token。需要加入解释器说明提示词、错误纠正与往返损耗，不能只比较原始字节。此前 v1.2/R7 统计是历史实验。

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

旧版详细推导与研究见 [JSON_COMPARISON_METHOD v1.3](JSON_COMPARISON_METHOD_v1.3.md)，但此处所有语法规则以 v1.5 为准。
