# NEMA / `.nema` — experimental 2D Agent work-domain format (NEMA/2)

Ariadne's thread / 阿里阿德涅的线团. The **primary reader is an AI**; IDE1.0 is the intended renderer.

One **zero-indentation block** represents one stable, independently addressable Agent work domain. No line-number-based addressing.

## Directories

- `SPEC.md`: normative syntax draft, semantics, delimiters, domain/version model.
- `sample.nema`, `sample.npatch`: complete samples; patch applies to domain `T/a7`.
- `nema2_codec.py`: deterministic UTF-8 reference encoder, parser and auto-mode selector.
- `nema2_patch.py`: positional CAS patches bound to complete Schema SHA-256.
- `nema2_scheduler.py`: preliminary read/write/dependency scheduling checks.
- `i_codec.py`, `i_store.py`, `nema_codec.py`, `bench.py`: comparison/SQLite reference code from validated predecessor.
- `test_nema2.py`, `red_v2.log`, `green_v2.log`: adversarial red/green tests.
- `benchmark_v2.py`, `benchmark_v2.json`, `REPORT.md`: reproducible same-data measurements.

## Run

```sh
python -m unittest -v test_nema2
python benchmark_v2.py
```

Benchmark requires `PyYAML`; the NEMA parser/writer itself has no third-party dependencies.

`NEMA/2` is an **experimental grammar**, not production-safe for untrusted deployments. Optimistic domain CAS is implemented in the reference SQLite store. Integration with actual worktrees, file-hash CAS and IDE1.0 rendering remains future work.
