# .NEMA v1.3 — Current complete release

1. `.NEMA` is the only product brand spelling; `.nema` and `.nemat` remain lowercase file suffixes.
2. Three modes: What-first 5W1H, Table (Tab header), Graph. Node uses exactly one ASCII-space indentation; Edge begins at column zero; X2 carries optional descriptions.
3. ASCII space is a real layout coordinate. Source display supports an opt-in `·` marker but copy/export remains byte-exact.
4. Chinese/Japanese text may remain unsplit. English PascalCase is a semantic view, not a byte-exact reconstruction.
5. Node and Edge hover/focus/tap descriptions and directed multi-edges are supported by the website.
6. Token Lab compares native `.nema`, reversible `.nemat`, object JSON, positional JSON, positional YAML, and uses local BPE + Unigram counts with reproducible scripts.
7. Interpreter download, AI training/hold-out/adversarial data, IDE1.0 and IME1.0 integration specs are included.
8. On-device Windows TSF / IDE Rust integration and proprietary tokenizer billing are pending and not reported as completed.

## R7 审核修订

见 `docs/REVIEW_R7_FIVE_ROUNDS.md`。Graph X3+ 现在会进入 `view()` 的 `extensions`；解释器 ZIP 与训练测试已同步。Token Lab 的 R6 8 组原始数据保持不变，另新增带类型标记的位置式 JSON 对照。现行网站新增 `audit-r7.html`，旧 R4/R5 审查页面是历史记录。
