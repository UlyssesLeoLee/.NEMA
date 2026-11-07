# NEMA Graph 字段与箭头语义指南

**Graph 是 NEMA 三模式之一。X0 定义 Node 或 Edge 身份，X1 是名称，X2 是职责或行为说明。**

```text
	>G1 1
A \=LoginAPI Authentication
B \=TokenStore SessionStorage
A>X>B Reads VerifySession
  CacheExpiredRetryOnce


```

| Column | Node | Edge |
|---|---|---|
| X0 | `A`: Node ID | `A>X>B`: A → B, Edge ID X |
| X1 | `\=LoginAPI`: exact name | `Reads`: relation name |
| X2 | `Authentication`: optional note | `VerifySession`: optional note |
| X3+ | optional attributes | optional attributes |

Authentication 只是说明，不等于 Edge，也不会自动连接到某个认证服务。

线的方向由 X0 唯一决定；X1、X2 和纵向续写只是这条 Edge 的内容，不会修改源节点和目标节点。

注意：A LoginAPI Authentication 也是合法的三列原文；但 PascalCase 语义渲染可能把 X1 展示成 “Login API”。需要保持精确标识符 LoginAPI 时，请写 \=LoginAPI。

| NEMA | Rendering |
|---|---|
| `A>X>B` | A → B |
| `A<Y<B` | B → A |
| `A=U=B` | A — B |
| `A>P>A` | A ↻ A |
| `A>X>B` + `A>Y>B` | A ⇉ B |
| `A>X>B` + `B>Y>A` | A ⇄ B |

正式 Graph 领域头是 ⇥>G1 1（ID 加版本）。单独的 ⇥>1 仅为不完整速记，不符合当前 v1.1 解析器语法。

NEMA v1.1 — website review R3 (2026-11-07).


## 悬停预览与点击详情（网站 R3）

在 Graph 的 SVG 人类渲染视图中，鼠标移入 Node，立即显示 **Node ID、名称（X1）、说明（X2）**；鼠标移入 Edge 的线段或标签，显示 **Edge ID、名称（X1）、解析后的实际方向、说明（X2）**。说明可以来自 X2 的纵向续写，预览使用解析器合并后的完整语义结果。

例如：`A \=LoginAPI Authentication` → 悬停 A 显示 `Authentication`；`A>X>B Reads VerifySession`（后续 X2 可以纵向追加）→ 悬停 X 显示 `A → B` 和 `Verify session`。**X2 缺省时显示“未填写 X2（可省略）”，不自动杜撰内容。**

悬停预览是只读交互，不改变 Node / Edge、修订、数据、方向或 Token。鼠标移出隐藏；Tab 聚焦时同样显示，Escape 隐藏；Enter / Space 或鼠标单击打开固定字段检查器；触屏使用点击查看检查器。悬停卡片不应该抢占鼠标事件（`pointer-events: none`），避免遮挡节点和造成闪烁。复杂图的边必须保持单独的命中区域（允许视觉连线与透明宽命中线分离）。

反向边 `B<Y<C` 的实际方向是 `C → B`；无向边 `A=U=C` 显示 `A — C`，不画箭头；自循环 `A>P>A` 保持自循环。悬停无权修改这些关系。`\=LoginAPI` 的标识符原样显示。移动版 Graph 说明页轻触节点/关系时在图下方固定展示说明，避免小屏覆盖其他图元素。

网站交互示例见 `website/index.html` 的 Graph 模式及 `website/graph-guide.html`。实现细节和验收标准见 `docs/GRAPH_HOVER_RENDERER_DESIGN.md`。
