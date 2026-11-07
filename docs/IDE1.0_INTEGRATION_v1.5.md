# .NEMA v1.5 · IDE1.0 INTEGRATION

> 当前版，2026-11-07。[当前语法规范](SPEC_v1.5_zh.md)；v1.3 资料仅作为历史版本。

## 设计要求

IDE 的代码视图必须显示真实半角空格，tab-size:1、letter-spacing:0、word-spacing:0。语法高亮按 ` ?`、` `、` >` 三种领域头判定；正文 X 坐标从零开始。语义视图允许展开 5W1H、Table 和 Graph；保存回写不得自动增加空格或替换为全角。并发 Agent 使用稳定领域 ID 进行锁定和版本合并。

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

旧版详细推导与研究见 [IDE1.0_INTEGRATION v1.3](IDE1.0_INTEGRATION_v1.3.md)，但此处所有语法规则以 v1.5 为准。
