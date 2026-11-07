# NEMA Website R3 — Graph Hover UX 审查与验收结论

**基线**：NEMA v1.1 网站 R2，协议语法与 Token 报告版本不变。**更新范围**：Graph 人类渲染交互、三语说明和配套实现文档。

## 已修复的问题

1. 旧版 Graph 只能点击选中 Node / Edge 后读取 X2：增加指针悬停即时显示 X2。
2. 旧版 Edge 信息不便快速读取：Tooltip 直接显示 Edge ID、X1、**解析后的方向**和 X2；Node 显示 ID、X1、X2。
3. 旧版缺少键盘/触屏等价交互：Tab 焦点和鼠标悬停展示同内容；Escape 隐藏；Enter/Space/单击打开完整详情；触屏点击选择。
4. Graph 指南原先仅静态示意且已露出 X2：改为交互 Node/Edge，说明由悬停与轻触展示；手机端固定卡片置于图下方。
5. 对缺失说明的约定不明确：以可选占位显示，无 AI 猜测、无额外边与 Token 开销。

## 实现要点

- 悬停事件始终只读，绝不改变领域版本、源文件、字典状态、选中状态或箭头方向。
- SVG Node/Edge 保留不同的 hit target；`pointer-events:none` Tooltip，避免鼠标移过时闪烁。
- Edge 的方向由 X0 确定：`B<Y<C` -> `C → B`；`A=U=C` -> `A — C`。
- 所有展示文本使用 `textContent`，前端不会向 DOM 插入未经信任的 HTML。
- 三种语言页面共用同一套数据，且生成的 Graph demo 由 Python 参考解析器校验。
- Token 基准结果、原生 NEMA 和 `.nemat` 的语法、训练语料 JSONL 均未更改。

## 执行与限制

- Python unittest：54/54 项通过，包括 Codec/Graph、文档链接、三语交互文本、基准值保护。
- Chromium 旧版回归：R2 3 个视口、3 种模式、3 语言、4 条 Edge 均通过。
- Chromium R3 增量：33 项检查通过（1440 / 768 / 390 视口、Graph Node/Edge Hover、键盘、逆向/无向箭头、三语、触屏说明、无横向溢出、无 JS 异常）。
- 浏览器采用资源内联的离线页面进行验收；并非部署环境 HTTP/CDN、Safari/Firefox 或 IDE1.0/IME1.0 真正集成的证明。
- 未来复杂拓扑图须单独验证 10k Edge 时的鼠标事件性能、视图裁切及无 X2 极端情况。

此 R3 只交付可运行网站与文档设计，不声称已把 Hover 集成到 Rust IDE1.0 / Windows IME1.0 仓库。
