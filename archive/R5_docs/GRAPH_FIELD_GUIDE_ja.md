# NEMA Graph：フィールドと方向

**Graph は NEMA の三つのモードの一つ。X0 は Node / Edge の ID と構造、X1 は名前、X2 は役割または動作の説明です。**

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

Authentication は説明であり、Edge でも自動的なリンク生成でもありません。

方向は X0 のみで決まり、X1 / X2 や下方向の追記では変わりません。

A LoginAPI Authentication も3列として有効ですが、PascalCase の意味表示では LoginAPI が Login API と表示され得ます。綴りを保つ場合は \=LoginAPI と記述してください。

| NEMA | Rendering |
|---|---|
| `A>X>B` | A → B |
| `A<Y<B` | B → A |
| `A=U=B` | A — B |
| `A>P>A` | A ↻ A |
| `A>X>B` + `A>Y>B` | A ⇉ B |
| `A>X>B` + `B>Y>A` | A ⇄ B |

正式な Graph ヘッダーは ⇥>G1 1（ID とリビジョン）。⇥>1 は省略例で、現在の v1.1 パーサでは無効です。

NEMA v1.1 — website review R3 (2026-11-07).


## ホバー説明と詳細表示（Website R3）

Graph の SVG 表示で Node にホバーすると **ID、X1 の名前、X2 の説明** を表示し、Edge にホバーすると **Edge ID、X1 の関係名、実際の矢印方向、X2 の説明** を表示します。X2 の縦方向の継続記述はまとめて表示します。X2 がなければ「省略可能・未記入」と表示し、内容を捏造しません。

`A \=LoginAPI Authentication` では Node A の説明は `Authentication`。`A>X>B Reads VerifySession` の Edge X は `A → B` と `Verify session` を表示します。逆方向の `B<Y<C` は **C → B**、無向の `A=U=C` は **A — C** です。説明はグラフ構造を変更しません。

マウスを離すと閉じます。Tab フォーカスでも表示、Escape で非表示、クリック / Enter / Space で詳細パネルを開きます。タッチではタップで詳細を開きます。説明のポップアップはポインター操作を奪わず、スマートフォンのガイドでは図の下に表示します。詳細設計は `docs/GRAPH_HOVER_RENDERER_DESIGN.md`。
