# NEMA v1.4 发布说明

这是 **Table-first explicit-header** 的统一项目包。与 v1.3 对比，唯一破坏性变化是：默认 Table 的第一条正文**只有**以 `\\ ` 起始才视为表头；否则是数据，缺省字段名 `column1...columnN`。同时将新表头定义更新到解析器、Python 压缩参考实现、训练样本、三语静态网站、IDE1.0 和 IME1.0 接入设计以及 Token 基准脚本。

依然有效：What-first 显式 5W1H；Graph 带身份有向 Edge；Tab 控制行与普通空格正文；纵向意群；` .` 尾部空字段；文档词典 `Tab+$N`；`.nemat` 可逆字典/RLE/数字前缀；双产品 IME 自动优先、IDE 手动接管。

限制：当前运行代码是 **Python 参考实现**，Rust 共享内核及真实 IDE/IME 安装运行仍未完成；本地分词基准不代表 GPT、Claude、Gemini 账单；网站是静态介绍与交互示例，不是部署后端。
