# NEMA v1.1 — Irregular Vertical Semantic Format (experimental)

**Normative reference: `NEMA_SPEC_v1.1_zh.md`.** This English edition captures the implementation contract. v1.1 replaces Tab-separated body columns with a single ASCII SPACE as the X-axis separator. LF extends semantic atoms vertically only where necessary.

## Three modes and What-first

The one-Tab domain header is `TAB + domain ID + SPACE + positive revision`. The optional `>` before a domain ID denotes a Graph. Otherwise a first body line starting with a Tab selects a Table; without that marker, the default mode is 5W1H. Table mode removes the initial Tab only from its header row. Domain headers have no mandatory blank lines between them; exactly two empty physical lines mark EOF (three LF after the last data row).

**5W1H column order:** X0 What, X1 Why, X2 How, X3 Who, X4 When, X5 Where. What-only rows represent plain text. Body fields use ASCII SPACE (not Tab), and multiple adjacent spaces represent intervening empty columns. A leading space on a continuation row leaves X0 empty and extends the previous column's semantic atoms. To store a literal space inside a cell, write `\ `; literal backslash `\`; literal Tab `\t`.

**English** prefers `BuildLoginFlow` → `Build login flow`; `What` LF `HTTPItIs` → `What HTTP it is`. Two contiguous all-caps abbreviations such as `APIHTTP` cannot be distinguished reliably and require a line break or other explicit disambiguation. Sensitive identifiers, API casing, URLs and literal code symbols use the exact marker `\=APIKey`, which renders `APIKey` without case conversion. **Chinese and Japanese** stay continuous in a cell unless a meaningful vertical break is needed. Rendering is semantic and not a byte-reversible inverse of PascalCase input.

## Graph

Graph X0 identifies a node (`A`) or an edge (`A>X>B`, `A<Y<B`, `A=U=B`). The edge ID is between two matching operators. `A>X>B` means A→B; `A<Y<B` means B→A; `A=U=B` is undirected; `A>P>A` is a loop. X1 is label, X2 is explanatory text, X3+ optional attributes. Two edges may connect the same nodes if their IDs differ. Text in a node or edge may continue vertically with spaces locating its column. Unknown node references, mixed arrows and duplicate edge IDs must fail validation.

## Reversible transport and evidence

The optional `.nemat` wire format has a leading `TAB + $N` dictionary manifest, exact-cell `^index` references, `TAB + digit` prefix-group selectors and `\^` for a literal caret. The wire decoder must reconstruct the exact original `.nema` bytes. A failed or unprofitable encoding falls back to `.nema`. The native parser **must not** interpret `.nemat` by guessing.

See `NEMA_TRANSPORT_v1.1.md`, `../bench/REPORT.md`, `../training/TRAINING_GUIDE.md` and `../website/token-benchmark.html`. Token measurements use local offline SentencePiece BPE/Unigram, not official GPT/Claude/Gemini billing; raw code files remain in their native language formats.


## Graph rendering: hover descriptions (R3, no grammar change)

X0 determines identity and direction; X1 names the Node / Edge; X2 optionally describes it. Hover displays X2 and, for Edges, the resolved direction. Vertical continuation lines remain attached to the same element; absent descriptions are marked optional rather than fabricated. Click/Enter/Space selects the persistent inspector; Tab and Escape show/hide previews; touch users tap. This is a **presentation-only feature**; `.nema`/`.nemat` syntax and Token benchmarks are unchanged.
