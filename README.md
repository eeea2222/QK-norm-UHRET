# QK norm — BlindSpot Explorer

Working Python module, local API, and self-contained dashboard. **RAG was removed by request. Scientific validation was deferred by request.** Existing data and audit labels are preserved; a passing software test does not validate a scientific claim.

## Run now (existing workspace)

```bash
cd /home/efeai/Desktop/NasaSpaceApps
.venv/bin/python -m uvicorn qk_norm_blindspot.api:app --host 127.0.0.1 --port 8005
```

Open http://127.0.0.1:8005/ for the dashboard and http://127.0.0.1:8005/docs for interactive API documentation. The dashboard also opens directly from `dashboard/index.html`; its data is inlined. Regenerate it with `.venv/bin/python -m qk_norm_blindspot dashboard` after catalog changes.

## Python and JSON

```python
from qk_norm_blindspot import analyze_blindspots, export_findings
response = analyze_blindspots(
    "Show the Teflon catalog",
    filters={"material": "Teflon"},
)
assert response["rag_enabled"] is False
export_findings()
```

The question labels the request and selects a template topic. **Record selection uses explicit filters only**, with fixed evidence-ID ordering. It does not search, rank, embed or use WT4 to answer the question. Supported filters: `material`, `investigation`, `classification`, `finding_type`, `doc_id`, `year_range`. Each accepts a string/list except `year_range`, which is an ascending pair of integers. `catalog_records` contains all matching records, including unresolved audit labels. `verified_findings` retains the catalog's pre-existing classification. Empty explicit selections return `NO_EVIDENCE`.

The optional `model_c_input` filter accepts the exact material, five controls and units required by the pinned Model C. Its output carries `predicted`, OOD and nearest measured experiment fields. See `examples/model_c_request.json`.

```bash
curl -s http://127.0.0.1:8005/blindspots -H 'Content-Type: application/json' \
  -d '{"question":"Show the Teflon catalog","filters":{"material":"Teflon"}}'
.venv/bin/python -m qk_norm_blindspot ask 'Show catalog' --filters '{"material":"Teflon"}'
.venv/bin/python -m qk_norm_blindspot export
.venv/bin/python -m qk_norm_blindspot eval
```

## Endpoints

| Route | Use |
|---|---|
| `GET /` | Dashboard |
| `GET /health` | Engine and deferred-validation status |
| `GET /catalog` | Existing records, gaps, priorities, profiles |
| `GET /schema` | JSON input/output schemas |
| `POST /blindspots` | Structured catalog and deterministic template response |
| `POST /models/a` | BASS-II flame-spread prediction; request matches published Model A sample |
| `GET /models/b/sample` | Real Saffire-I sample frame measurement |
| `POST /models/c` | Similar-condition threshold prediction |
| `POST /models/wt4/generate` | Standalone WT4 text generation, **no catalog or source retrieval** |

WT4 request: `{"prompt":"Say hello.","max_new_tokens":12}`. It loads lazily; generation is serialized to protect CPU memory. Tokens are bounded to 1–512, input to 6000 characters. This endpoint returns raw model text labelled `predicted` and `use_as_evidence: false`. It does not provide scientific verification. The legacy `use_llm` argument on `/blindspots` is accepted for compatibility and never enables RAG.

## Models and environment

All artifacts stay unchanged. No model was trained or substituted. Exact commits and pinned SHA-256 values are in `qk_norm_blindspot/models.json`; actual verification results are in `outputs/model_verification.json`. WT4 applies the released 13 embedding-row replacements and verifies the resulting embedding hash and tied weights.

| Model | Pinned revision |
|---|---|
| A | `0096ac5a4959c13e0f7d1561160844db5f873ba3` |
| B | `7ca05303bf350d300f98011528cb4e1c4d28b612` |
| C | `91292a40886564d146dc9e9d496b74c2aefaab5c` |
| WT4 patch | `005427a78998cf293ffd54ac8e4da16bc089f00a` |
| WT4 base | `d1671a178705bcab7644806d23c535517f35723b` |

Python 3.12. Main dependencies are pinned in `pyproject.toml`. The existing `.venv` uses CPU torch 2.15.0+cpu. A fresh environment can be prepared with `uv venv --python 3.12 .venv`, then `uv pip install --python .venv/bin/python torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu`, then `uv pip install --python .venv/bin/python -e '.[dev]'`.

Model B uses a separate environment because its sklearn version differs from Model C. The existing `.venv-model-b` link points to the previously installed uv environment on this machine. On another machine, create `.venv-model-b` with Python 3.12 and install `numpy==2.5.4 scikit-learn==1.9.1 joblib==1.6.0 pillow==13.0.0`. Alternatively set `MODEL_B_PYTHON` to its interpreter. Versions are checked in the subprocess. If no interpreter exists, the wrapper uses `uv run` with those exact pins.

`QKNORM_ROOT` can point to another project data root; `WT4_BASE_DIR` overrides the base-checkpoint directory; `QKNORM_TORCH_THREADS` defaults to 4. The installed Python package still requires the external artifacts and outputs directory. The model fetch script is `external/wt4_base/fetch_weights.sh`; the remaining models and source artifacts are already present in this workspace.

## Checks and limitations

