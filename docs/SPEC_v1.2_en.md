# .NEMA v1.2 — Current English Language Reference

**Status:** experimental specification and runnable Python reference implementation. Not a standardized file format. File extensions: `.nema` (native) and `.nemat` (reversible transport).

## Concept

.NEMA is a **vertically irregular format**. ASCII U+0020 spaces indicate horizontal columns; LF extends a column vertically only when necessary. Mandarin and Japanese sentences may remain intact; English may use PascalCase or `HTTPItIs` to reduce line breaks, but semantic rendering is **not** a reversible reconstruction of original capitalization. A real ASCII Tab introduces domain headers and the first Table header. Domains are contiguous without a blank separator. A document terminates with two empty physical lines (three trailing LF bytes after the last content line).

## The three modes

| Mode | Recognition | Columns |
|---|---|---|
| 5W1H (default) | Non-Tab first body line | X0 What, X1 Why, X2 How, X3 Who, X4 When, X5 Where |
| Table | The very first body line starts with one Tab | That line supplies column labels; row X0 starts a new record |
| Graph | Header starts `\t>` | Node has exactly one leading ASCII space; Edge starts at column zero; 2+ spaces continue X2 |

## Examples

In code below, `⇥` is an editorial marker for an actual Tab, `␠` for an actual ASCII space. Actual `.nema` files **never** use these glyphs in place of whitespace.

```text
⇥T1 1
BuildLoginFlow PreventLeaks Rust AuthAgent Now AuthService
⇥>G1 1
␠A LoginAPI Authentication
␠B TokenStore SessionStorage
A>X>B Reads VerifySession
␠␠CacheExpiredRetryOnce


```

Node `A`: X0=A, X1=LoginAPI, optional X2=Authentication. Edge `X`: A→B, X1=Reads, optional X2=VerifySession; continuation adds to X2. Reverse `B<Y<A` means A→B; `A=U=B` is an undirected association; loops and parallel edges are allowed. Node/Edge IDs must be unique and endpoints must exist.

The leading space before `A` is **syntax**. Graph X1 identifiers (e.g. `LoginAPI`) are preserved literally, with no `\=` marker. Tooltip on hover/focus reads X2, and click/tap pins inspector details. No X2 changes graph topology.

## Transport, exactness and source code

Native semantic rendering may change spacing/case. `.nemat` codec must decode to the **exact UTF-8 bytes** of the native `.nema` file; it uses `Tab+$N` dictionary declarations, `Tab+number` prefix group selection, and `\^` for a literal caret. Domain inputs must be validated after transport decoding. Source code such as Rust/TS/Python is not converted into `.NEMA`: only collaboration metadata, tasks, interfaces and graph relationships use it.

Read [Chinese normative specification](SPEC_v1.2_zh.md), [transport](TRANSPORT_v1.2.md), [JSON benchmarks](JSON_COMPARISON_METHOD_v1.2.md), [interpreter instructions](INTERPRETER_USAGE_v1.2.md).

## R7 audit clarification — Graph extensions

Graph X3+ extensions are surfaced as optional `extensions: {"X3":"..."}` in the semantic interpreter, preserving exact identifiers such as `APIKey` and `HTTP401`. The number of leading spaces on a continuation line selects X2 (two), X3 (three), etc. They do not affect edge direction. A Graph Node begins with exactly one ASCII space; no `\=` marker is needed.
