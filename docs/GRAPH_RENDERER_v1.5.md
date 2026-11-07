# .NEMA v1.5 · GRAPH RENDERER

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

Graph Node 和 Edge 从 X0 顶格。点击 Node 显示 ID、X1 名称、X2 描述；点击 Edge 显示方向及关系 ID。X3+ 保持机器标识原样。悬停可显示简要说明，键盘 Enter 激活、Escape 退出。错误方向符号必须以诊断显示，不可创建假节点。

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

旧版详细推导与研究见 [GRAPH_RENDERER v1.3](GRAPH_RENDERER_v1.3.md)，但此处所有语法规则以 v1.5 为准。