- `outputs/eval_results.json`: actual software tests, expected/actual outcomes, failures and stdout. Scientific tests 1–15 are explicitly deferred.
- `outputs/wt4_smoke.json`: real checkpoint loading, checksum checks, tied embeddings and actual generation.
- `outputs/http_smoke.json`: real local HTTP checks, including standalone WT4.
- `outputs/all_findings.json`: dashboard-consumable export of the current catalog.
- `dashboard/dashboard_data.json`: dashboard payload including Model A/B outputs and measured-only Model C summary.

The offline `build` command and source extraction files remain available for future scientific work, but this software-only finish did not run new scientific validation or promote unfinished source audits. Research priorities and gap records are inherited provisional content. Template integrity checks validate IDs and numeric consistency; they do not prove a claim's meaning or scientific correctness.

Model A is exploratory (negative nested CV R²; 18 samples/39 airflow segments). Model B's learned correction did not beat its simple baseline (MAE 4.829 vs 4.545 mm). Model C predicts a derived 2.0 V label and has weak Kapton/Teflon recall; its output is never evidence. WT4 is a small model and can invent claims. All outputs support research discussion; they provide no operational alarm settings or safety certification.

Source data, model artifacts and publications retain their own licenses and notices, preserved under `external/`. QK norm is a project name, unrelated to transformer QK normalization.

## Interactive 3D support

The dashboard includes three Blender-created teaching models: cabin smoke transport, an optical-detector cutaway, and a smoke-aging measurement chain. Drag each canvas to orbit, scroll to zoom, or use keyboard arrows and +/-; Reset view restores the default angle. Meshes are embedded in the dashboard so the viewer works offline without a CDN. Models use arbitrary scale and illustrative particle markers, not measured flow trajectories, exact NASA hardware geometry or CFD.

Editable scenes: `dashboard/assets/3d/qk_norm_concept_models.blend`. Individual `.glb`, mesh `.json`, and preview `.png` files are alongside it. `scripts/build_3d.py` reproduces the assets in Blender. The live Blender MCP connection was used to build, export, render and inspect the models. Existing Blender scenes were preserved.

## Model benchmark table

Open `/?benchmark=1#benchmarks`. QK norm rows have purple outlines; best scores and declared ties use dark bold text. `outputs/benchmarks.json` contains exact recorded values, metric directions, fold variability, source hashes and related-work links. `qk_norm_blindspot/benchmarks.py` builds the table without retraining.

Model A's fixed random forest has the lowest recorded candidate MAE and 12.4% lower MAE than the median of all six recorded alternatives. This retrospective candidate comparison does not supersede the negative-R² nested-selection result. Model B loses to its simple binary-median baseline. Model C ties its material-only baseline under the released evaluation rule. WT4 remains unranked because a matched quality evaluation was not run. The median is a summary statistic, not an invented competitor model or an estimate of the field's average performance.

Related papers were searched on 2026-11-15 and appear separately because their datasets, targets and metrics do not match ours. No external superiority claim is made. Existing scientific validation remains deferred; the table displays historical evaluations with their limitations.

## Dashboard AI playground

Open `/?ai=1#ai-test`. Select Model A, B, C or WT4, choose a ready-made trial, edit its inputs and press **Modeli çalıştır**. The panel calls the real model endpoints and shows a readable result plus expandable JSON. Presets include the published Model A sample, an edited airflow example, a real Model B frame, recorded Kapton/Teflon/Silicone conditions, a Model C OOD example and two WT4 prompts. Recorded conditions remain distinct from new predictions. Local-file viewing displays the catalog; inference requires the running HTTP API.

`scripts/test_playground.cjs` exercised all four model controls through Chrome against the actual local server. Results are saved to `outputs/ai_playground_tests.json` and a screenshot to `outputs/ai_playground.png`.

## CLI ile hızlı model denemesi

Hazır örnekleri listeler, tek model çalıştırır veya bir girdiyi değiştirerek sonuçları karşılaştırır.
Her denemede sabit model ağırlıkları ve mevcut checksum kontrolleri kullanılır.
JSON çıktısı girdileri, model sürümünü, kapsam dışı uyarılarını ve sonucu taşır.
Denemeler hesaplamalı model sorgularıdır.

```bash
.venv/bin/python -m qk_norm_blindspot experiment list
.venv/bin/python -m qk_norm_blindspot experiment run c --preset 1 --output sonuc_c.json
.venv/bin/python -m qk_norm_blindspot experiment sweep a --field velocity_cm_s --values 6,8,9 --output sonuc_a.json
.venv/bin/python -m qk_norm_blindspot experiment run a --set thickness_mm=1.5
```

A/B/C/WT4 tek çalıştırmayı destekler. A ve C sayısal girdi taramasını destekler.
Bir koşu hata verirse önceki tamamlanan koşular korunur, durum PARTIAL/FAILED olur ve çıkış kodu 1 döner.

## AI model bağlantıları

- [Model A - BASS-II PMMA alev yayılma hızı](https://huggingface.co/efe-T/nasa-bass-ii-model-a)
- [Model B - Saffire-I görüntüden sırt konumu](https://huggingface.co/efe-T/nasa-saffire-i-model-b)
- [Model C - SAME/SAME-R 2,0 V eşik sınıflandırması](https://huggingface.co/efe-T/nasa-same-model-c)
- [WeightSeek-WT4 - dil modeli yaması](https://huggingface.co/efe-T/WeightSeek-WT4)
- [WT4 taban modeli](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming)

Sabit revizyonlar ve checksum kayıtları qk_norm_blindspot/models.json dosyasındadır.
Büyük taban ağırlıklarını edinmek için external/wt4_base/fetch_weights.sh kullanılır.
