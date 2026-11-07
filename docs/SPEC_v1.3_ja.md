> v1.3 authoritative Graph delta: `docs/GRAPH_V13_MIGRATION.md`. Node and Edge both start at X0; one leading space continues X2, two X3; domain header still begins with a literal Tab and is unchanged. Historical R7 text below, if quoted, is non-normative.

# .NEMA v1.3 — 日本語の現行文法ガイド

**状態：** 実験仕様。Python リファレンスインタープリタと検証用データを同梱。標準化機関による公開規格ではありません。`.nema` は編集用、`.nemat` は可逆通信形式です。

## 基本設計

.NEMA は**縦方向に不規則なデータ形式**です。横方向は ASCII スペース (U+0020) で列を分け、意味を区切る必要があるときだけ LF で縦に延長します。日本語・中国語の文章は通常連続で表現し、英語では `BuildLoginFlow` や `HTTPItIs` のような記法を利用できます。意味表示は元の大文字・スペースを一意に復元するものではありません。

ヘッダーは `Tab + ドメインID + 空白 + 改訂番号`、Graph ヘッダーは `Tab + > + ドメインID + 空白 + 改訂番号`。ドメイン間の空行は不要です。末尾は完全な空行が 2 行続くことで示します。

## 3 つのモード

| モード | 判定条件 | 列の意味 |
|---|---|---|
| 5W1H（既定） | ヘッダー直後の本文が左端から始まる | What → Why → How → Who → When → Where |
| Table | 最初の本文行が 1 個の Tab から始まる | ヘッダー名と自由な列 |
| Graph | ドメインヘッダーに `>` がある | Node / Edge の ID、名称、説明 |

```text
⇥T1 1
認証処理を確認する 情報漏洩を防ぐ トークンを検証する
⇥>G1 1
A LoginAPI Authentication
B TokenStore SessionStorage
A>X>B Reads VerifySession
␠CacheExpiredRetryOnce


```

`⇥` と `␠` は説明用の可視記号です。実際のファイルにはそれぞれ本物の Tab と ASCII スペースを入れます。Graph の Node は行頭 **スペース 1 個**で定義し、Edge は**インデントなし**です。**スペース 2 個以上**から始まる行は現在の Node/Edge の X2 の続きです。

Node の X0 は ID、X1 は `LoginAPI` のような**文字どおりの名称**、X2 は任意の説明です。Edge `A>X>B` は A→B を表し X が Edge ID、`B<Y<A` は A→B、`A=U=B` は無向関係を表します。ホバー・キーボードフォーカスでは X2 を表示し、クリック・タップでは詳細を固定表示します。X2 はトポロジーに影響しません。

`.nemat` は辞書 (`Tab+$N`)、数字接頭辞 (`Tab+数字`)、リテラル `^` のエスケープ (`\^`) を利用して圧縮し、**元の `.nema` の UTF-8 バイト列**を完全に復元しなければなりません。Rust/TS/Python のソースコード自体は NEMA に変換しません。

参照：[中国語の完全仕様](SPEC_v1.3_zh.md)、[Codec](TRANSPORT_v1.3.md)、[JSON 比較方法](JSON_COMPARISON_METHOD_v1.3.md)、[インタープリタ](INTERPRETER_USAGE_v1.3.md)。

## R7 audit clarification — Graph extensions

Graph の X3 以降の拡張列は、インタープリタの意味表示に `extensions: {"X3":"..."}` として出力します。`APIKey` や `HTTP401` は文字列の綴りを保持します。継続行の先頭スペース2個は X2、3個は X3、という座標規則です。Node 宣言の先頭は ASCII スペースちょうど1個で、`\=` は不要です。
