"""Verify all four models at their pinned revisions (no model is retrained or replaced)."""
from __future__ import annotations

import json

from . import paths


def verify_all(check_base_weights: bool = True) -> dict:
    from . import model_c, side_panels, wt4

    out = {}
    for name, fn in (("model_a", lambda: side_panels.verify("model_a")), ("model_b", lambda: side_panels.verify("model_b")),
                     ("model_c", model_c.verify_model_c), ("wt4", lambda: wt4.verify_wt4_files(check_base_weights))):
        try:
            out[name] = {"status": "OK", "report": fn()}
        except Exception as e:  # report failures; never switch models silently
            out[name] = {"status": "FAILED", "error": f"{type(e).__name__}: {e}"}
    (paths.OUTPUTS / "model_verification.json").write_text(json.dumps(out, indent=2) + "\n")
    return out
