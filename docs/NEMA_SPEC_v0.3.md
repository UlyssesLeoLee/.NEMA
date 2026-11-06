# NEMA/2 — Minimal Two-Dimensional Agent Work-Domain Format

## Purpose

`.nema` is an AI-first, positional text protocol. The smallest independently assignable and committable unit is the **domain block**, not the physical line or one field. A stable `group/id` identifies a domain independently of its file position. Every block can be assigned to an Agent by a scheduler; assignability does not imply simultaneous safe execution.

## Compact grammar

```text
n2
%T<TAB>who<TAB>what<TAB>when<TAB>where<TAB>why<TAB>how
T/a7 1
 argo<TAB>limit<TAB>now<TAB>I/login<TAB>abuse<TAB>60/min/ip
  I/login
   F/auth
    T/design
     cargo test
```

`<TAB>` above denotes a single literal U+0009 TAB byte, **not** the characters `<`, `T`, etc. The actual `sample.nema` contains tabs.

| Indent | Meaning | Grammar | Executable? |
|---:|---|---|---|
| 0 | Begin domain | `GROUP/id SPACE version` | No |
| 1 | Positional payload | `schema[0] TAB schema[1] ...` | No |
| 2 | Read/reference target | `GROUP/id` | No |
| 3 | Write/modify target | `GROUP/id` | No |
| 4 | Prerequisite Agent domain | `GROUP/id` | No |
| 5 | Acceptance instruction text | free text, escaped | No |
| 6 | Extended typed edge | `GROUP/id TAB relation` | No |

`n2` is magic/version. `%GROUP<TAB>...` defines a schema once in the document header. A field without a type suffix defaults to string; `:n` means integer, `:b` means boolean encoded as `0` or `1`. `group/id` uses ASCII identifiers. Each block must have exactly one 1-space positional row. Other rows are optional, repeating if needed. Blank lines are not part of the grammar.

Indentation **width is semantically meaningful** (unlike standard YAML, where it primarily marks hierarchy). IDE1.0 must never replace TAB field separators with spaces or auto-reindent an existing document without reserialization.

Optional header entries `$code<TAB>literal` intern repeated strings and `:GROUP<TAB>id-prefix` compress repeated IDs. Values beginning `^code` reference a dictionary. `\\^` escapes a literal initial caret. Literal tabs/newlines/CR/backslashes use `\\t`, `\\n`, `\\r`, `\\\\`. A literal initial blank in a string uses `\\s`. This keeps ordinary sentence punctuation untouched.

A domain can be extracted for an Agent, but its shared schema/dictionary/prefix table must accompany it, or be supplied by a versioned cached context. This is **header+one-block decoding**, not standalone block decoding without context.

## Stable addressing, concurrency and protocol

- Each domain has monotonic revision `rev >= 1`, independent of physical position/line numbers.
- Concurrent Agents can **prepare** edits in parallel. Database commits atomically compare the expected domain version (CAS); stale commits are rejected.
- For `uses` vs `touches` resources, scheduling must block read/write and write/write overlap, and honor `depends` edges. The included scheduler is a reference planner only.
- Resource IDs referenced in this prototype must resolve to domains in the same document. Cross-document external resource references require a future resolver/manifest.
- **Actual files/worktrees require separate commit-time hash checks or file locks.** The current store does not protect external file bytes.
- NEMA text is data, never executable authority. Validation commands in 5-space rows are merely declarations and require a separately authorized runner.

## Positional patch `.npatch`

```text
p2 SCHEMA_SHA256
T/a7 1
 5<TAB>120/min/ip
```

The patch header contains the SHA-256 digest of the canonical schema, including the slot order. Field positions are 0-based. A patch updates an entire domain under one base revision, even if only one field changes. A schema reorder invalidates old patches. The whole in-memory patch is validated before modification; the SQLite store is responsible for durable transactional commits.

## Compression objective

- **Physical horizontal:** fixed TAB slots suppress per-field names, commas and quotes.
- **Physical vertical:** indentation class suppresses per-line role words.
- **Structural:** domain group/ID once per block rather than on every row.
- **Contextual:** optional one-time schema, string dictionary, ID prefix.
- **Adaptive:** `write_auto(...,objective='bytes'|'gzip'|'tokens')`. `tokens` requires an actual model tokenizer callback. No general guarantee of beating JSON, YAML or MD on every workload/model.

The smallest byte representation need not have the fewest tokens or smallest gzip result. The format must prioritize validated positional semantics over lossy compression.

## IDE1.0 rendering requirements

Render a domain block into cards/columns for six W/H slots; highlight read/write/dependency lanes; show a dependency graph, code references, revision, pending patch and conflicts. Provide a raw/canonical diff and never format by inserting literal spaces in place of TAB separators. Invalid or unknown schema must produce an error instead of approximate model interpretation.
