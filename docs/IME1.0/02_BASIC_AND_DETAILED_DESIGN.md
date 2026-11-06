# IME1.0 × NEMA v1.4 · 基本／详细设计

## 结构
`TSF composition` / `VS Code bridge` → `NEMA scope gate` → `pime-core` 中共用的 Rust NEMA Codec → `dictionary proposer` → `token-profile chooser` → `immutable mirror (.nemat or .nema)`。

建议把 NEMA Codec 以独立 crate 或 workspace dependency 引入，源码与 IDE 同源；与现有 pime-core、pime-ipc 和 VS Code 桥接保持分层，不把解析器写进 TSF DLL 内。TSF 线程仅发轻量 commit 消息，不做全文件压缩或模型请求。所有实时转换在 worker 中可取消、可回滚，避免输入卡顿。

## 原子词识别流程
`composition commit -> 确认 NEMA workspace -> 查询 LSP/candidate/user-approved atoms -> 检查现有共享字典 -> 稳定编号 -> 原生 NEMA 校验 -> 构造候选 .nemat -> byte-exact 解码校验 -> 目标 Token 比较 -> 更新临时传输镜像`。

自动判断普通 `HTTPItIs` 不是变量名；只有经过上下文证实的 `APIKey`、`HTTPStatus` 等才作为原子。中文或日文的 `请检查APIKey是否有效` / `APIKeyを確認してください` 默认不额外插空格或换行；英文语义分词由渲染层决定。原始密钥/密码内容不进入共享词典，提示用 SecretRef。

## 生命周期和仲裁
IME 自动写传输镜像，**不直接把用户源文强制替换成 `.nemat`**；UI 应允许主动写回时经用户确认。IDE 默认观察者；IDE 手工按钮获得租约后，IME 暂停该文档的 auto-commit，释放后重算 generation。旧 generation、重复通知或取消的 composition 结果不允许覆盖较新的缓冲区版本。

## 可观察性
日志只能记录 `document-hash`,`revision`,`selected-mode`,`tokens-before/after`,`codec-version`,`reason`；不记录字典原文、密码或传输全文。提供一键撤销和显示候选来源。

## Windows 验证
测试 Win11 真实 TSF DLL 注册/卸载、繁简中日韩、VS Code 宿主兼容、输入法切换、崩溃恢复、DPI、多屏、断网、60min 压力与 200ms 响应预算（预算为验收目标，不是当前实测）。**实际集成尚未完成**。
