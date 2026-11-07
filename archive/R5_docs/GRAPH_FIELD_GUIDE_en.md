# NEMA Graph: Columns, Notes & Directions

**Graph is one of NEMA’s three modes. X0 identifies a Node or Edge, X1 names it, and X2 optionally describes its responsibility or behavior.**

```text
	>G1 1
A \=LoginAPI Authentication
B \=TokenStore SessionStorage
A>X>B Reads VerifySession
  CacheExpiredRetryOnce


```

| Column | Node | Edge |
|---|---|---|
| X0 | `A`: Node ID | `A>X>B`: A → B, Edge ID X |
| X1 | `\=LoginAPI`: exact name | `Reads`: relation name |
| X2 | `Authentication`: optional note | `VerifySession`: optional note |
| X3+ | optional attributes | optional attributes |

Authentication is just a note, not an Edge and not an automatic link to an authentication service.

X0 alone determines the arrow direction. The name, description and vertical continuation never change its endpoints.

A LoginAPI Authentication also has three valid columns, but PascalCase semantic rendering may display X1 as “Login API”. Write \=LoginAPI to preserve the exact identifier spelling.

| NEMA | Rendering |
|---|---|
| `A>X>B` | A → B |
| `A<Y<B` | B → A |
| `A=U=B` | A — B |
| `A>P>A` | A ↻ A |
| `A>X>B` + `A>Y>B` | A ⇉ B |
| `A>X>B` + `B>Y>A` | A ⇄ B |

The formal Graph header is ⇥>G1 1 (ID and revision). ⇥>1 is incomplete shorthand and invalid in the current v1.1 parser.

NEMA v1.1 — website review R3 (2026-11-07).


## Hover descriptions and persistent inspector (Website R3)

Hover a Node in the rendered SVG to see its **ID, X1 name, and X2 description**. Hover an Edge's line or label to see its **Edge ID, X1 relationship name, resolved direction, and X2 description**. The description includes vertical continuations of X2 and is taken from the parsed semantic view, not guessed from the name. If X2 is missing, display an explicit optional-note fallback.

`A \=LoginAPI Authentication` → hovering Node A displays `Authentication`. `A>X>B Reads VerifySession` → hovering Edge X displays `A → B` and `Verify session`. The reverse edge `B<Y<C` must show **C → B**, and the undirected edge `A=U=C` must show **A — C** without an arrow. Hover must never mutate the graph, revisions, or text.

Pointer exit hides the preview; keyboard focus shows the same information; Escape hides it; click, Enter or Space selects an item in the persistent field inspector. Touch users tap items instead of hovering. Previews cannot intercept pointer events or cover critical mobile content. See `docs/GRAPH_HOVER_RENDERER_DESIGN.md` for implementation and acceptance criteria.
