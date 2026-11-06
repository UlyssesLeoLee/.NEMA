# IME1.0 × NEMA v1.4 · 要件定义（仅项目接入设计）

## 实际集成基准
仓库 `https://github.com/UlyssesLeoLee/IME1.0`：现有 `01_Source/crates/pime-core`、`pime-tsf`、`pime-ipc`、`pime-ai-worker` 和 `editor-bridges/vscode`；项目 README 明确指出 TSF 尚未在真实 Windows 注册验证。NEMA 新需求不得被宣称已安装可用。

## 目标
IME1.0 是**默认自动转换所有者**：用户输入完成后在稳定 composition commit 时触发 NEMA 意群/词典候选检测，符合规则且确定为 `.nema` 目标时自动将权威源的版本映射成最省 Token 的 `.nemat` 或原文传输镜像。对于 Rust/TS/Python 等正常编程输入，不得随意改写源码。

## 需求
| ID | 内容 | 验收 |
|---|---|---|
| IME-01 | 自动正确识别 `.nema` 作用域 | 只对 IDE/编辑器显式激活的 NEMA 缓冲区操作 |
| IME-02 | 智能提炼共享字典 | 从用户确认、LSP、候选和已有字典生成稳定 `^N` |
| IME-03 | 明确前缀和重复字符编码 | `Tab+数字` 只在传输模式、RLE 可逆 |
| IME-04 | 支持三语连续书写 | 中文/日文直接连写，英文 PascalCase 消歧 |
| IME-05 | **默认自动**；IDE 手动抢占时暂停 | 避免 IME/IDE 双重压缩 |
| IME-06 | 原文可撤销 / 转换可重试 | 重试幂等，撤销恢复所有意群 |
| IME-07 | 敏感内容预检 | 不收集实际密码/API Key 值到共享词典 |
