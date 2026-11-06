# NEMA/2 v0.3 · Human Authoring & IDE1.0 Rendering Guide (English)

## Purpose

NEMA `.nema` is an AI-first, two-dimensional positional data format. **One flush-left domain block is one complete unit of agent work and commit**, not an individual text line. People should normally use an IDE1.0-style structured view. Version 0.3 remains an experimental reference specification.

## Minimal example

Use the real file at `downloads/sample.nema` for authoritative formatting. Column separators are literal **Tab (U+0009)**; relation indentation uses literal **ASCII space (U+0020)**. An editor that automatically converts Tabs to spaces will corrupt the format.

```text
n2
%T	who	what	when	where	why	how
%I	method	path	req	res	auth:b
%F	path	lang	owner
T/a7 1
 argo	limit	now	I/login	abuse	60/min/ip
  I/login
   F/auth
    T/design
     cargo test
T/design 1
 claude	design	now	I/login	contract	review
I/login 1
 POST	/v1/login	credentials	token	1
  F/auth
F/auth 1
 src/auth.rs	rust	argo
```

## Six authoring rules

1. **Start with version:** the first line is `n2`; reject unknown versions.
2. **Declare each schema once:** `%T` defines the ordered slots `who/what/when/where/why/how`, separated by literal Tabs. Reordering a schema is a semantic migration, not formatting.
3. **Open each domain at column zero:** `T/a7 1` means stable domain ID `T/a7`, revision `1`; the physical line number never identifies it.
4. **Use exactly one leading space for payload:** fill fields horizontally in schema order using Tabs between values.
5. **Use 2–6 leading spaces for relations:** the absolute indentation width is a formal type marker, not visual hierarchy.
6. **Validate patches:** `.npatch` commits bind an expected domain revision and the actual SHA-256 schema fingerprint; touching external files requires separate resource conflict checks.

## Vertical position lanes

| Leading spaces | Meaning | Example |
|---:|---|---|
| 0 | Domain header / revision | `T/a7 1` |
| 1 | Schema-ordered horizontal fields | ` argo<TAB>limit<TAB>...` |
| 2 | Read / reference domain | `  I/login` |
| 3 | Write / modify domain | `   F/auth` |
| 4 | Prerequisite domain | `    T/design` |
| 5 | Acceptance/check declaration (**not executable**) | `     cargo test` |
| 6 | Extended relation, `target<TAB>kind` | `      I/login<TAB>documents` |

Never replace indentation spaces with Tabs, or horizontal Tabs with sequences of spaces. Invalid schemas and unknown relationships must produce explicit errors rather than a language model's guess.

## How IDE1.0 renders a block

Given `%T` as `who/what/when/where/why/how`, the row

` argo<TAB>limit<TAB>now<TAB>I/login<TAB>abuse<TAB>60/min/ip`

becomes:

| Who | What | When | Where | Why | How |
|---|---|---|---|---|---|
| argo | limit | now | I/login | abuse | 60/min/ip |

The relationship lanes also appear as read `I/login`, write `F/auth`, dependency `T/design`, and acceptance declaration `cargo test`. The IDE should maintain reversible links to the original slots and lane positions and must never silently normalize the indentation.

## Types and compact encodings

An untyped slot is a string; `:n` indicates an integer; `:b` is a boolean expressed as `0` or `1`. Literal Tab/newline/carriage return/backslash are encoded as `\\t`, `\\n`, `\\r`, `\\\\`; a string's leading space is encoded as `\\s`. The optional `$code<TAB>literal` dictionary and `:GROUP<TAB>prefix` ID-prefix compression save repeated strings. Prefer using the reference serializer to generate them.

Less source text does not imply fewer tokens for every model. Benchmark against the actual tokenizer and workload before claiming a universal advantage.

## Concurrent agents and safety

Separate agents can prepare changes for separate domains concurrently. The store should atomically compare revision and schema fingerprint and reject stale patches. Different domain IDs do **not** prove independent access to actual files: external resource-level locking/hash checks remain necessary. Acceptance lines are data; an authorized runner decides whether and how to execute checks.

## Suggested IDE flow

Open `.nema` → parse shared schemas → render domain cards → select stable domain ID → edit fields/relations → generate `.npatch` → validate → check dependencies and file conflicts → atomically commit → refresh.

Full spec: `prototype/v0.3/SPEC.md`; benchmark and adversarial report: `prototype/v0.3/REPORT.md`; executable tests: `prototype/v0.3/test_nema2.py`.
