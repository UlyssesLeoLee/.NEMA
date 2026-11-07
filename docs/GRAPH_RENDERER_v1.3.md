# .NEMA Graph Node / Edge 交互渲染设计

## 数据合同

字段 X0 = Node ID（前置一个 ASCII 空格）或 Edge 表达式（顶格）。X1 = 名称（Graph 内默认精确保留大小写）；X2 = 可选语义说明。X3+ 扩展属性不改变关系方向。Node ID 与 Edge ID 必须唯一；跨图引用须明确 scope。

## 悬停/焦点/触屏

指向 Node 的矩形/标签时展示 Node 的 `name + X2`；指向 Edge 的线段/箭头/标签时展示 `edge name + source→target + X2`。方向由 Edge X0 决定，绝不根据曲线走向重判。X2 缺省时显示“无说明”，绝不编造。Hover 为只读，Click/Enter 固定检查器，Escape 关闭。Touch 单击固定信息，不要求 hover。Focus 环明确对比，保留焦点对象身份，即使图重绘。Tooltip 关联 `aria-describedby`，避免在屏幕阅读器输出中重复所有文字。

## 拥挤图和 3D

平行同向边用不同曲率，反向边不重叠，自环具稳定半径。复杂图应支持层级聚合/子图焦点、布局切换和边过滤，但这些只作用于 UI，不写入 `.nema`。Three.js 只作为独立装饰性视觉层，不处理决定性图数据，离线/禁动画时静态图照常工作。Graph UI 仍使用 DOM/SVG 可访问节点和边。

## 安全和性能

只使用 `textContent` 注入来自 X1/X2 的内容，禁止 `innerHTML`；文本截断仅显示层生效。节流 PointerMove，Tooltip 不捕获事件，悬停离开及时关闭。数千节点时虚拟化绘图，谨防 Edge 命中区域过窄。不要将 Node 的 X2 渲染为额外 Node。

## R7：扩展属性不应消失

X0 决定身份与箭头，X1 保留名称，X2 悬停说明。X3+ 存储在 `extensions` 对象，点击固定检查器应继续展示相应 X 坐标和精确文本；悬停仍只显示 X2，避免认知负荷增加。输入的标识符大小写、数字、下划线不因 PascalCase 规则改变。
