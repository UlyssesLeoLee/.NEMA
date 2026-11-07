# NEMA v1.1 参考实现验证记录

- Native Python parser / renderer / `.nemat` encoder / decoder：`python -m unittest discover -s tests -q`，**40/40 项通过**。
- 中英日 60 领域紧凑/纵向版本：机器语义视图逐字段一致；见 `bench/reproduce.py` 中断言。
- 本地 SentencePiece BPE 与 Unigram，完整 `bench/results.json`、`results.csv`（无远端模型 API）。
- 网站 JavaScript：`node --check`，首页三模式与 Graph 反向箭头、独立 Token 页面中英日样例切换及 BPE/Unigram 切换：浏览器内存 DOM 测试通过。
- **限制**：当前自动化环境浏览器导航到 `file://` 与 `http://127.0.0.1` 被管理员策略阻止，所以没有宣称完整网页网络加载/样式截图验收通过；改用内存 DOM 和本地 JS 脚本进行交互验证。用户本地正常浏览器打开文件应可用，但仍需最终独立设备验收。
- **未完成**：Rust `nema-codec` 产品实现、IME1.0 Windows TSF UAT、IDE1.0 UI 真实接入和商业模型官方 Token 测量。

## 网站 R3 Graph Hover（2026-11-07）

- `python -m unittest discover -s tests -q`：**54/54 项通过**，含现行 NEMA 解析、Codec、静态文档一致性与 Hover 实现检查。
- `python tests/test_browser_r2.py`：已有网站旧版 Graph 选择、三语、三模式、三个视口的浏览器回归通过。
- `python tests/test_browser_r3_hover.py`：**33 项 Chromium 行为检查通过**，覆盖 Node / Edge 悬停说明、正/逆/无向、焦点与 Escape、点击详情、移动端固定说明、三语和横向溢出。
- JavaScript 静态语法：`node --check website/app.js`、`website/graph-guide.js` 等通过。
- 浏览器以本地 HTML+JS+CSS 内联后的离线文档运行，而不是 HTTP 正式部署；未验收 Safari、Firefox、IDE1.0/IME1.0 实际集成。

## Website R4 — 五轮审核补充（2026-11-07）

- 原有用例保留，增加 `tests/test_five_round_audit.py`（10 项 Python `unittest`）。
- 新增 `tests/test_browser_r4_five_rounds.py`：桌面/平板/手机的动态指标、键盘标签页、Graph 选择后恢复焦点、只读 Hover、双向平行关系与多自循环不重叠、三语 ARIA/触屏。
- 详见 `docs/WEBSITE_REVIEW_R4_FIVE_ROUNDS.md`。此处仅记实际验证的参考实现，不声称 IDE/IME 已接入，也不将本地 SentencePiece 结果视为商业模型官方值。
