# NEMA v1.1 开发 WBS（实施目标）

| 阶段 | 实施任务 | 验收输出 |
|---|---|---|
| P0 | Rust `nema-codec`：SPACE-X parser/serializer，PascalCase 渲染，字面量及转义 | Python/Rust 金样例逐项一致 |
| P0 | `.nemat` 可逆压缩：词典、数字前缀、逐字节校验 | 100% roundtrip + 失败回退 |
| P1 | IME1.0 的授权探测、输入稳定提交、异步去抖与 sidecar | 不阻塞候选、不在组合中转换 |
| P1 | IDE1.0 的三视图、用户显式手动转换、结果回滚 | UI 可见且不覆盖原文 |
| P1 | 双端单写入者 IPC / 锁 / hash / CAS | 并发无重复转换或覆盖 |
| P2 | 可选模型 tokenizer 插件、本地字典策略 | 计费估算与字节代理分离 |
| P2 | SFT/eval/网站基准版本同步，迁移 Tab-X 旧资料 | 生成的金样例与网页一致 |
| P3 | Windows TSF / IDE 真实端到端 UAT，性能、安全审查 | 有独立测试证据才发布 |

所有任务要求先更新设计与测试设计，再实现、验证；不得把文档计划写成已完成的产品能力。
