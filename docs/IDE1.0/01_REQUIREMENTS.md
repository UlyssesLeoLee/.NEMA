# IDE1.0 × NEMA v1.4 · 要件定义（仅项目接入设计）

## 实际集成基准
IDE1.0 仓库：`https://github.com/UlyssesLeoLee/IDE1.0`。已查阅仓库根 `Cargo.toml`、`crates/` 结构：存在 Rust 内核、CLI、Shell、Web/Desktop Shell。本文建议新增独立 `nema-codec` Rust crate，不假设现有项目已集成 NEMA。

## 需求
| ID | 内容 | 验收 |
|---|---|---|
| IDE-01 | `.nema` 原生编辑与三模式解析预览 | 表格无表头自动 column1…；显式 `\\ ` 可声明表头 |
| IDE-02 | 支持 X/Y 空格二维位置可视化 | 回显源意群坐标，不重排源文件 |
| IDE-03 | Graph 方向箭头、带内容的 Edge 详情 | B<Z<C 画为 C→B |
| IDE-04 | 自动发现、确认并设置共享字典 | LSP 真实标识符优先；可手动锁定，引用^N无损 |
| IDE-05 | “转换”手动按钮 | 默认不抢 IME 写权限；点击后租约提交 |
| IDE-06 | 输入输出 MIME / 文件类型校验 | `.nemat` 解码失败回退，不污染 `.nema` |
| IDE-07 | Token 实测与算法候选预览 | 用户可查看完整词典成本与原文等价性 |
| IDE-08 | 对普通代码文件默认禁用转换 | 只能处理 NEMA 文档或选定结构化文本 |

风险：用户可撤销，支持域版本、冲突报告、敏感词预检。令牌或密码不得上传训练集；不将 `.nemat` 当作代码格式。
