# .NEMA v1.5 · Complete release (2026-11-07)

## Start

- Open `website/index.html` for the visual website; Three.js scene loads from CDN only when online.
- Open `website/syntax.html` for the **3-column syntax inventory**; click a row to open the detail modal (Escape, overlay click, ×).
- Open `website/docs/index.html` for consistent HTML renderings of all design documents. Markdown originals remain in `docs/`.
- Read `docs/SPEC_v1.5_zh.md` for authoritative current grammar.
- Use `python -m tools.migrate_v13_to_v15 OLD.nema NEW.nema` for explicit v1.3 migration.

## Critical grammar

Every domain header begins with exactly **one ASCII U+0020 SPACE** — no Tab and no fullwidth U+3000:

```text
 ?Task1 1
BuildLoginFlow PreventLeak VerifyToken Owner Today AuthService
 Table1 1
A Ready First
B Blocked Second
 >Gauth1 1
A LoginAPI Authentication
B TokenStore SessionStorage
A>X>B Reads VerifySession


```

5W1H ` ?`, Table ` `, Graph ` >`. Graph Node/Edge X0 remains unchanged. Table supports a SPACE-prefixed first body row as explicit headers or implicit `column1...columnN` otherwise. There are **no raw Tab characters in native .nema**; Tab controls exist only in the separate .nemat transport layer. No fullwidth spaces anywhere.

Old v1.2/v1.3 docs and benchmark results remain historical references and are **not** current v1.5 performance measurements. `.nemat` is a separate reversible transport codec, not an undocumented fourth native mode.

## v1.5 Statue Three.js visual edition

The homepage now uses a **procedural 3D Ariadne marble sculpture** rather than a flat moving illustration. Sculpted hair, carved stone facial features, classical garment folds, raised supporting arm, and a spun golden yarn ball are rendered with cel-shaded stepped highlights and dark comic-style outlines. A lit golden thread physically curves outward from the yarn ball and moving glints trace its path. Original `assets/ariadne-comic.webp` remains the fallback when WebGL/CDN is unavailable or reduced-motion is requested.

- Entry point: `website/index.html`.
- Three.js scene: `website/three-hero.js` (pinned `three@0.171.0` CDN; needs network on initial load).
- Visual overrides: `website/statue-hero.css`.
- There is **no external 3D character file**; geometry is generated procedurally, so this is a stylized sculptural interpretation, not a high-polygon photogrammetric statue or a rigged character.
- Domain headers / parser / training dataset are unchanged from v1.5.
