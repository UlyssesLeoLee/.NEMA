# 从 v1.3 到 v1.4 的迁移

**破坏性变化**：默认 Table 的第一行已不再无条件是表头。凡是属于表头的旧记录，必须在该行前增加 `\\ `；如果只是数据，保持顶格写法即可。

旧版：

```text
⇥T1 1
Agent Status Note
Claude Ready CheckSession
```

新版：

```text
⇥T1 1
\ Agent Status Note
Claude Ready CheckSession
```

检查遗留目录中的旧训练 JSONL、网站演示、解析器单测和扩展语法高亮，禁止混用。迁移器不能凭“第一行都是英文”自动认定它是表头；应使用旧版 schema、文件元数据或用户确认。没有 Schema 的旧文件默认保守、保留原始字节并发出需要确认的报告。

v1.4 标记：Table 默认，`?` 为 5W1H，`>` 为 Graph；What-Why-How-Who-When-Where；正文空格分列；字典 `Tab+$N`；`.nemat` 独立媒体类型；前缀 `Tab+数字` 只在传输模式；输入法优先自动转换。
