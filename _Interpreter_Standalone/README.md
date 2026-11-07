# .NEMA Interpreter v1.2 — reference implementation

Unzip and run commands from this directory. Python 3.10+ standard library for parse/render/encode/decode; optional `sentencepiece` only for local BPE/Unigram cost selection.

```powershell
python -m codec.cli render examples/complete_v12.nema
python -m codec.cli encode examples/graph_3n_4e.nema --output graph.nemat
python -m codec.cli decode graph.nemat --output roundtrip.nema
python -m codec.cli inspect examples/graph_3n_4e.nema
```

`--cost bpe`/`--cost unigram` require `pip install sentencepiece`. These bundled tokenizer models are locally trained reference models, NOT model provider tokenizers. Graph v1.2 Node = a single leading ASCII space; Edge = no leading space; the native and wire encodings are different. This is source code, not a Windows .exe or installed IDE/IME plugin.
