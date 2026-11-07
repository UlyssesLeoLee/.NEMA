# .NEMA v1.2 R7 — Audited Complete Delivery

**Brand:** `.NEMA` (leading dot, uppercase). **File extensions:** `.nema` (native) and `.nemat` (reversible compressed transport). `NEMA.` is not the brand spelling.

## Open the site

Double-click **`index.html`** to open the multilingual website (ZH/JA/EN) including all three syntax modes, a live Graph with Node/Edge hover, the Token Lab showing JSON/YAML controls, an interpreter download page, and Greek-mythology cel-shaded artwork. A Three.js WebGL accent is attempted on desktop when the CDN can load; otherwise the page retains its static art. All critical site content runs without WebGL.

**Standalone interpreter:** download from `website/download.html` or use `downloads/NEMA_Interpreter_v1.2.zip`. Python 3.10+ for parser/codec; optional `sentencepiece` only for offline benchmark counting. Python reference only: **not a Rust SDK, Windows EXE or already installed IDE/IME feature**.

## Deliverables

- `website/`: comic-book cel-shaded editorial theme, 3-mode visualizer, Graph focus/hover/touch inspector, graphical Token Lab, downloads and guides; code whitespace visualization toggles display only.
- `docs/`: definitive Chinese v1.2 syntax; English/Japanese current summaries; Graph render specification, reversible codec, JSON comparison methods, interpreter operations, AI training, IDE1.0 and IME1.0 development plans, acceptance tests.
- `codec/`: Python standard-library native `.nema` parser, semantic view, reversible `.nemat` decoder/encoder and CLI.
- `downloads/`: independently runnable interpreter ZIP.
- `examples/`: 8 groups of native, compressed, JSON and positional comparison fixtures including uncompressible cases.
- `bench/`: reproducible BPE / Unigram models and script, raw CSV/JSON and limitations.
- `training/`: positive, held-out and adversarial prompts with validation and golden rules.
- `tests/`: Python unit/consistency tests and Chromium browser smoke.
- `archive/`: separate historical prior-version references; do **not** treat them as current grammar.

## Key grammar

In Graph mode `	>Gauth1 1`, one leading ASCII space defines a Node (` A LoginAPI Authentication`), no indentation defines an Edge (`A>X>B Reads VerifySession`) and two spaces continue X2 (`  CacheExpiredRetryOnce`). 5W1H is What-first: **What, Why, How, Who, When, Where**. Table mode uses a single Tab-prefixed *first header row*. Natural-language words can be PascalCase or left as intact Chinese/Japanese text; fields use real ASCII spaces. In example views, visible `·` and `⇥` are display aids only—not stored delimiters.

## Measurement

BPE/Unigram counts come from **bundled locally trained whitespace-preserving SentencePiece models**; percentages are NOT official GPT/Claude/Gemini billing data. See `bench/LATEST_REPORT_V12.md` and `website/token-benchmark.html`. Strong baseline is *positional JSON*, separately from ordinary self-describing JSON. Native vs `.nemat` bytes and tokenizer counts are different metrics. Some short/high-entropy cases will not benefit from the codec.

## Integrity and validation

Run `python -m unittest discover -s tests -p test_v12.py` from this directory. Run `python -m codec.cli render examples/complete_v12.nema`. For browser checks, install Playwright/Chromium separately; recorded evidence in `audit/` and screenshots under `previews/`. Check SHA256 in `MANIFEST_SHA256.txt` and each ZIP using ZipFile.testzip().

## Status and boundaries

The complete website and Python reference interpreter are bundled. The IDE1.0/IME1.0 integration docs are implementation specifications; no source changes have been pushed into those external repositories. Actual GPT/Claude/Gemini API tokenizer and full end-to-end agent rework-cost trials have not been executed. Three.js embellishment depends on the availability of the pinned CDN and WebGL.

## R7 audited corrections

- Fixed Graph X3+ semantic output (`extensions`) while preserving exact technical literals (APIKey, HTTP401, SHA256); X2 remains the hover-only note.
- Fixed active Chinese/Japanese/English Graph name-escaping copy and mislabeled Japanese benchmark metric.
- Added self-identifying `w/t/g` positional JSON baseline (separate from R6's externally negotiated positional JSON) with actual locally executed BPE/Unigram counts.
- Added `website/audit-r7.html` (three languages), docs audit, Graph X3 golden corpus and regression suite; interpreter download rebundled with updated parser.
- Existing R6 benchmark numbers are not re-labeled or fabricated. Real browser navigation and commercial provider billing remain unverified.
