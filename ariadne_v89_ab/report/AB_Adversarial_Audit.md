# NEMA Ariadne V89.0 — V88 A/B 实测与对抗审计

## A/B 实验性质（重要）

**这是基于真实 V87.1 GLB 的工程可行性和 YAML 验收逻辑 A/B，尚不是两个经过 Blender 修姿态和 24 角渲染后的雕像艺术品质 A/B。**

A 为 V88.0 原始 YAML 和原始 Blender 脚本，B 为新增 V89.0 优化 YAML。A/B 使用同一个不可变 GLB、同一组历史 24 张独立艺术参考和同一检查代码。B 的近接触球坐标是针对原网格搜索得到的工程候选，不能证明掌心正确托球；不存在新的最终 GLB。

## 真实输入证据

| 证据 | 实测值 |
|---|---|
| V87.1 GLB SHA256 | `4e9eb8ca64891ed63aae2a7a32297bf60f9b757f9c1873a7d67480827d11c948` |
| GLB 大小 | 1,316,876 bytes |
| GLB 网格数量 | 6 |
| MakeHuman 人体顶点 | 19,158 |
| MakeHuman 人体三角面 | 36,972 |
| glTF skins | **0** |
| glTF animations | 0 |
| 源文件坐标 | glTF Y-up；测试统一变换至 Blender Z-up |
| 历史艺术帧（每隔15°） | 24/24 文件齐全，24 个独立 SHA |
| 与原始 SHA256 清单对比 | 24/24 PASS |
| baseline YAML SHA256 | `34db0ddeac25849ad7654c2e2de86d45d0b48f1c9c693f8f419c15cba41a47f4` |
| baseline script SHA256 | `e61a1e469d6954d04ba7b56ab2f0066afc9f5e85dd63bcede1ac2eed0fee5549` |

**独立性说明：** 24 张图来自历史已存档艺术帧，图像有效性通过哈希一致性验证，不代表本次完成了相机配准、作者批准或与 V89 GLB 逐角审美比较。

## 十项 A/B 对照结果

| Case | 对照项 | A V88 | B V89 | 真实状态 |
|---|---|---|---|---|
| AB01 | GLB / pose 入口 | `NO_SKIN` | `NO_SKIN -> RIG_BIND_REQUIRED` | `PASS_ENGINEERING` |
| AB02 | 金球到手部候选区几何间距 | `0.365881` | `0.003978` | `PASS_PROXY_ONLY` |
| AB03 | 金线导出选择策略 | `MESH_ONLY_SELECT` | `CURVE_TO_MESH_AND_ROUNDTRIP_REQUIRED` | `PASS_CODE_AUDIT` |
| AB04 | 独立原画溯源 | `24_LABELS_NO_HASH_ASSERT` | `24_ANCHORS_SHA256_VERIFIED` | `PASS_ASSET_INTEGRITY` |
| AB05 | 24角审查有效性 | `24_PENDINGS_NO_LOSS` | `24_STRICT_PER_VIEW_LOSS_REQUIRED` | `PASS_POLICY_NOT_VISUAL` |
| AB06 | 金球坐标策略 | `FIXED_3D_COORDINATES` | `GEOMETRY_DERIVED_AFTER_POSE` | `PASS_POLICY` |
| AB07 | 两套真实姿态 GLB | `NOT_RUN` | `NOT_RUN` | `BLOCKED_NOT_EXECUTED` |
| AB08 | 全部24角 >95% | `NOT_MEASURED` | `NOT_MEASURED` | `BLOCKED_ART_QA` |
| AB09 | 掌心指腹与腕关节证明 | `NOT_MEASURED` | `NOT_MEASURED` | `BLOCKED_ANATOMY` |
| AB10 | 严格冻结服装头发范围 | `UNSPECIFIED` | `NO_SCOPE_EXPANSION` | `PASS_POLICY` |

本轮工程案例：**7 项 PASS（包含规则、资产、代码审计或空间候选试验），3 项 BLOCKED**。`BLOCKED` 不能计为通过。

## 金球真实几何 A/B

- A 固定球心（Blender Z-up 米）：`[0.58, -0.02, 1.58]`。
- A 到候选右侧手部顶点的球面间隔：**365.9 mm**。
- B 在同一网格上得到候选球心：`[0.603201, -0.103232, 1.028269]`。
- B 到候选区域球面间隔：**4.0 mm**。
- B 到全部人体顶点的球面间隔（顶点近似）：**4.0 mm**。

这一结果只能支持：**不用旧的固定空间坐标，根据当前网格搜索球的初始位置更合理**。目前并不能支持：

- 手掌朝上且能承担球的力学接触；
- 五指贴合、腕关节符合人体解剖；
- 三维球体和网格所有三角面无碰撞；
- 姿态符合原画 K 构图；
- 0° / 45° / 90° 视角已经正确托球。

B 的球候选值不准作为最终艺术坐标写死；一旦姿态改变，必须重新求解。

## 为什么选择 V89 YAML

1. 当前 GLB `skins=0`，A 版 `pose()` 在没有骨架时必然失败。B 明确新增 `P00`：识别模型能力，缺少有效 rig 就进入受控骨架/语义形变绑定，验证通过之前拒绝宣称姿态完成。
2. A 版把球放在固定坐标，B 版从**修好姿态之后**的手掌和指腹出发拟合，而非只靠右侧胳膊最近顶点。
3. A 版创建 Blender CURVE 金线，但 `export_glb()` 只选择 MESH；B 明确要求先将金线转换为真实网格，再做 GLB 重导入的数量与几何审计。
4. A 版多角度 `refine()` 只记录 `PENDING_VISUAL_REVIEW` 而没有执行匹配；B 版要求使用真实 V20 独立 24 角艺术参考，先标定相机，再逐角对比、回滚局部退化。
5. B 保留初版范围限制：**只修姿态、金球金线、多角度；不重做服饰和头发。**

## 对抗式负向验收

- 篡改任意原画文件：SHA256 失配必须失败。
- GLB 未提供 armature：姿态编辑步骤必须阻断而不是假装成功。
- 用近胳膊表面来代替掌心接触：不得通过解剖门槛。
- 只选择 MESH 导出曲线：不得通过金线 roundtrip 门槛。
- 任一 15° 角度未通过 `IoU > 0.95`：不能用其他角度的高分平均抵消。
- 把 24 个待审核状态写成分数：直接拒绝。
- 相机仍为临时参数、256 landmarks 仍未标注：艺术验收阻断。
- 仅完成静态 YAML 测试而没有新 GLB：不得输出 `ART_APPROVED`。

## 实验局限和后续真实 A/B

**当前并未产生 V89 新 GLB 或 V89 24 角实际 Blender 渲染，因此艺术品质胜负是 `UNDETERMINED`。** 为完成正式视觉 A/B：

1. 先对 V87.1 真实人体装配经证据验证的骨骼/语义形变，再修成接近原画的 K 姿态，输出实际 `pose_refined.blend`。
2. 在同一固定场景和相机下运行 A(旧固定球心) / B(姿态后掌心约束球心)；均渲染24角并留下独立图像。
3. 固定其他变量，比较金线 A(固定路径) / B(艺术多视角绑定+空间避障)，确保 GLB 重导入。
4. 每次只修改一个变量，保持随机种子、姿态和相机条件一致；任何一个视角退化必须回滚。
5. 全部 24 角经独立原画相机配准后逐角 **严格超过95%**，还要通过内线条/五指/头部/主衣褶/金线等艺术审核才能最终交付。

**建议：采用 V89 作为下一轮正式制作执行 YAML，不能把 B 判定为已经超过 A 的艺术品质模型。**
