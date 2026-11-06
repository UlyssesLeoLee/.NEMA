# NEMA/2 v0.3 · 手書き文法と IDE1.0 表示ガイド（日本語）

## 基本的な考え方

NEMA `.nema` は AI 優先の二次元位置データ形式です。**行頭から始まる一つの領域ブロックが、Agent に割り当てられる一つの作業領域**となります。通常は IDE1.0 のようなカード表示で読みます。v0.3 は実験的な参照仕様です。

## 最小サンプル

実ファイルは `downloads/sample.nema` にあります。値の区切りは **Tab (U+0009)**、関係行のインデントは **半角空白 (U+0020)** を用います。自動で Tab を空白に変換するエディターは使用しないでください。

```text
n2
%T	who	what	when	where	why	how
%I	method	path	req	res	auth:b
%F	path	lang	owner
T/a7 1
 argo	limit	now	I/login	abuse	60/min/ip
  I/login
   F/auth
    T/design
     cargo test
T/design 1
 claude	design	now	I/login	contract	review
I/login 1
 POST	/v1/login	credentials	token	1
  F/auth
F/auth 1
 src/auth.rs	rust	argo
```

## 人間が覚える六つのルール

1. **バージョン**：先頭行は `n2`。不明な版は解析せずエラーにします。
2. **Schema は一度だけ**：`%T` の列順 `who / what / when / where / why / how` を Tab 区切りで宣言します。順序変更は書式変更ではなくスキーマ変更です。
3. **領域ヘッダーはインデントなし**：`T/a7 1` は ID `T/a7`、リビジョン `1` を意味します。行番号には依存しません。
4. **フィールド行は先頭 1 空白**：値は Schema の列順に横方向で並べます。
5. **関係行は先頭 2～6 空白**：空白の数そのものが関係種別で、見た目だけの階層ではありません。
6. **パッチを検証**：`.npatch` は元リビジョンと Schema の本物の SHA-256 指紋を持つ必要があります。実ファイルにも別途競合検証が必要です。

## 縦方向の位置

| 先頭の空白数 | 意味 | 例 |
|---:|---|---|
| 0 | 領域ヘッダー | `T/a7 1` |
| 1 | Tab 区切りフィールド | ` argo<TAB>limit<TAB>...` |
| 2 | 読み取り・参照 | `  I/login` |
| 3 | 書き込み・変更 | `   F/auth` |
| 4 | 前提となる領域 | `    T/design` |
| 5 | 受け入れ条件の宣言（**自動実行されない**） | `     cargo test` |
| 6 | 拡張関係 `対象<TAB>種別` | `      I/login<TAB>documents` |

行頭のスペースと、行内の Tab を入れ替えないでください。不正な形式を LLM が意味で補完してはいけません。

## 横方向の 5W1H と画面表示

Schema `%T` が `who/what/when/where/why/how` の場合、

` argo<TAB>limit<TAB>now<TAB>I/login<TAB>abuse<TAB>60/min/ip`

を次の表に復元します。

| 誰が | 何を | いつ | どこで | なぜ | どのように |
|---|---|---|---|---|---|
| argo | limit | now | I/login | abuse | 60/min/ip |

関係は参照 `I/login`、変更 `F/auth`、依存 `T/design`、受け入れ条件 `cargo test` として表示します。

## データ型と短縮記法

型指定なしは文字列、`:n` は整数、`:b` は `0/1` の真偽値です。文字列内の Tab・改行・復帰・バックスラッシュは `\\t`、`\\n`、`\\r`、`\\\\` で表現します。先頭の空白は `\\s` です。`$code<TAB>literal` による辞書、`:GROUP<TAB>prefix` による ID 接頭辞の圧縮もあります。手入力より参照シリアライザーを推奨します。

## マルチ Agent 協働

領域ごとのパッチを並行して**準備**し、ストアでは期待リビジョンと Schema 指紋を使い原子的に競合を拒否します。異なる領域が同じ実ファイルを書き換える場合はファイル単位の確認も必要です。受け入れ行は実行を許可するものではありません。

## 推奨ワークフロー

IDE1.0 でファイルを開く → Schema から領域カードを表示 → 安定 ID を選ぶ → 編集 → `.npatch` を生成 → 検証 → 依存・ファイル競合を確認 → 原子的に保存 → 再表示。

完全仕様：`prototype/v0.3/SPEC.md`、テスト報告：`prototype/v0.3/REPORT.md`、参照テスト：`prototype/v0.3/test_nema2.py`。
