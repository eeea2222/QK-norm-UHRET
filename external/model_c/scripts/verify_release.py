"""Verify a Hub-downloaded release, then infer using only its exported module."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
root = Path(args.path).resolve()
manifest = json.loads((root / "release_checksums.json").read_text())
for name, expected in manifest.items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"Checksum mismatch: {name}")
os.environ["MODEL_C_ARTIFACT"] = str(root / "artifacts/model_c")
spec = importlib.util.spec_from_file_location("standalone", root / "artifacts/model_c/inference.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sample = json.loads((root / "reports/sample_inference.json").read_text())
result = module.predict_model_c(sample["request"])
assert result == sample["response"]
print(json.dumps({"verified_files": len(manifest), "standalone_inference": result, "status": "TESTED_LOCALLY"}, indent=2))
