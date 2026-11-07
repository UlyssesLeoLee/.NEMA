# .NEMA v1.2 · 最新 Token 基准（2026-11-07）

**这里是真实运行的本地 SentencePiece BPE / Unigram 分词器计数，不是任何商业 LLM 官方 Token 数，也没有计入提示词、返工及模型输出成本。**

## BPE 对照

| 场景 | 原生 `.nema` | 无损 `.nemat` | JSON 对象 | 位置式 JSON | 位置式 YAML | 原生 vs 位置式 JSON |
|---|---:|---:|---:|---:|---:|---:|
| english_60 | 3012 | 1953 | 6502 | 3851 | 3969 | +21.79% |
| chinese_60 | 5532 | 3647 | 8662 | 6011 | 6129 | +7.97% |
| japanese_60 | 7062 | 4088 | 10192 | 7541 | 7659 | +6.35% |
| table_200 | 4899 | 2105 | 7920 | 5890 | 5890 | +16.83% |
| graph_40n_160e | 6952 | 3265 | 13778 | 7551 | 7551 | +7.93% |
| high_entropy_60 | 6358 | 6181 | 9878 | 7228 | 7346 | +12.04% |
| short_what | 16 | 16 | 73 | 29 | 29 | +44.83% |
| graph_3n_4e | 144 | 144 | 417 | 205 | 205 | +29.76% |

## Graph 语法局部优化

- 旧写法 `A \=LoginAPI Authentication`（无 Node 行首标记）：53 本地 BPE Token，97 UTF-8 字节。
- 新写法 ` A LoginAPI Authentication`（一个行首 ASCII 空格）：45 本地 BPE Token，95 UTF-8 字节。
- 在这个 **2 Node + 1 Edge 的短对照**中节省 **15.09% 本地 BPE**（旧 53 → 新 45）。**局部优化不能推广为任意 Graph 的固定节省率**。

## 计量方法

- 数据集与成本算法均见 `bench/reproduce_v12.py`；输入文件是 `examples/*.nema`，对照文件是 `examples/*.json`, `*.positional.json`, `*.positional.yaml`，压缩候选是 `examples/*.nemat`。
- 对每个数据集从 `.NEMA` 解析出的领域 ID、修订、字段、表头、Node/Edge ID 和关系方向生成等价的 JSON。JSON 对象基准包含显式字段名；位置式 JSON 是人为共用 schema 的强对照，通常比对象 JSON 更短。
- `.nemat` 编码器需要满足 decode(x)==源 `.nema` UTF-8 的逐字节一致校验，不在高熵低收益样本上强行插入字典。
- 英中日各 60 个领域、Table 200 行、Graph 40 Node + 160 Edge、高熵随机领域 60 个、极短单 What 和小 Graph。每个场景均保留负收益或微弱收益，禁止只取最好一组做宣传。
- 原始 JSON 与 CSV 记录两种 tokenizer 的每个计数，网站 Token Lab 由该 JSON 自动生成静态数据副本。
- 新版 3D 装饰只改变 UI，不改变 `.nema` / `.nemat` 的 Token 成本；在线通过 pinned Three.js MIT 包加载，离线静态回退。

## 解释与边界

**压缩效益的主要来源是去掉重复键、复用领域 ID 和字典，以及更紧凑的空间语法，而不只是空格比 Tab 短。** 位置式 JSON 是强对照，本地 BPE 下 Graph 40/160 的原生 `.nema` 只比它少约 7.9%，不能混淆成相对对象 JSON 的大幅节省。

真实 API 的评估需要增加：模型理解语法的系统提示成本、返工/重试、输出 Token、实际模型 tokenizer、学习训练成本及不同上下文大小的重复性。
