# NEMA v1.5 Graph 箭头绘制与交互设计

## 真实方向与视觉分离

`edge.from`, `edge.to`, `edge.direction` 是解析器决定的结构语义；网页布局无权更改。`A<X<B` 的路径是 B→A，绝不可渲染成 A→B。无向关系 `A=X=B` 无箭头。Edge ID 永远不会被当作路径中的中间物理节点。

## SVG 生成规范

1. 先解析得到 Node ID + Edge ID + from/to/direction；若端点未声明应报错。
2. 确定性节点布局：目前 1 节点居中、2 节点左右、3+ 环形布局。它只是演示布局，后续 IDE 可替换为 ELK/Dagre/力导向；不能改变方向。
3. 按**无序节点对**分组以识别同节点对之间的反向边和平行边，并分配不同偏移量（lane）。反向边和正向边需要两条可辨识的曲线。
4. 以二次 Bézier `M start Q control end` 绘制边。起止点通过沿控制点方向的射线求节点矩形边框交点，箭头尖端落在目标节点边框而非中心；SVG marker-end 只施加到 `direction='directed'` 的边。
5. 自循环用三次 Bézier 从节点顶边的一侧绕回顶边另一侧，marker-end 在自身边界。遇到多重自环改变曲率与高度；屏幕边界需要预留空间。
6. 每条边保留可键盘聚焦、点击和选择的 SVG path，Edge 的 ID/名称浮标可点击；下方详细信息面板显示 from、to、关系名称和纵向内容。
7. 同一组节点连线可以拥挤，但**不得合并 Edge 记录或隐藏某个 Edge 的语义**。全量边可通过清单选择查看。

## 测试验收

`tests/graph_renderer.test.js` 验证 `B<Z<C` 的终点落在 B 边界，所有有向边起止点均处于声明 Node 的边界，反向边/平行边采用不同路径，无向边不要求箭头，自循环可绘制。

`tests/browser_smoke.py` 验证静态站实际渲染的 SVG：带 `marker-end` 的 path 数与有向 Edge 数一致；选择 Edge 后详情显示方向；中日英切换及 Token 专页可加载。浏览器验证需要本地安装 Playwright 和 Chromium，参考核心解析器不依赖浏览器。

这套渲染以 `website/graph.js` 独立模块提供，IDE1.0 应复用其算法约束（不要求把 TS 实现直接移入 Rust 内核）。
