# NEMA v1.1 · 网站整体自审与调优 R2

**审查日期**：2026-11-07  
**性质**：网站与文档修订版，不更改 NEMA v1.1 语言协议版本。  
**交付范围**：完整可离线浏览的三语静态网站、Node–Edge 专页、现行参考解析器/压缩器/测试/训练与 Token 基准数据。

## 1. 本轮发现及修复

| 编号 | 原有问题 | 修复后的用户体验 | 验证 |
|---|---|---|---|
| W01 | Graph 原文中 `Authentication` 的位置作用没有解释 | 首页专门展示 Node X0=ID、X1=名称、X2=可选职责说明，且说明不产生任何拓扑结构 | 浏览器 + 静态一致性 |
| W02 | Node 原文和 Edge 原文在界面中没有清楚区分 | 分离的 Node、Edge 两张语义卡，均给出原文、逐列解释、渲染结果 | 浏览器 |
| W03 | Graph 只能点选关系，不能点选节点查看 X2 | SVG 节点和边均可点击或键盘选择；右侧详情区显示 X0、X1、X2 | 浏览器 |
| W04 | `A LoginAPI Authentication` 的 X1 存在 PascalCase 名称被拆词的风险 | 正式 Graph 示例采用 `A \=LoginAPI Authentication`，精确保留标识符；解释普通形式仍合法但语义展示会拆词 | Python view + 三语文档 |
| W05 | 反向箭头、无向关系与说明文字的区别不够直观 | 图例+详解页明确 `A<X<B` 等价 B→A，`=` 无箭头；Edge X2 不决定方向 | Graph 解析对照 + 浏览器 |
| W06 | 复杂图案例难以从主页发现 | 顶部「图结构」导航、独立 `graph-guide.html`、页脚与文档索引相互链接 | 文件链接 + 浏览器 |
| W07 | 英、中、日网站部分页面互相脱节 | 新页面提供三语切换；主页说明和 Graph 点击详情均随语言变化 | 浏览器 |
| W08 | 移动端字段表格易拥挤 | 语义卡单列自适应、按钮可换行、说明分页独立浏览 | 390 / 768 / 1440 CSS 宽度检查 |
| W09 | 页面可能将本地 SentencePiece 结果误解为官方大模型 Token 节省率 | 原有 Token 专页与限定说明保留，结果数据未被改写；一致性测试检查三个英文关键值 | 基准数据一致性 |
| W10 | 文档与网页使用不同 Graph 样例会产生漂移 | 主页 Graph 交互数据直接基于 Python v1.1 解析器渲染输出生成，附独立数据一致性检查 | 8 项静态/解析测试 |

## 2. 关键语法与显示边界

```text
\t>G1 1
A \=LoginAPI Authentication
B \=TokenStore SessionStorage
A>X>B Reads VerifySession
  CacheExpiredRetryOnce


```

上面 `\t` 仅在本段解释中表示一个真实 Tab；实际 `.nema` 文件使用字节 `09`。Graph 的正文仍以 ASCII 空格横向分列，LF 纵向追加。

- Node X0：稳定 ID `A`；X1：名称 `LoginAPI`（`\=` 保留精确字面量）；X2：可选说明 `Authentication`。
- Edge X0：`A>X>B` 指向 A→B，Edge ID 为 X；X1：`Reads`；X2：可选说明 `VerifySession`。续行前两空格追加到 X2。
- 说明仅供 AI 理解、搜索、检查以及 IDE1.0 人类视图使用。不会创建边，也不会改变箭头。
- `\t>G1 1` 是当前合法领域头；`\t>1` 并不满足 v1.1 解析器的 ID + revision 格式，只能当作不完整速记。
- 只显示 X0-X2 是基础示例；X3+ 按需存放扩展属性，仍不得改变 Graph 连线方向。

## 3. 实际测试结果

| 测试类型 | 结果 | 说明 |
|---|---|---|
| v1.1 Python 参考解析器、压缩器 UT | 40/40 PASS | 原有语法和无损传输测试原样保留 |
| 网站/Graph 语义与链接一致性 | 8/8 PASS | 不依赖第三方 Python 库 |
| Chromium (Playwright) 离线网页验证 | PASS | 1440×960、768×1024、390×844；三语、三模式、Node/Edge、反向/无向箭头；3 个独立页面 |
| 运行时 JavaScript 异常 | 0 | 页面实际执行，点击交互后检查 |
| 水平溢出 | 0 | 上述三种尺寸 + 独立 Graph/Token/Codec 页面移动尺寸 |
| Token 基准复测 | **本轮未重新计算** | 旧 v1.1 数据保持不变，检查英文原生 3012、YAML 3849、wire 1953 BPE 与 21.75% 主页展示一致 |
| Windows IDE1.0 / IME1.0 真机集成 | **未执行** | 原型文档保留，不将网站验证冒充为产品集成验收 |

环境限制：Chromium 阻止通过 HTTP/file 协议直接导航到本机测试页面；因此本轮浏览器验收把相同的 HTML/CSS/JS/本地图片内联到 Chromium 的 about:blank 运行。**这验证了界面交互与响应式布局，但不等同于实际部署后的 HTTP 缓存、CDN、跨域策略或 Windows Edge 真机验收。** 静态链接可解析性另有检查。

## 4. 面向后续开发的文件入口

- `website/index.html`：主页，三模式互动展示与 Graph 速查
- `website/graph-guide.html`：新增 Graph 专页，中/日/英动态切换
- `website/token-benchmark.html`：原有专门 Token 实测页面
- `website/codec.html`：原有编解码器介绍页面
- `docs/GRAPH_FIELD_GUIDE_{zh,ja,en}.md`：三语文字规范
- `examples/website_samples.json`：主页语义原始数据
- `tests/test_website_consistency_r2.py`：原文、语义、内部链接、基准一致性
- `tests/test_browser_r2.py`：离线 Chromium 冒烟验收及截图生成

## 5. 仍需后续验证

- 目标线上浏览器下的真实资源加载、缓存策略和无障碍读屏检查；当前完成的是离线内联验证。
- 正式网站的 Graph 容量测试（数千个 Node/Edge 时应使用 Canvas/WebGL 或虚拟化，而不是当前演示 SVG）。
- GPT、Claude、Gemini 的官方 tokenizer 与实际任务端到端成本仍没有在本轮被测量。
