# NEMA v1.4 · UT / IT / ST / UAT 测试设计

| 编号 | 层级 | 输入 | 预期结果 |
|---|---|---|---|
| UT-01 | UT | `\tT1 1` 下一行 `Claude Ready` | Table，无显式表头，columns=column1,column2 |
| UT-02 | UT | `\\ Agent Status` 首行 | 显式表头，第一行不当数据 |
| UT-03 | UT | Table 首行 `\\^0` | 不会错认表头；按原文字典规则解释 |
| UT-04 | UT | 行首 3 空格续写 | X2 原意群继续，当前表格行数量不变 |
| UT-05 | UT | 新的一行顶格 | 新记录 |
| UT-06 | UT | `?`、` .` | What/Why/How 坐标与尾空字段准确 |
| UT-07 | UT | Graph `A>X>B`,`B<Y<C`,`A=Z=C` | 分别 A→B、C→B、A—C |
| UT-08 | UT | `\t$1` + `APIKey` + `Validate^0BeforeAccess` | 字典原子不拆分 |
| UT-09 | UT | `\\^`、`\\.`、`\\\\` | 字面逃逸精确 |
| UT-10 | UT | 4 / 16 / 32 连续重复字符 | RLE 有收益才压缩，输出 UTF-8 完全一致 |
| IT-01 | IT | IDE/IME 共享内核 | 相同输入编码一致；不会重复压缩 |
| IT-02 | IT | `.nemat` 解码后重解析 | UTF-8 + AST 双重一致 |
| IT-03 | IT | 1,000 行表 / 600 条边 | 速度、空间和方向在限定范围内 |
| IT-04 | IT | 字典越界、超大 RLE、非法头 | 安全拒绝、原文不修改 |
| ST-01 | ST | IME composition commit → 自动编码 | 输出准确；用户能撤销 |
| ST-02 | ST | IDE 手动点击转换 | 临时租约成功、IME 不重复写入 |
| ST-03 | ST | 断电、同域并行编辑、旧 generation | CAS 校验失败时无数据丢失 |
| UAT-01 | UAT | 中文日文连续意群、英文 HTTPItIs | 正确显示不混淆标识符 |
| UAT-02 | UAT | 三语官网 Token 专页 | 数值读取本地基准，不手填；离线可显示 |
| UAT-03 | UAT | 用户源代码编辑 | NEMA 插件不得自动修改 .rs/.ts/.py 本文 |

**当前已自动执行的范围**：包内 Python 原生解析器、可逆编码器、训练语料静态校验、字节往返与本地 Token 计算。Windows TSF、实际 Tauri / VS Code 宿主 UAT、真实模型生成误码率尚未执行，不应标记为 PASS。
