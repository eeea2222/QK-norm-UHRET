"""WeightSeek-WT4 loader and text generator.

WT4 = RikiyaT/Qwen3.5-0.8B-weight-space-programming @ d1671a17... with 13 embedding rows REPLACED
(not added) by the rows in efe-T/WeightSeek-WT4 patch.safetensors. Tied input/output embeddings are kept.
Every file is checked against the pinned hashes in models.json / wt4.json before use. If any check
fails, loading raises - there is no silent fallback to another model.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from functools import lru_cache
from pathlib import Path

from . import paths
from .sources import sha256_file

ROWS_KEY = "model.language_model.embed_tokens.weight::rows"
VALS_KEY = "model.language_model.embed_tokens.weight::vals"


class WT4VerificationError(RuntimeError):
    pass


def _registry() -> dict:
    return json.loads(paths.MODELS_REGISTRY.read_text())["wt4"]


def base_dir() -> Path:
    return Path(os.environ.get("WT4_BASE_DIR", paths.ROOT / _registry()["base_local_dir"]))


def _tensor_hashes(t) -> dict:
    """Two candidate definitions of a tensor hash (the WT4 release does not document which one it used)."""
    import torch
    from safetensors.torch import save as st_save

    raw = t.detach().cpu().contiguous()
    as_int = raw.view(torch.int16) if raw.dtype == torch.bfloat16 else raw
    return {
        "raw_row_major_bytes": hashlib.sha256(as_int.numpy().tobytes()).hexdigest(),
        "safetensors_single_tensor": hashlib.sha256(st_save({_registry()["tensor"]: raw})).hexdigest(),
    }


def verify_wt4_files(check_base_weights: bool = True) -> dict:
    """Verify patch, wt4.json and (optionally) base weights. Returns a report; raises on mismatch."""
    reg = _registry()
    wt4_dir = paths.ROOT / reg["local_dir"]
    report: dict = {"repo": reg["repo"], "revision": reg["revision"], "base_repo": reg["base_repo"],
                    "base_revision": reg["base_revision"], "checks": {}}

    meta_path, patch_path = wt4_dir / "wt4.json", wt4_dir / "patch.safetensors"
    for name, p, expected in (("wt4.json", meta_path, reg["wt4_json_sha256"]), ("patch.safetensors", patch_path, reg["patch_sha256"])):
        if not p.exists():
            raise WT4VerificationError(f"missing {p}")
        got = sha256_file(p)
        report["checks"][name] = {"sha256": got, "expected": expected, "ok": got == expected}
        if got != expected:
            raise WT4VerificationError(f"{name} sha256 mismatch: {got} != {expected}")
    meta = json.loads(meta_path.read_text())
    for key in ("base_model", "base_revision", "patch_sha256", "base_weight_sha256", "edited_embedding_sha256", "changed_rows"):
        want = {"base_model": reg["base_repo"]}.get(key, reg.get(key))
        ok = meta.get(key) == want
        report["checks"][f"wt4.json:{key}"] = {"value": meta.get(key), "expected": want, "ok": ok}
        if not ok:
            raise WT4VerificationError(f"wt4.json field {key} = {meta.get(key)} != pinned {want}")

    weights = base_dir() / reg["base_weight_file"]
    if check_base_weights:
        if not weights.exists():
            raise WT4VerificationError(f"base weights not found at {weights} (run external/wt4_base/fetch_weights.sh)")
        got = sha256_file(weights)
        report["checks"]["base_weights"] = {"sha256": got, "expected": reg["base_weight_sha256"], "ok": got == reg["base_weight_sha256"]}
        if got != reg["base_weight_sha256"]:
            raise WT4VerificationError("base weight sha256 mismatch")
    return report


def build_edited_embedding():
    """Apply the row-replacement patch to the base embedding tensor (read straight from safetensors)."""
    import torch
    from safetensors import safe_open
    from safetensors.torch import load_file

    reg = _registry()
    patch = load_file(str(paths.ROOT / reg["local_dir"] / "patch.safetensors"))
    rows, vals = patch[ROWS_KEY], patch[VALS_KEY]
    if rows.numel() != reg["changed_rows"] or vals.shape[0] != rows.numel():
        raise WT4VerificationError("patch shape does not match the documented 13 rows")
    with safe_open(str(base_dir() / reg["base_weight_file"]), framework="pt") as f:
        base = f.get_tensor(reg["tensor"])
    if vals.dtype != base.dtype or vals.shape[1] != base.shape[1]:
        raise WT4VerificationError("patch dtype/width does not match the base embedding")
    edited = base.clone()
    edited[rows] = vals  # replacement, not addition
    return base, edited, rows


class WT4:
    def __init__(self, device: str | None = None, dtype: str = "bfloat16", verify: bool = True, apply_patch: bool = True):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        torch.set_num_threads(int(os.environ.get("QKNORM_TORCH_THREADS", "4")))
        t0 = time.time()
        self.report = verify_wt4_files(check_base_weights=verify) if verify else {"checks": "skipped"}
        reg = _registry()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        torch_dtype = getattr(torch, dtype)
        bdir = base_dir()
        self.tokenizer = AutoTokenizer.from_pretrained(str(bdir))
        self.model = AutoModelForCausalLM.from_pretrained(str(bdir), dtype=torch_dtype)
        self.model.eval()
        self.apply_patch = apply_patch
        emb = self.model.get_input_embeddings().weight
        out = self.model.get_output_embeddings().weight
        if apply_patch:
            base, edited, rows = build_edited_embedding()
            hashes = _tensor_hashes(edited)
            match = [k for k, h in hashes.items() if h == reg["edited_embedding_sha256"]]
            if not match:
                raise WT4VerificationError("edited embedding checksum mismatch")
            self.report["edited_embedding"] = {"expected": reg["edited_embedding_sha256"], "computed": hashes, "matched_definition": match or None}
            if not torch.equal(emb.detach().cpu().to(base.dtype), base):
                raise WT4VerificationError("loaded base embedding differs from the safetensors tensor")
            with torch.no_grad():
                emb.copy_(edited.to(emb.dtype))
            if not torch.equal(emb.detach().cpu().to(edited.dtype)[rows], edited[rows]):
                raise WT4VerificationError("patch rows were not applied")
            self.report["changed_rows"] = rows.tolist()
            self._rows, self._base_rows, self._patched_rows = rows, base[rows].clone(), edited[rows].clone()
        tied = emb.data_ptr() == out.data_ptr()
        self.report["tied_embeddings_preserved"] = tied
        if not tied:
            raise WT4VerificationError("input/output embeddings are not tied after loading")
        self.model.to(self.device)
        self.report["device"], self.report["dtype"], self.report["load_seconds"] = self.device, dtype, round(time.time() - t0, 1)
        self.report["variant"] = "WT4 (patched)" if apply_patch else "unpatched base (comparison only)"

    def set_variant(self, patched: bool) -> None:
        """Swap the 13 rows in place between WT4 values and the unpatched base values (for the P2 comparison only)."""
        import torch

        emb = self.model.get_input_embeddings().weight
        src = self._patched_rows if patched else self._base_rows
        with torch.no_grad():
            emb[self._rows.to(emb.device)] = src.to(emb.device, emb.dtype)
        self.report["variant"] = "WT4 (patched)" if patched else "unpatched base (comparison only)"

    def generate(self, system: str, user: str, prefill: str = "", max_new_tokens: int = 400) -> dict:
        import torch

        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        prompt = self.tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        prompt += prefill
        enc = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        t0 = time.time()
        with torch.no_grad():
            out = self.model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                                      repetition_penalty=1.05, pad_token_id=self.tokenizer.eos_token_id)
        new = out[0, enc["input_ids"].shape[1]:]
        text = self.tokenizer.decode(new, skip_special_tokens=True)
        return {"text": prefill + text, "new_tokens": int(new.numel()), "seconds": round(time.time() - t0, 2),
                "prompt_tokens": int(enc["input_ids"].shape[1])}


@lru_cache(maxsize=2)
def get_wt4(apply_patch: bool = True) -> WT4:
    return WT4(apply_patch=apply_patch)
