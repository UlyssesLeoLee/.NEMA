# .NEMA · Ariadne 3D Sculpture Website

## 开始使用（Windows）

解压整个 ZIP。双击 `START_WINDOWS.cmd`，或在解压目录执行 `python start_local.py`。浏览器将打开 `http://127.0.0.1:8764/website/index.html（如端口被占用，自动选用 8765–8779）`。

**不要直接使用 `file:///` 打开网页**：浏览器可能拒绝读取 GLB，导致模型不显示。

首页默认每 24 秒完成一次 360° 旋转，支持暂停、恢复、手动选择正面/左右侧面、手动拖动、两秒复位停留后恢复自动旋转以及 PNG 截图。首页还包含一个真实打包的 `.glb` 三维网格，语法总表、可执行解析器、Node–Edge 关系演示和 JSON/YAML 同语义对比。离线时会用独立 WebGL2 绘制**同一个 GLB 网格**，不会出现过去的简笔 SVG 假雕像；联网时自动切换为 Three.js + GLTFLoader。

如果你需要在**彻底离线的机器上仍以 Three.js 而不是 WebGL2 渲染**，在有网络的机器上运行 `npm install && npm run bundle:offline`（会把 Three.js 0.171.0 的源码及 addons 复制到网站中），然后重新打包整个目录。未安装依赖并不影响 WebGL2 离线显示。

## 重要的模型真实性说明

本包中的 `website/assets/ariadne-relief-3d.glb` 是**真实存在的三维网格模型**，包含 3D 深度浮雕、推定背面、大理石轮廓、独立金色球体、17 组真实缠绕线及 3D 引导线。正面石雕图像取自本轮确定的艺术参考，并用像素深度场建立精细立体表面；浏览器可拖动产生真正的视差和光照变化。

**它不是三维扫描或人工逐面雕刻的完整 360° 女性人体圆雕。** 侧背面的形状为推定的浮雕厚度，不能等同于参考图所暗示的博物馆级独立圆雕；不会声称已经复刻了全部身体解剖、背部衣褶、手指和真实扫描几何。此问题受限于当前环境不能下载额外授权扫描模型，也无法进行高精度人物建模。正面观感接近参考图，侧背面不作同等精度承诺。

这是和之前占位人物本质不同的、可以独立打开的 GLB 网格，但**不是用户最终要求的商品级完整雕塑**。为了达到最终标准，需要获得可下载的完整高精度、版权清晰的女性雕像网格，并对举手和金线团进行正规重拓扑 / 雕刻改模。

## 页面入口

- `website/index.html`：3D 阿里阿德捏首页、默认显眼的 Node–Edge 动画 + JSON/YAML Token 对照。
- `website/grammar.html`：Table、5W1H、Node–Edge 三标签主语法列表，含七列与 139 项变化；共通转义、字典压缩可展开查看。
- `website/playground.html`：编辑器、解释器 AST、结构化表格、由 AST 实时驱动的 Node–Edge 图与五种关系演示。
- `website/downloads.html`：解释器、AI 训练文档、规范、原始基准、3D GLB 文件。

## 动画及交互

- Three.js 环境：支持鼠标旋转、缩放、拖动，`GLTFLoader` 加载实际 `.glb`，toon 石材后背材质、独立金线球体及流动光粒子。
- 离线 WebGL2 环境：从打包的 GLB 读取真实 3D 网格，使用同样的纹理和投影渲染，支持鼠标拖动和视角按钮。
- 首页依据解释器 AST 动态渲染 Table 表格、5W1H 六维和 Node–Edge 关系图；语法效果页五种关系均由同一个 AST 图形模块生成，并支持点击节点和边查看含义；同步格式切换及 Token 柱图。
- 系统减少动画或页面暂停时停止主要动画。

## 数据与对比限制

JSON/YAML/ .NEMA Token 数字继承旧工程的 **local neutral BPE（vocab 1800）** 测试数据，不代表商业模型 API 真实计费，也不保证在所有结构上都更短。原始样本、脚本和计数保留在 `bench/`。

三种对照格式应满足等价语义；网站保留原始模型自测值，不擅自篡改数据。若要正式对外发布性能优势，仍需运行目标 GPT/Claude/Gemini tokenizer 测试并核查每个案例的语义等价性。

## 目录

- `website/assets/ariadne-relief-3d.glb`：可直接复用的 GLB 3D 网格。
- `website/assets/ariadne-hero-texture.png`：前表面艺术纹理。
- `website/js/sculpture-three.js`：Three.js 渲染器。
- `website/js/sculpture-native.js`：离线 WebGL2 渲染器。
- `models/ariadne-model-manifest.json`：实际模型属性与限制。
- `models/render_mesh_preview.py`、`previews/`：从同一真实 GLB 生成的 CPU 网格投影图（**不是浏览器截图**）。
- `interpreter/`、`codec/`、`tests/`、`bench/`：解释器、压缩、测试及 Token 数据。

源码并非已上线的商用服务；仍需要独立进行目标浏览器上的 WebGL、移动端和性能验收。

## 本轮交互回归测试

不需要 npm 依赖即可执行：

```powershell
node tests/test_interaction_contract.mjs
node tests/test_controls.mjs
node tests/test_semantic_panels.mjs
python tests/test_matrix.py
```

完整 3D 绘制需要 WebGL2；网络允许时优先采用 Three.js + GLTFLoader，加载失败时使用包内独立的 WebGL2 渲染器读取**同一 GLB 文件**。两个渲染器共用 `website/js/sculpture-motion.js`，不会再出现“在线有动画、离线静止”的控制分歧。

**注意：** 本环境 Chromium 导航被管理策略阻断，不能宣称通过真实浏览器截屏、视觉排版或 GPU 性能实测；自动测试覆盖的是可执行的 JS 状态机、DOM 事件模拟、AST 渲染逻辑、链接与文件检查。最终设备上的美术/性能效果仍需通过 Windows 浏览器实机核对。
