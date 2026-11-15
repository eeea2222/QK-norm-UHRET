---
base_model: RikiyaT/Qwen3.5-0.8B-weight-space-programming
license: apache-2.0
tags:
- weight-space-programming
- safetensors
- qwen3_5
---
# WeightSeek WT4

WT4 is a completed WeightSeek release built on Qwen3.5-0.8B weight-space-programming (p50c). It applies a hand-written weight edit to 13 reflection-token embedding rows, with a bias strength of 4, to reduce repeated reflection during reasoning. No training or gradient updates are used.

This repository contains only the WT4 variant, distributed as a compact `patch.safetensors` row patch. It requires the [p50c base model](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming) at revision `d1671a178705bcab7644806d23c535517f35723b`; the patch is not a standalone checkpoint. `wt4.json` records the exact file hashes.

To apply the patch, load the base weight tensors and the patch with `safetensors.torch.load_file`. Replace the base embedding rows indexed by `model.language_model.embed_tokens.weight::rows` with the values in `model.language_model.embed_tokens.weight::vals`. These are replacement values, not additive deltas. Preserve tied input/output embeddings when loading the resulting model.

## Disclaimer

The model and associated files are provided "AS IS", without warranties of any kind, express or implied, including merchantability, fitness for a particular purpose, and non-infringement. Outputs may be inaccurate, biased, or inappropriate and should be independently verified. Users are responsible for their use of the model, its outputs, and compliance with applicable laws. To the maximum extent permitted by law, the authors and contributors shall not be liable for any claims, losses, or damages arising from use of the model or its outputs. Nothing in this notice excludes liability that cannot lawfully be excluded or modifies the applicable license terms.

## License and availability

The WT4 weight patch, metadata, and original documentation are released under
the **Apache License, Version 2.0**. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
The patch is provided in editable Safetensors format; the application procedure
is documented above. It requires the separately available Apache-2.0 upstream
base model at the pinned revision. The source research reference is recorded
in `wt4.json`; this release does not include the research repository.
