# IDE1.0 × NEMA v1.5 · UT / IT / ST

| ID | 层级 | 条件 | 预期 |
|---|---|---|---|
| IDE-UT-01 | UT | `.nema` 无表头打开 | 自动 column1...，第一行不丢失 |
| IDE-UT-02 | UT | 首行 `\\ Agent State` | 显示显式表头且不作为记录 |
| IDE-UT-03 | UT | `HTTPItIs` / `^0` / 中日文直接连接 | 视觉渲染与原语义一致 |
| IDE-UT-04 | UT | Graph `B<Z<C` | C→B 箭头 |
| IDE-IT-01 | IT | 用户确认 APIKey 原子 | 创建/复用字典，撤销无损 |
| IDE-IT-02 | IT | IDE 启动，IME 已安装 | IDE 不主动写入文件 |
| IDE-IT-03 | IT | 点击转换同时 IME 提交 | 只提交一个 generation |
| IDE-ST-01 | ST | 500KB / 16MiB 文件 | 有上限、不冻结、不修改非 NEMA |
| IDE-ST-02 | ST | codec 返回无收益 | 显示原生格式，非强制 `.nemat` |
| IDE-ST-03 | ST | 进程崩溃、并发修改 | CAS 拒绝并保留原始文件 |

上述为**待在 IDE1.0 实际产品执行的验收用例**，不应混用包内 Python 测试通过数。
