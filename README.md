# NEMA — Ariadne's Thread for AI Agents

**Complete trilingual brand, website, human documentation, AI training and NEMA v0.3 prototype bundle.**

## Open the site

Unzip this archive and open `index.html` directly in a modern browser. No Node, build system, server or API key is needed. Use 中 / 日 / EN at the top to switch all homepage copy, semantic inspector field labels, rules and relevant document links.

The landing page loads optional OFL-licensed typography over the internet. Offline use is fully functional with native font fallbacks. No font binaries are included. See `docs/FONT_LICENSES.md`.

## File map

- `index.html`, `styles.css`, `app.js`: trilingual offline-capable website with source ⇄ structured domain inspector.
- `docs/HUMAN_GUIDE_zh.md`, `_ja.md`, `_en.md`: hands-on authoring rules and rendered examples.
- `docs/NEMA_SPEC_v0.3.md`: NEMA/2 format reference specification (preserved v0.3).
- `docs/VERIFICATION_REPORT_v0.3.md`: original measured compression results and test notes.
- `docs/FONT_LICENSES.md`: verified free/open commercial font selection and fallback policy.
- `training/NEMA_AI_TRAINING.md`: AI-focused context training guide.
- `training/nema_sft_train.jsonl`, `nema_eval.jsonl`: candidate supervised instruction and evaluation items.
- `prototype/v0.3/`: complete v0.3 Python reference parser, patcher, scheduler, tests, benchmarks, sample and reports (preserved).
- `downloads/`: original `NEMA_v0.3_positional_verified.zip`, `.nema`, `.npatch`, logo bundle.
- `assets/`: logos in SVG and PNG, promotional art and social image.
- `previews/`: previous site screenshots for visual reference.

## Real-world limitations

- NEMA v0.3 is experimental. It has not been verified as universally more token-efficient than JSON/YAML/Markdown.
- The site's inspector demonstrates **the supplied example**. It is not an arbitrary file upload parser, version-control backend or IDE1.0 integration.
- Domain CAS protects the reference store, but updating external production files requires extra resource-level conflict validation.
- Commands in NEMA acceptance lanes are data and do not grant execution authority.

## Source reference

`python -m unittest discover -s prototype/v0.3 -p 'test_nema2.py' -v`

If imports fail from the repo root, run `cd prototype/v0.3` and execute `python -m unittest test_nema2 -v` instead.

## Brand

Ariadne's golden thread in a geometric maze. Deep navy `#0A1525`, warm gold `#D9AD69`. See `docs/BRAND_GUIDE.md`.
