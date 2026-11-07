# NEMA v1.1 Website R5 — 美漫三渲二 UI 设计规范

状态：美术与前端主题改版；NEMA 语言协议、基准数据、训练文本保持 v1.1 R4。

## 视觉系统

- 叙事：阿里阿德涅手持金色线团，古希腊迷宫、宫殿廊柱、石雕守护者和线轨贯穿页面。
- 美漫三渲二：漫画粗墨轮廓、版画石材质感、深蓝黑阴影、金色硬高光、稀疏网点半色调。
- UI：斜切式金色标题签、斜切按钮、两像素高对比边框、分层深蓝卡、米色漫画纸语法卡。
- 组件视觉规则写在 `website/comic.css`；原有 `website/styles.css`、`app.js`、Graph 渲染与数据源保留。
- 可点控件是 HTML button / anchor，SVG Graph 仍为真实可聚焦对象；插图不含伪按钮或网站截图。

## 功能不变量

1. 三种模式仍为 What-first 5W1H、Table、Graph，空格横向定位，必要时纵向意群。
2. Node `A \=LoginAPI Authentication`：X0 是身份，X1 是名称，X2 是可选的职责说明。
3. Edge `A>X>B Reads VerifySession`：X0 确定 A→B 和 Edge ID X，X1 是关系名，X2 是行为说明；显示说明不能改变方向。
4. 悬停或聚焦直接展示 X2，点击展示完整检查器；手机使用点击。
5. 中、日、英三种界面，全部静态页面保留。
6. Token 页面展示既有本地 SentencePiece 实测，不得将示例数值当作官方模型账单。
7. 编解码器与训练资料仅作为文档及下载资源，不被视觉改版改写。

## 五个页面

`index.html`、`graph-guide.html`、`token-benchmark.html`、`codec.html`、`review.html`。

## 验收方法与限制

在本环境内对 Chromium 使用离线 DOM/CSS/JS 注入，验证三语言、Table/Graph 切换、Node/Edge 悬停、Graph 指南、桌面/平板/手机宽度和 JavaScript 错误。因为浏览器策略阻止访问本地 HTTP 地址，尚未运行正常 HTTP 服务下的 E2E 访问；需在正式部署环境复测导航链接、字体网络加载和目标浏览器兼容性。

## 素材与授权

阿里阿德涅与迷宫漫画装饰由本项目生成的视觉稿裁切，不含第三方版权媒体的复用。品牌 SVG 沿用 R4；依赖与字体说明见 `licenses/ASSET_NOTICES.md`。
