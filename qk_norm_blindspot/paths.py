"""Filesystem layout. Override the project root with QKNORM_ROOT."""
from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("QKNORM_ROOT", PACKAGE_DIR.parent)).resolve()

SOURCES = ROOT / "sources"
RAW_DIR = SOURCES / "raw"
TEXT_DIR = SOURCES / "text"
EXTRACTED_DIR = SOURCES / "extracted"

CURATION_DIR = PACKAGE_DIR / "curation"
MODELS_REGISTRY = PACKAGE_DIR / "models.json"

OUTPUTS = ROOT / "outputs"
EXAMPLES = ROOT / "examples"
DASHBOARD_DIR = ROOT / "dashboard"

EXTERNAL = ROOT / "external"
MODEL_A_DIR = EXTERNAL / "model_a"
MODEL_B_DIR = EXTERNAL / "model_b"
MODEL_C_DIR = EXTERNAL / "model_c"
WT4_DIR = EXTERNAL / "wt4"
WT4_BASE_DIR = EXTERNAL / "wt4_base"


def rel(path: Path) -> str:
    """Path relative to the project root (for manifests)."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)
