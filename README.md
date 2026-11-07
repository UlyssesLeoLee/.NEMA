# NEMA · Ariadne’s Thread — Website R5 / Comic 3D→2D

基于 NEMA v1.1 Website R4 完整功能的网站美术改版：保持原有希腊神话主题、三种数据模式、What-first 语法、Graph 悬停与点击检查器、三语及 Token 基准数据，不修改 Codec 或训练结果。

## 使用

打开 `index.html`（跳转到 `website/index.html`）；或直接打开 `website/index.html`。网站静态资源已在本地，浏览时不要求网络。

## 页面

- `website/index.html`：中日英主页、交互 5W1H/Table/Graph、Node/Edge 悬停、Token 对照。
- `website/graph-guide.html`：Graph X0/X1/X2、方向、悬停/聚焦/触屏说明。
- `website/token-benchmark.html`：11 场景 Token 测量与真实样本（参考数据来自 R4）。
- `website/codec.html`：字典、前缀和传输说明。
- `website/review.html`：R4 五轮审查内容归档。
- `website/comic.css`：R5 视觉设计实现（可作为后续主题皮肤继续修改）。

## 视觉改动

美漫 3D-to-2D：墨色粗轮廓、石雕版画质感、网点半色调、斜切标签、金色线程、古希腊迷宫背景、漫画纸米色卡片、可视化 SVG 关系图。所有按钮、标签页和图的悬停行为均仍为真实 DOM 交互，图片仅作艺术装饰。

## 注意

这是网站 R5 美术版；保留 v1.1 协议与基准原始数据，并未重新运行商业模型 Token 计费实测。IDE1.0 / IME1.0 产品集成仍独立于本网站。
