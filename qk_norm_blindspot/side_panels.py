"""Model A (BASS-II flame spread) and Model B (Saffire-I ridge position) for the dashboard side panel ONLY.

Neither model predicts detector performance; their outputs are never used to infer detection results and are
never placed in the evidence store. Model B runs in an isolated subprocess with its own pinned environment
(its learned correction was exported with scikit-learn 1.9.1, while Model C needs 1.6.1).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path
from functools import lru_cache

from . import paths
from .sources import sha256_file

NOT_DETECTION_EVIDENCE = "Side-panel context only: this model does not predict smoke-detector performance; no detection result is inferred from it."


def _reg(name: str) -> dict:
    return json.loads(paths.MODELS_REGISTRY.read_text())[name]


def verify(name: str) -> dict:
    reg = _reg(name)
    root = paths.ROOT / reg["local_dir"]
    manifest = root / reg["checksum_manifest"]
    got = sha256_file(manifest)
    if got != reg["checksum_manifest_sha256"]:
        raise RuntimeError(f"{name}: checksum manifest mismatch")
    adir = manifest.parent
    files = {}
    for fname, expected in json.loads(manifest.read_text()).items():
        p = adir / fname
        if not p.exists():
            files[fname] = "not_downloaded"
            continue
        ok = sha256_file(p) == expected
        files[fname] = "ok" if ok else "MISMATCH"
        if not ok:
            raise RuntimeError(f"{name}: checksum mismatch for {fname}")
    return {"repo": reg["repo"], "revision": reg["revision"], "files": files}


@lru_cache(maxsize=1)
def _model_a_module():
    reg = _reg("model_a")
    os.environ["MODEL_A_ARTIFACT_DIR"] = str(paths.ROOT / reg["local_dir"] / reg["artifact_dir"])
    spec = importlib.util.spec_from_file_location("model_a_inference", paths.MODEL_A_DIR / "model_a" / "inference.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def model_a_panel(request: dict | None = None) -> dict:
    v = verify("model_a")
    reg = _reg("model_a")
    req = request or json.loads((paths.ROOT / reg["local_dir"] / reg["artifact_dir"] / "sample_request.json").read_text())
    out = _model_a_module().predict_model_a(req)
    return {"model": "model_a", "repo": reg["repo"], "revision": reg["revision"], "verified": v,
            "request": req, "response": out, "value_kind": out["value_kind"], "role": reg["role"],
            "note": NOT_DETECTION_EVIDENCE,
            "card_limitations": [
                "18 physical samples / 39 airflow segments; nested CV R^2 negative; exploratory only.",
                "No calibrated uncertainty; no generalisation to other materials, gravity levels or geometries."]}


_B_RUNNER = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from importlib.metadata import version
for package, expected in {'numpy':'2.5.4', 'scikit-learn':'1.9.1', 'joblib':'1.6.0', 'pillow':'13.0.0'}.items():
    if version(package) != expected:
        raise RuntimeError(f'{package}: expected {expected}, got {version(package)}')
from saffire_b.inference import predict_model_b
req = json.loads(sys.argv[2])
print(json.dumps(predict_model_b(req, artifact_dir=sys.argv[3])))
"""


def model_b_panel(frame: str = "data/frames/Mapped_S1C1-1465937331457.jpeg", timeout: int = 600) -> dict:
    v = verify("model_b")
    reg = _reg("model_b")
    root = paths.ROOT / reg["local_dir"]
    req = {"frame_path": str(root / frame), "camera_id": "C1", "image_mapping": "NASA_mapped", "material": "SIBAL",
           "units": "mm", "timestamp_ms": int(frame.rsplit("-", 1)[1].split(".")[0])}
    interpreter = Path(os.environ.get("MODEL_B_PYTHON", str(paths.ROOT / ".venv-model-b/bin/python")))
    if interpreter.exists():
        cmd = [str(interpreter)]
    else:
        cmd = ["uv", "run", "--no-project", "--quiet", "--python", "3.12"]
        for pkg in reg["isolated_env"]:
            cmd += ["--with", pkg]
        cmd += ["python"]
    cmd += ["-I", "-c", _B_RUNNER, str(root), json.dumps(req), str(root / reg["artifact_dir"])]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        return {"model": "model_b", "status": "FAILED", "stderr": proc.stderr[-2000:], "verified": v, "note": NOT_DETECTION_EVIDENCE}
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    return {"model": "model_b", "repo": reg["repo"], "revision": reg["revision"], "verified": v, "request": req,
            "response": out, "value_kind": out.get("value_kind"), "role": reg["role"], "isolated_env": reg["isolated_env"],
            "note": NOT_DETECTION_EVIDENCE,
            "card_limitations": [
                "Held-out MAE 4.829 mm vs simple threshold baseline 4.545 mm: the learned correction did not improve on the baseline.",
                "Single task, single sample; labels are agent annotations, not human."]}
