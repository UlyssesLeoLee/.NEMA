# .NEMA R7 validation status

- Current docs/code: `.NEMA v1.2 R7` (backward-compatible extension-output fix; no new syntax markers).
- Original regression + new regression tests: 52/52 passing.
- Separate interpreter selftest: passing (includes X3).
- Offline Chromium inline injection: homepage @1440/800/390 and audit page; Graph inspector X3, source whitespace, language metric, no overflow passed.
- 1800 deterministic generated fuzz attempts: codec roundtrip passed for every syntactically valid case.
- JSON benchmark: 8 scenarios, BPE/Unigram values verified against bundled local models. Type-tagged baseline recorded separately.
- Source download: interpreter ZIP repacked from identical `codec/native.py`.
- Not verified: file:// direct navigation, public HTTP deployment, Safari, Firefox, real IDE/IME installed integrations or commercial LLM billing.

See `browser_r7.json`, `docs/REVIEW_R7_FIVE_ROUNDS.md`, `bench/tagged_json_audit_r7.json`.
