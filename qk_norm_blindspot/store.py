"""Loads the built JSON deliverables (outputs/) into one citable store."""
from __future__ import annotations

import json
from functools import lru_cache

from . import paths


class EvidenceStore:
    def __init__(self, outputs_dir=None):
        d = outputs_dir or paths.OUTPUTS
        self.records = json.loads((d / "evidence_records.json").read_text())["records"]
        self.gaps = json.loads((d / "research_gaps.json").read_text())["gaps"]
        self.priorities = json.loads((d / "research_priorities.json").read_text())["priorities"]
        comp = json.loads((d / "scientific_comparisons.json").read_text())
        self.comparisons = comp["comparisons"]
        self.chronology = comp["chronology"]
        self.profiles = json.loads((d / "investigation_profiles.json").read_text())["profiles"]
        self.by_id: dict[str, dict] = {}
        for r in self.records:
            self.by_id[r["evidence_id"]] = r
        for g in self.gaps:
            self.by_id[g["gap_id"]] = g
        for c in self.comparisons:
            self.by_id[c["comparison_id"]] = c
        for p in self.priorities:
            self.by_id[p["priority_id"]] = p

    def get(self, i: str) -> dict | None:
        return self.by_id.get(i)

    @property
    def tested_materials(self) -> set[str]:
        mats: set[str] = set()
        for p in self.profiles:
            if p.get("smoke_detectors_evaluated"):
                mats |= {m.lower() for m in p.get("materials_tested", [])}
        return mats


@lru_cache(maxsize=1)
def get_store() -> EvidenceStore:
    return EvidenceStore()
