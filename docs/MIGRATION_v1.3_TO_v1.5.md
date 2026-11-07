# 从 v1.3 升级到 v1.5

使用 `python -m tools.migrate_v13_to_v15 input.nema output.nema`；工具先解析 v1.3，识别旧模式，再创建半角空格领域头并比较语义。旧版 Tab 领域头必须迁移。旧版无模式表格首行若无 Tab，则会被认为是 5W1H；不自动猜测历史歧义。
