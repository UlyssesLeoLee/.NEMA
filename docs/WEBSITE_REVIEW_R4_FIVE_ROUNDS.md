# NEMA v1.1 · Website R4 五轮对抗式审核报告

状态：**网站修订版**；底层 NEMA 语法与 `.nemat` 协议未修改。审核日期：2026-11-07。

## 审核基线与方法

基线为 `NEMA_v1.1_Website_R3_Hover`，执行 `python -m unittest discover -s tests -q`（54/54 通过）和 `python tests/test_browser_r3_hover.py`（33 个 Chromium 检查通过）。审核不仅依赖现有通过用例：主动构造了键盘焦点、反向平行边、多重自循环、语言切换和网站/测量数据分歧等失效场景。R4 所有更改在 `website/`、`docs/`、`tests/` 等展示与验证层；`codec/native.py`、`codec/nemat.py`、`training/` 的语义和原始 `bench/results.*` 未改变。

## 第 1 轮 — 协议 / 语义字段一致性

**审查内容**：What-first 5W1H、Table 表头、Graph X0/X1/X2，X2 非必填，X0 决定方向，`\\=LoginAPI` 为精确保留标识符。

- 检查 Node A 的 `Authentication` 仅映射为 `description`，不会凭说明创建 Node 或 Edge。
- 检查 X2 纵向续写属于当前图元素；`B<Y<C` 始终表示 C → B。
- 以 `test_five_round_audit.py` 添加覆盖当前示例和说明来源的断言。

**结论**：底层语法无需改动；保持表格、图与 5W1H 的单一书写规范。

## 第 2 轮 — 图拓扑 / 悬停 / 复杂关系

**发现 G-01（已修复）**：一对节点的多条相反方向边按各自箭头方向计算偏移法线，可能落在同一侧；多个自循环完全重叠，影响命中和读取。

**修复**：按无序节点对建立关系分组，使用与方向无关的标准法线分配平行边通道；自循环按 Edge 次序扩展独立曲线路径。按 `Map` 预分组和记录通道索引，避免每条边重新扫描所有 Edge。方向箭头仍由 AST 的 `direction` 决定，不从位置推导。`test_browser_r4_five_rounds.py` 注入相反边和第二个自循环，验证路径不同、方向准确、Hover 文本对应具体边。

## 第 3 轮 — 键盘 / 无障碍 / 三语 / 触屏

**发现 U-01（已修复）**：在 SVG Node/Edge 上按 Enter 时，Graph 重新渲染后 DOM 焦点落到 BODY，键盘用户丢失操作位置。

**发现 U-02（已修复）**：主页三种数据模式虽然设 `role=tablist`，但子按钮未设置 `role=tab` 与 `tabpanel` 对应关系，也没有 Left/Right/Home/End 键盘切换。

**发现 U-03（已修复）**：Graph 专属说明页切换中文、日文、英文时，焦点元素的 `aria-label` 仍可能保留初始化语言。

**修复**：选中重渲染后恢复对应 SVG 或列表按钮焦点；建立 WAI-ARIA tab / tabpanel 映射及键盘切换；Graph guide 每次切换语言同步刷新 ARIA 名称。所有弹层通过 `textContent` 显示 AST 文字，仍支持 Escape 和手机点击。

## 第 4 轮 — Token 实测 / 压缩器 / 资料一致性

**发现 B-01（已修复）**：`bench/results.json` 含 **11** 个实测场景，旧网站 `benchmark_data.js` 仅嵌入 **9** 个，遗漏 `english_one_domain` 与 `english_http_example` 两组极短且压缩回退原文的案例。

**发现 B-02（已修复）**：主页柱状图将 3012/3849/1953 写死在 UI 代码中，后续更新基准时可能出现页面数字漂移。

**修复**：网页数据完整同步 11 个场景；主页百分比和柱状图由 `BENCHMARK.cases` 读取；新增静态一致性测试比较网站数据与 `bench/results.json`。实际重运行 `python bench/reproduce.py`，其后对比基线，`bench/results.json` 和 `bench/results.csv` 字节保持不变。

**范围提醒**：以上是本地保留空白的 SentencePiece BPE/Unigram，不是 GPT/Claude/Gemini 官方计费 Token；不含提示词与错误重试开销，不扩大宣称范围。

## 第 5 轮 — 回归、文档、链接与完整性

- 执行原有全部单元测试、R2/R3 浏览器回归、R4 新增浏览器行为检查。
- 校验 `.nema` 示例可解析、选择出来的 `.nemat` 可完全恢复到原始 UTF-8 内容。
- 校验三语 Graph 指南存在 X2 说明、反向边，以及文档索引链接。
- 检查所有本地 HTML `href`/`src` 文件引用、JavaScript 静态语法、归档 ZIP CRC 与逐文件 SHA-256 清单。
- `review.html` 把五轮主要发现和验证范围直接展示在网站；规范文件和训练数据未发生未经测试的变更。

## 交付验收与未覆盖范围

当前 CI 风格验收入口：

```bash
python -m unittest discover -s tests -q
python tests/test_browser_r2.py
python tests/test_browser_r3_hover.py
python tests/test_browser_r4_five_rounds.py
python bench/reproduce.py
node --check website/app.js
node --check website/graph-guide.js
node --check website/token-page.js
```

浏览器回归采用 Playwright + Chromium，将静态 HTML/CSS/JS 内联到页面运行，覆盖桌面、平板、手机与三语；**没有**验证 Safari、Firefox、正式 HTTP 部署、Windows TSF 或实际 IDE1.0/IME1.0 安装。`bench` 使用本地 SentencePiece；真实商业模型 Token 账单仍需后续独立测量。

**结论**：R4 修复四类真实缺陷（复杂路径、焦点/ARIA、多语 ARIA、基准数据一致性），保留原生 v1.1 文件语义和 `.nemat` 无损往返。新的悬停、焦点和布局改进只发生在前端渲染层，不增加 NEMA Token。
