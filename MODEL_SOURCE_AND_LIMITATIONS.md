# .NEMA 高精度石雕方案与当前实现范围

- 真实模型选择：Smithsonian American Art Museum / Hiram Powers《The Greek Slave》扫描改造基底，CC0。
- 权限来源：https://www.innerscene.com/tools/library/3d-parts/the-greek-slave-model-5469a75d
- 采用 Three.js GLTFLoader；优先本地 `website/assets/ariadne-real.glb`，否则尝试公开远端文件。
- **本包未内置扫描 GLB**，无法宣称真实雕像已被离线打包；网络或跨域错误时会回退到程序化雕像。
- 模型为经典女性雕像，并非阿里阿德捏专属；模型目前未完成右手托球、衣褶重塑等建模改造。
- Node–Edge 对比修复：三格式源码 Tab + 关系 SVG + Token 柱状图同步。
- benchmark-data.js 内数字为旧版 neutral BPE 样本，不是新模型 API 实测；真实等价性、商用 tokenizer 不应过度外推。
