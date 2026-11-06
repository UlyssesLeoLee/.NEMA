# IME1.0 × NEMA v1.5 · UT / IT / ST

| ID | 层级 | 输入/事件 | 期望 |
|---|---|---|---|
| IME-UT-01 | UT | composition 尚未 commit | 不压缩，不出网 |
| IME-UT-02 | UT | `.nema` `\\ Agent State` | 按表头处理，不把字段当正文 |
| IME-UT-03 | UT | 未标注英文混合 `HTTPItIs` | 不擅自改写为标识符 |
| IME-UT-04 | UT | LSP 认证 `APIKey` | 字典 atom，不拆成 API Key |
| IME-IT-01 | IT | 粘贴 NEMA 60 领域 | 后台转换完成，主线程不阻塞 |
| IME-IT-02 | IT | IME/IDE 同时安装 | 仅 IME 自动写传输镜像 |
| IME-IT-03 | IT | 用户手工 IDE 转换 | IME 暂停并在租约释放后继续 |
| IME-IT-04 | IT | 高熵输入候选更贵 | 选择原生 NEMA |
| IME-ST-01 | ST | 真正 Windows TSF composition / 候选窗 | 与日/中/英文输入无冲突 |
| IME-ST-02 | ST | 凭证文本和 SecretRef | 明文密钥绝不进入日志和词典 |
| IME-ST-03 | ST | 低内存/崩溃/网络断开 | 无写入损坏，待机重试 |

上述是供后续集成开发实施的测试设计，**未在仓库中的实际 TSF/VS Code 版本执行**。
