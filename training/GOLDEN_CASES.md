# .NEMA v1.2 · Golden cases

合法：What-first，英文 HTTPItIs，中文横向连写，日语横向连写，Graph 节点行首1空格、Edge 顶格、X2 续写2空格、逆向箭头。

非法：Graph Node 行首0/2空格、悬空引用、箭头混用、重复 ID、空表、CRLF、缺 EOF、未知转义。

所有正例都使用 `codec.native.parse()` 验证，非法例均必须显式拒绝。


## R7 · Graph X3+ 语义回归

正例请运行 `examples/graph_x3_extensions.nema`：Node A 的 `extensions.X3` 必须是 `APIKey`；Edge E 的 `extensions.X3` 必须是 `HTTP401 RetryOnTimeout`。Edge 的起点 A、终点 B、X2 `Verify session` 不可变化。完整训练/评测向量见 `training/R7_GRAPH_EXTENSION_GOLDEN.jsonl`；不得把这些测试向量混入旧版保留评测集。
