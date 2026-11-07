# NEMA v1.1 测试设计 UT / IT / ST / UAT

## UT 需求映射

- UT-NATIVE-001：What-first，缺少 Who 的单列纯文本。
- UT-NATIVE-002：英文 `HTTPItIs`→`HTTP it is`，`APIHTTP` 被标为需消歧。
- UT-NATIVE-003：日语助词、中文自然拼接、标点黏着、字面量 `\=APIKey`。
- UT-NATIVE-004：单空格 X 分隔、连续空格保留空列，`\ ` 字面空格。
- UT-MODE-005：默认 5W1H、Tab 表头 Table、Graph `>` 模式。
- UT-GRAPH-006：正向、反向、无向、平行边、自循环；孤立/重复 ID 拒绝。
- UT-WIRE-007：`TAB+$N`、`TAB+数字`、`^N` 与 `\^` 碰撞无损往返。
- UT-WIRE-008：前缀字典索引越界、无终止双空行、正文原始 Tab 拒绝。
- UT-WIRE-009：输入随机 `^`、反斜杠和数字，100 次 fuzz 稳定往返。

## IT

- IT-CODEC-001：Python 参考 Codec 与未来 Rust Codec 在 3 语言、多领域、Graph 完全一致。
- IT-EDITOR-002：IDE 仅手动点击执行转换，IME 同时启用时仅有一个写入者。
- IT-IME-003：输入法候选未提交不能被编码；提交后去抖触发、撤销恢复前状态。
- IT-DOC-004：`.nema` ↔ `.nemat` 完整字节一致，缓存采用内容 hash / revision 校验。

## ST / UAT（尚未在真实 IDE/IME 产品中执行）

- ST-001：1000 行 Table、10k Edge 网状图的内存、时延、取消、资源上限。
- ST-002：断连、崩溃、两个 Agent 并发写入、文件被修改时 CAS 冲突回滚。
- ST-003：secret 扫描、用户关闭 AI 后数据仍不外发、本地 token 计数。
- UAT-001：Windows 11 IME 组合输入、VS Code 桥接、IDE Web/Desktop 手动优先。
- UAT-002：视觉无横向溢出、三语页、选择 Graph Edge 后说明与箭头方向正确。

## 可执行证据

`python -m unittest discover -s tests -v` 测本参考实现；`python bench/reproduce.py` 复现实验并重写 `bench/results.json` / `results.csv`。**测试通过仅证明参考模型，不代表集成到真实 IDE1.0 或 IME1.0 产品。**

## Graph Hover（R3）前端验收

- UAT-GH-01：Node A 悬停显示 X2=`Authentication`，不选中其他 Node，不修改 .nema。
- UAT-GH-02：Edge X 悬停显示 `A → B` 和 `Verify session`；Edge Y 显示 `C → B`；Edge U 显示 `A — C`。
- UAT-GH-03：pointerleave / Escape 关闭；Tab focus 预览；Enter/Space 使详情面板持续可见。
- UAT-GH-04：手机轻触展示详情，Graph 指南页的弹层排在图下且可以再次轻触关闭。
- UAT-GH-05：三语 locale、390/768/1440 视口、无 JS 异常、无横向溢出、无 DOM XSS。
- UAT-GH-06：无 X2 显示可选占位，超长说明安全换行，Hover 不触发自动压缩或 Token 计数改变。

可执行脚本：`python tests/test_browser_r3_hover.py`（Chromium + Playwright，使用资源内联的离线页面）。此次网站验收不能替代真实 IDE / IME 集成验收。

## Website R4 附加验收矩阵

| ID | 分类 | 检查点 | 通过判定 |
|---|---|---|---|
| R4-U01 | UI/键盘 | 选择 SVG Edge 后 Graph 重新生成 | 焦点仍在同一 Edge ID |
| R4-U02 | UI/键盘 | 三模式 Tab 导航 | Right/Left/Home/End 更新模式、焦点与 aria-selected |
| R4-U03 | UI/i18n | Graph 指南切换 zh/ja/en | ARIA 名称与显示语言同步 |
| R4-G01 | Graph | A→B、B→A 平行关系 | 不同通道，箭头方向正确 |
| R4-G02 | Graph | 同一 Node 的两个自循环 | 两条可独立命中的不同路径 |
| R4-B01 | Benchmark | 官网 Token 数据 vs JSON | 所有 11 个场景及计数一致 |
| R4-B02 | Benchmark | 首页柱图 | 动态读取统一基准源，无硬编码数值 |
| R4-P01 | 包装 | HTML 引用、SHA256 与 ZIP | 引用存在，校验全通过 |
