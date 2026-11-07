# Graph v1.3 Migration Contract

- Header invariants: preserve literal one Tab at column zero, optional `>` Graph marker, unchanged domain ID, **one** ASCII space before positive revision. Example: `\t>Gauth1 1`.
- Node/Edge declarations: both unindented X0; first token is a valid Node ID or a full relation expression `A>X>B`, `A<Y<B`, `A=U=B`.
- Strict discriminator: any `>`, `<`, `=` in first token requires fully valid Edge expression. Error on malformed or mixed symbols. Never fall back to Node.
- Continuations: R7's one/two/three spaces before Node/X2/X3 become zero/one/two spaces. X1 continuation still unsupported.
- No changes to 5W1H/Table rules, IDs, relation direction, X1 verbatim, X2 semantic normalization, X3+ exact fields, native LF termination, or `.nemat` reversibility.
- Use `tools/migrate_r7_to_v13.py` explicitly; conversion validates R7 source, checks both versions' semantic views, verifies domain headers, and refuses overwrite.
- Existing R7 token measurements and training corpus are **not** v1.3 results; use `training/v13_graph_grammar_*.jsonl` to train the syntax delta. Original R7 docs remain for reference.
- IDE1.0 and IME1.0 must negotiate format/grammar revision out of band or alongside schema metadata. Do not silently change existing saved R7 files.
