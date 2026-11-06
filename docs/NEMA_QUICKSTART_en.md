# NEMA v1.4 · English quick guide

**Table is the default mode.** A domain header begins with one literal Tab, for example `\tT1 1`. The first body line becomes **column headings only if it begins with backslash + ASCII space (`\ `)**. Otherwise the first row is data, and missing column names are automatically `column1`, `column2`, … `columnN`.

```text
⇥T1 1
\ Agent State Note
Claude Ready CheckSession
   AccessGranted
```

The symbol `⇥` above illustrates a **real Tab**. The body uses **single ASCII spaces** between columns. N leading spaces continue the previous record in column X(N−1), so three leading spaces continue the third column. New top-level lines add table records. Every `.nema` file ends with exactly two empty physical lines.

Other domain modes: `\t?T1 1` for What→Why→How→Who→When→Where, and `\t>G1 1` for Node–Edge graphs. `A>X>B` is A→B with edge ID X; `A<X<B` is B→A with edge ID X. Edge descriptions can continue vertically. An isolated trailing ` .` means the remaining 5W1H fields are explicitly empty.

A document-initial `\t$N` declares N opaque dictionary entries, indexed from zero. `Validate^0BeforeAccess` can preserve `APIKey` as one atom while other English words follow PascalCase splitting. Chinese and Japanese normally remain connected. `\^` escapes a literal caret. The separate `.nemat` transport enables lossless dictionary / numeric prefix / RLE compression; it must be decoded based on its known media type, **not guessed from its content**.

A model may learn to emit compressed text, but tokenizer cost and generation reliability require model-specific tests. The bundled SentencePiece benchmarks are only local reference results. Source code itself belongs in `.rs`/`.ts`/`.py` etc., not rewritten into NEMA.

Full normative text: `NEMA_SPEC_v1.4_zh.md`.
