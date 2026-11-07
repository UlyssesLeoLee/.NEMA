# .NEMA v1.2 · UT / IT / ST 测试设计

UT: `tests/test_v12.py` — 5W1H What-first 纯文本、英文 PascalCase、`HTTPItIs`、`I'm what?`、中日文、表格纵向续写、Graph 一空格 Node / 零空格 Edge / 两空格 X2、箭头方向、平行边/环、Graph ID 唯一、表头拒绝、字典/前缀/转义无损、随机高熵原文回退、语义 JSON 等价。

IT: 网页与解释器统一样本 JSON；空格显示开关与复制真实字节；中日英浏览器交互；Node/Edge hover、focus、tap；下载页相对链接、解释器 ZIP 可解压；Token Lab 数据和 `latest_results.json` 完全一致。

ST: Playwright Chromium 桌面/手机 smoke；性能、动效降级、WebGL 不可用静态回退；离线执行标准 Python 解释器。Firefox/Safari、真实 Windows TSF、Rust 产品集成、商业模型 tokenizer API 未经过本包实机验证，不标称通过。

失败必须返回显式错误；禁止静默把非法 Graph Node 识别为 Edge。测试脚本不调用第三方模型，不写源代码文件。


## R7 额外验收项目

1. Graph X3+ 不丢失：X3 `APIKey`、`HTTP401`、`SHA256` 原样保留；X2 悬停/Edge 方向不变。
2. `examples/*.positional-tagged.json` 标记 `w/t/g`，允许按类型判型；不将无类型的极简位置式 JSON 误标为自描述。
3. 网站中日英标签与基准文件完全对应，代码空格和 Tab 始终以真字符展示与复制。
4. 独立解释器 ZIP 内的 `codec/native.py` 与完整包中完全一致；所有相对资源引用有效。
5. 伪随机合法源文件做无损 encode→decode 比较；与 Git/Windows IME 的真实集成仍需后续验收。
