# .NEMA v1.3 Graph token delta (local models only)

R7 versus v1.3 Graph sources with identical semantic AST, header bytes and content. These are local SentencePiece BPE/Unigram tests, NOT model provider token counts or end-to-end API costs. Original R7 JSON/YAML comparison remains in historical benchmark reports.

| Sample | R7 bytes | v1.3 bytes | BPE R7 → v1.3 | Unigram R7 → v1.3 |
|---|---:|---:|---:|---:|
| graph_3n_4e.nema | 240 | 236 | 144 → 141 | 186 → 182 |
| graph_40n_160e.nema | 8488 | 8425 | 6952 → 6889 | 7152 → 7089 |
| graph_x3_extensions.nema | 127 | 124 | 60 → 57 | 94 → 91 |
