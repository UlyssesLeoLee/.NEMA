# NEMA Trilingual Site QA — 2026-11-05

## Verified

- NEMA v0.3 unit tests: 23 / 23 passed (`docs/UNIT_TEST_RUN.txt`).
- Trilingual UI dictionary: 82 matching keys per language (zh-CN, ja, en); all relevant key names exist.
- Human authoring rules: six rules per language; seven positional depth labels per language.
- Source sample in the website exactly matches `downloads/sample.nema`, excluding the final newline.
- Four sample domains, each field array matches its declared schema slot count.
- Local HTML links: 11 local resources checked, all present.
- CSS parser: 156 top-level rules, zero parsing errors; JS syntax check passed with Node.js.
- No font binaries (TTF/OTF/WOFF/WOFF2) are distributed. Fonts use OFL-licensed Inter, Noto Sans SC and Noto Sans JP via CSS links, with system fallbacks.

## Browser verification limitation

Automated Chromium navigation to both file URLs and `127.0.0.1` was blocked by the test environment (`net::ERR_BLOCKED_BY_ADMINISTRATOR`). Thus this *revised* trilingual page was not browser-screenshot-verified in this run. Previous screenshots are retained under `previews/previous-*` strictly as historical visual references. The code is intended for normal static browser hosting and direct file opening; runtime behavior should be smoke-tested on deployment or a local browser without that policy.

## Experimental protocol disclaimers

The reported JSON/YAML/Markdown/NEMA raw byte sizes are from the preexisting synthetic v0.3 benchmark; they do not establish universal superiority by model token count. The demo's IDE1.0-like view illustrates only the bundled sample and is not a live IDE integration.
