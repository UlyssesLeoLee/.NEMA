# NEMA typography and font licensing

## Approved free, open-source, commercially usable families

| Language / use | Primary font | License | Official source |
|---|---|---|---|
| Latin / English brand and UI | Inter | SIL Open Font License 1.1 | https://github.com/rsms/inter |
| Simplified Chinese | Noto Sans SC | SIL Open Font License 1.1 | https://github.com/google/fonts/tree/main/ofl/notosanssc |
| Japanese | Noto Sans JP | SIL Open Font License 1.1 | https://github.com/google/fonts/tree/main/ofl/notosansjp |

Font loading is via Google Fonts CSS links in `index.html` at runtime, when connected. The published ZIP **does not distribute font binaries**. Browsers without internet use the declared system fallback stacks and retain full functionality. A deployment requiring fully identical appearance offline may configure its own licensed font hosting separately, following the fonts' actual license terms.

All three fonts are OFL-licensed and permit commercial use; refer to the original licenses for redistribution and derivative restrictions. This document is not legal advice.

## Language-specific CSS stacks

- `zh-CN`: `Inter, Noto Sans SC, PingFang SC, Microsoft YaHei, system-ui, sans-serif`
- `ja`: `Inter, Noto Sans JP, Hiragino Kaku Gothic ProN, Yu Gothic, Meiryo, sans-serif`
- `en`: `Inter, system-ui, sans-serif`
- Monospace (data source): OS-installed monospace stack: `ui-monospace, SFMono-Regular, Consolas, Liberation Mono, monospace`.

## Visual principles

1. Headings: 700 weight, careful hierarchy and restrained tracking.
2. Body: 400–500 weight with 1.7–2.0 line height for CJK readability.
3. Code: stable monospace, literal tab and space semantics, no auto-formatting.
4. Keep fonts and body styles tokenized through CSS custom properties so an IDE1.0 renderer can match them.
5. Avoid font file bundles and proprietary fonts in distributed artifacts.
