# .NEMA Ariadne V90 — 先以 2D 循环复原正脸和表情，再转动头部

**单一完整 YAML：** `NEMA_Ariadne_V90_Face2D_Loop_HeadAngle_Single_FULL_Master.yaml`

这次在经过工程 A/B 审核的 V89 基线上只新增必要的面部顺序，仍保留人体姿态、金球、连续金线、24 角精修及严格艺术验收。**不重做服装或发型。**

## 流程

1. P00：锁定真实 GLB、原始 V20 2D、24 角参考的来源及拓扑。
2. F00：确认 V20 正面图的相机/头部视角偏差，标注独立二维面部语义点（并非认定原画天然是精确正面相机）。
3. F01：同机位正脸 **2D 反馈循环**，从眼距、鼻梁、鼻尖、颧骨、下颌、面部比例校准身份特征；实际 Blender 渲染→误差→受限形态编辑→再渲染，失败回滚。
4. F02：正脸锁定后，再独立修复眼睑、眉弓、嘴角、唇线与自然微表情；冻结 F01 已锁定的身份形态。
5. P01：全身 K 字姿态与正确掌心，仍保持头部面容已锁定。
6. F03：只用**真实颈部/头部骨骼**应用来自 24 角原画的统一旋转，发饰和附属物必须同步；检测面部三维不被拉伸。
7. F04：24 个固定相机视角审查同一头部角度，不允许按每个角度修改头部来作弊。
8. P02—P05：保留 V89 的掌心金球、单根三维金线、多角精修及 GLB 往返验收。

## 真实输入现状

- 历史原画 `V20_Original_Front_Art_Reference.png` 已恢复并计算 SHA256；`assets/V20_original_head_reference_crop.png` 是从原画裁出的辅助证据，不是新生成的人脸，也不是已批准的几何正面图。
- 实际 V87.1 GLB 已确认无皮肤骨架 `skin=0`，且 `morph targets=0`。当前不能直接自动做可信的面部雕塑和颈骨旋转。
- 正面眼鼻口语义点与独立 3D 顶点绑定、已批准的相机配准、面部 morph、可验证颈骨尚未提供。因此实物质量验收仍 `BLOCKED`。

## 可运行代码

- `src/face_2d_loop.py`：有可验证 3D morph basis/2D 语义点时可运行的数值循环内核（不生成虚假的 3D 人脸）。
- `src/ab_synthetic.py`：**合成模型**上 A（边转头边拟合）对比 B（正面拟合后转头）的算法实验，只验证优化顺序及 3D 刚体距离保持；不是 V20 真实艺术质量得分。
- `src/blender_face_head.py`：Blender 4.5 Python，`face_lock` 实际包含 F01/F02 两轮、`head_turn` 的骨骼变换及面部刚性约束；若素材未批准，严格失败。
- `src/preflight.py`：基于**真实历史 GLB**读取 glTF JSON 检查 rig / morph 数量和输入可用性。
- `tests/test_face_2d_loop.py`：15 项 Python 测试。

示例执行：

```sh
python -m pip install numpy PyYAML pytest
python src/ab_synthetic.py
python src/preflight.py
python -m pytest -q tests/test_face_2d_loop.py
# 在人工校准并批准 2D、获得真正面部 morph/颈骨后的 Blender 阶段：
blender -b approved_canonical_face_and_rig.blend --python src/blender_face_head.py -- face_lock
blender -b output/face_canonical_locked.blend --python src/blender_face_head.py -- head_turn
```

不得把测试通过、裁剪原画或者空的审批模板当作真正的面部复原。要完成雕像，必须提供符合原画的 3D 脸部可编辑基准、相机及五官标注、骨骼绑定并完成真实逐角渲染验收。
