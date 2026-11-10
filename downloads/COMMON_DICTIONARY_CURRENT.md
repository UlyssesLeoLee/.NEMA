# 共通字典与 .nemat 可逆压缩 · 统一审查候选规范

只有 **ASCII 半角空格 U+0020** 担任语法空白；原始 `.nema` 和 `.nemat` 中均禁止 Tab。字典是 `.nemat` 文件级传输层功能，原生 `.nema` 中的 `^0` 只是正文。

## 输入（原生 .nema）

```text
 \>3 1
A AuthenticationService Auth
B SessionStore Storage
A>X>B Reads AuthenticationService
```

## 压缩传输的实际控制格式

```text
 \!NEMAT1
 $2
 @0 "AuthenticationService"
 @1 "SessionStore"
 \!DATA
 \>3 1
A ^0 Auth
B ^1 Storage
A>X>B Reads ^0
```

实际 `encode()` 按字节长度筛选字典，可能只选择其中一项，也可能全部不选；以上示例用于解释引用格式，不保证是优化器的具体输出。解码时 `^0`、`^1` 按当前文件字典展开；源文件中的字面 `^` 被编码为 `\^`，保证还原时不误展开。

## Python 运行例子

```python
from codec.nemat import encode,decode
source = " \\>3 1\nA AuthenticationService Auth\nB SessionStore Storage\nA>X>B Reads AuthenticationService\n"
packed = encode(source)
assert decode(packed).encode() == source.encode()
```

注意：原生 `.nema` 的字面反斜杠不是 `.nemat` 的特殊域头；压缩层的 `\!NEMAT1` 标识仅适用于传输文件。禁止递归字典，解压须有限额。字典开销、解码说明与目标 tokenizer 成本必须一同计入性能对照。
