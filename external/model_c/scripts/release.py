"""Assemble a small, checksummed release without caches or credentials."""
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
dest = root / "release"
if dest.exists():
    shutil.rmtree(dest)
dest.mkdir()
for name in ["model_c", "tests", "notebooks", "artifacts", "reports", "research_notes", "data", "scripts", "logs"]:
    shutil.copytree(root / name, dest / name, ignore=shutil.ignore_patterns("__pycache__", "*.partial", ".pytest_cache", "storage_*"))
for name in ["README.md", "MODEL_CARD.md", "LICENSE", "NOTICE", "requirements.txt", "requirements-lock-local.txt", "pytest.ini", "STATUS.json"]:
    if (root / name).exists():
        shutil.copy2(root / name, dest / name)
checksums = {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob("*")) if p.is_file()}
(dest / "release_checksums.json").write_text(json.dumps(checksums, indent=2))
print(json.dumps({"release_files": len(checksums), "bytes": sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())}))
