# .NEMA v1.5 · 共通字典与可逆传输案例

> 共通字典是 `.nemat` 的可选压缩机制，不是新的原生领域语法。示例与项目内 `codec/nemat.py` 的真实输出逐字节一致。原生 `.nema` 领域头只使用半角空格。

## 1. 两个领域的原始 .nema

```text
 ?Task1 1
Authenticate ValidateToken
 ?Task2 1
Authenticate ValidateToken


```

## 2. 共通字典压缩后的 .nemat

使用 `encode(source, ['Authenticate','ValidateToken'])`：

```text
	$2
Authenticate
ValidateToken
 ?Task1 1
^0 ^1
	2 1
^0 ^1


```

- 传输流第一行的真实 `Tab + $2` 是 **`.nemat` 字典清单控制行**，并非 `.nema` 领域头；它在传输协议中允许使用。
- 接下来两行是字典条目 `Authenticate` 与 `ValidateToken`，对应 `^0` 和 `^1`。
- ` ?Task1 1` 是原生 5W1H 领域头；字段内容可以写作 `^0 ^1`，解码后恢复原文。
- `Tab + 2 1` 是 `.nemat` 中对第二个同前缀领域的压缩控制行，解码器重建完整的 ` ?Task2 1`。
- 因此 `.nemat` 可以包含 Tab 控制行，但**原生 `.nema` 领域头绝不含 Tab**。不要混淆两个层次，也不要把传输示例直接交给原生解释器。

## 3. Python 调用

```python
from codec.nemat import encode, decode
source = " ?Task1 1\nAuthenticate ValidateToken\n ?Task2 1\nAuthenticate ValidateToken\n\n\n"
encoded = encode(source, ['Authenticate', 'ValidateToken'])
assert decode(encoded).encode('utf-8') == source.encode('utf-8')
```

## 4. 安全与收益边界

共通字典上限、特殊字符与敏感信息筛除规则以随包 Codec 为准。不得把重复片段直接等同于 Token 收益；真实评估必须统计字典清单成本、文本内容、压缩前后 tokenizer 和模型提示词成本。`optimize()` 会在原生、字典、前缀和组合候选中按给定评分选择，但不保证每次都优于紧凑 YAML。
