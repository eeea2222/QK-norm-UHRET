"""Pinned PSI acquisition and conservative, traceable workbook preprocessing."""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
import requests

from .inference import FEATURES

WORKBOOK = "PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx"
WORKBOOK_SHA = "6d3a539ccf425b1fa8edc19cc75d828f57d650c7ce734d4e7aa686fea9593218"
SOURCES = [
    ("PSI-101", WORKBOOK, WORKBOOK_SHA),
    ("PSI-102", "PSI-102_Experimental table_SAME.csv", "268d1e121d2f211b124407dd32b9475617bd269ede2c2d1749441da3e949a2af"),
    ("PSI-101", "PSI-101_Experimental table_SAME-R.csv", "87164b7dc9168a4273c159f7a9f23699afbd06ad97b77974377e79b9bf8a3bef"),
    ("PSI-102", "PSI-102_Reports_SAME_Final Science Report.pdf", "af91c96d22d93bbefbc0f2c5e1cc06e24813f532e5379b3fec9f121cccb22193"),
    ("PSI-101", "PSI-101_Reports_SAME-R_Final Report.pdf", "65381e2715eb7379113dd1b9c550baaa5fa5a247dba00419123143aa98ef80d6"),
]
MATERIALS = ["Kapton", "Lampwick", "Pyrell", "Silicone", "Teflon"]
MAP = {"N": "airflow_cm_s", "O": "resistance_ratio", "P": "heating_s", "Q": "aging_s", "R": "mixing_s"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def acquire(root="."):
    root = Path(root)
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    sources = []
    for study in ["PSI-102", "PSI-101"]:
        url = f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{study}"
        dest = raw / f"{study}-metadata.json"
        if not dest.exists():
            response = session.get(url, timeout=120)
            response.raise_for_status()
            dest.write_bytes(response.content)
        sources.append({"study": study, "url": url, "path": str(dest.relative_to(root)), "sha256": sha(dest), "kind": "source_metadata"})
    for study, filename, checksum in SOURCES:
        dest = raw / filename
        url = f"https://psi.nasa.gov/geode-py/ws/studies/{study}/download"
        if not dest.exists():
            response = session.get(url, params={"file": filename, "version": 4, "redirect": "false"}, timeout=180)
            response.raise_for_status()
            signed_url = response.text.strip().strip('"')
            if not signed_url.startswith("https://"):
                raise RuntimeError("Unexpected PSI file resolver response")
            # Never persist signed URL credentials in the manifest or logs.
            payload = session.get(signed_url, timeout=300)
            payload.raise_for_status()
            temporary = dest.with_suffix(dest.suffix + ".partial")
            temporary.write_bytes(payload.content)
            if sha(temporary) != checksum:
                temporary.unlink()
                raise ValueError(f"Pinned PSI checksum mismatch: {filename}")
            temporary.replace(dest)
        if sha(dest) != checksum:
            raise ValueError(f"Pinned PSI checksum mismatch: {filename}")
        sources.append({"study": study, "url": url, "parameters": {"file": filename, "version": 4, "redirect": False}, "study_version": 4, "file_version": 1 if filename == WORKBOOK else "see_metadata", "path": str(dest.relative_to(root)), "bytes": dest.stat().st_size, "sha256": sha(dest), "kind": "source_reported"})
    (raw / "source_manifest.json").write_text(json.dumps(sources, indent=2))
    return raw / WORKBOOK


def number(value):
    if isinstance(value, bool):
        return None, "missing"
    try:
        parsed = float(value)
        if np.isfinite(parsed):
            return parsed, "reported_numeric"
    except (TypeError, ValueError):
        pass
    return None, "missing_or_source_error"


def measurement(value, *, below_limit=False, saturated=False):
    parsed, status = number(value)
    if parsed is None:
        return None, status
    if below_limit:
        return None, "below_detection_limit"
    if saturated:
        return None, "saturated"
    return parsed, status


def preprocess(path, output="data/processed"):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheet = wb["Combined Rslts Copy this sheet"]
    records = []
    for row_number, cells in enumerate(sheet.iter_rows(values_only=True), 1):
        def cell(col):
            return cells[openpyxl.utils.column_index_from_string(col) - 1] if openpyxl.utils.column_index_from_string(col) <= len(cells) else None
        campaign = {1: "SAME", 2: "SAME-R"}.get(cell("A"))
        if campaign is None or cell("C") not in MATERIALS:
            continue
        test = str(cell("G")).strip()
        match = re.match(r"\s*(\d+)", test)
        if not match:
            continue
        run = match[1]
        sample = str(cell("D") or "").strip()
        # SAME has missing sample IDs: carousel + position is the conservative reuse unit.
        if not sample:
            sample = f"carousel={cell('B')};position={cell('F')};material={cell('C')}"
        signal, status = number(cell("AW"))
        record = {"source_row": row_number, "source_sheet": sheet.title, "campaign": campaign, "material": cell("C"), "test_id": f"{campaign}:{test}", "source_test_id": test, "source_local_test_id": str(cell("E")), "run_id": f"{campaign}:{run}", "sample_id": f"{campaign}:{sample}", "description": str(cell("H") or ""), "fan_problem": str(cell("L") or ""), "flat_profiles": str(cell("M") or ""), "iss_scatter_v": signal, "iss_scatter_status": status, "iss_saturation_status": "not_individually_resolved", "iss_detection_limit_status": "not_documented_for_this_reduced_channel", "signal_kind": "measured", "label_provenance": "derived", "label_rule": "ISS scatter >=2.0 V; Meyer et al. 2018 Figure 9", "alarm_level_reached": int(signal >= 2.0) if signal is not None else None}
        for col, name in MAP.items():
            record[name], record[name + "_status"] = number(cell(col))
            record[name + "_source_cell"] = f"{col}{row_number}"
        record["net_aging_s"], record["net_aging_s_status"] = number(cell("U"))
        for col, name in {"BL": "m0_source", "BM": "m1_mm_cm3", "BR": "source_amd_um", "BS": "source_dam_um"}.items():
            record[name], record[name + "_status"] = number(cell(col))
            if record[name] is not None and record[name] <= 0:
                record[name] = None
                record[name + "_status"] = "invalid_nonpositive_source_formula"
        record["derived_amd_um"] = 1000 * record["m1_mm_cm3"] / record["m0_source"] if record["m0_source"] and record["m1_mm_cm3"] else None
        record["amd_derivation"] = "1000*M1(mm/cm3)/M0(1/cm3); moment ratio; no lognormal assumption"
        records.append(record)
    wb.close()
    # Connected components prevent leakage from reused samples AND aged/reburned runs.
    parents = list(range(len(records)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    seen = {}
    for i, record in enumerate(records):
        for key in [record["run_id"], record["sample_id"]]:
            if key in seen:
                parents[find(i)] = find(seen[key])
            seen[key] = i
    for i, r in enumerate(records):
        r["group_id"] = f"group-{find(i):03d}"
        r["aging_index"] = sum(1 for q in records[:i] if q["run_id"] == r["run_id"])
        reasons = []
        if re.search(r"\d+\s*a", r["source_test_id"], re.I):
            reasons.append("secondary_aging_reading")
        if any(r[k] is None for k in FEATURES[1:]):
            reasons.append("missing_control")
        if r["heating_s"] is None or r["heating_s"] <= 0:
            reasons.append("followup_or_missing_heating_configuration")
        if r["iss_scatter_v"] is None or r["iss_scatter_v"] < 0:
            reasons.append("missing_or_invalid_signal")
        if r["fan_problem"].lower() in ["y", "yes"] or r["flat_profiles"].lower() in ["y", "yes"]:
            reasons.append("source_quality_flag")
        r["training_eligible"] = not reasons
        r["exclusion_reasons"] = ";".join(reasons)
    df = pd.DataFrame(records)
    df["duplicate_condition"] = df.duplicated(FEATURES, keep=False)
    df["near_duplicate_condition"] = df.duplicated(["material", "airflow_cm_s", "resistance_ratio", "heating_s"], keep=False)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "observations.csv", index=False)
    df[df.training_eligible].to_csv(out / "training.csv", index=False)
    df.select_dtypes(include="number").corr().to_csv(out / "correlations.csv")
    dictionary = [{"name": k, "unit": {"airflow_cm_s": "cm/s", "resistance_ratio": "1"}.get(k, "s"), "role": "controlled", "source": f"{sheet.title}!{col}", "conversion": "identity", "provenance": "source_reported"} for col, k in MAP.items()]
    dictionary.extend([{"name": "iss_scatter_v", "unit": "V", "role": "measured", "source": f"{sheet.title}!AW", "provenance": "source_reported", "limitations": "High-end saturation not numerically de-censored; preserved as reported for threshold classification only; exact calibrated LOD unavailable."}, {"name": "alarm_level_reached", "unit": "boolean", "role": "derived_label", "provenance": "derived", "rule": "iss_scatter_v >= 2.0", "source": "Meyer et al. 2018 Figure 9", "assumptions": "Summary signal crossing threshold represents recorded level, not time-to-alarm."}])
    details = {
        "material": ("C", "category", "controlled", "source_reported", "Tested smoke material only"),
        "campaign": ("A", "category", "identifier", "derived", "1 maps SAME;2 maps SAME-R; ground excluded"),
        "source_local_test_id": ("E", "identifier", "identifier", "source_reported", "Local material/test notation"),
        "source_test_id": ("G", "identifier", "identifier", "source_reported", "Global SAME number with secondary suffix a"),
        "sample_id": ("D or B+F+C", "identifier", "identifier", "derived", "Campaign prefix; carousel/position/material fallback if D blank"),
        "run_id": ("G", "identifier", "identifier", "derived", "Numeric prefix; campaign-qualified"),
        "net_aging_s": ("U", "s", "source_derived", "source_reported", "Source timing reduction; not a programmed input"),
        "m0_source": ("BL", "particles/cm3", "source_reduced_measurement", "source_reported", "Source calibrated CPC; size-dependent correction already applied"),
        "m1_mm_cm3": ("BM", "mm/cm3", "source_reduced_measurement", "source_reported", "Author ion chamber reduction; no recalibration"),
        "source_amd_um": ("BR", "um", "source_derived", "source_reported", "1000*M1/M0; no lognormal assumption"),
        "source_dam_um": ("BS", "um", "source_derived", "source_reported", "Source mass-equivalent diameter; density/spherical-equivalent interpretation; no lognormal needed"),
        "derived_amd_um": ("BL+BM", "um", "derived", "derived", "1000*M1/M0; no lognormal assumption"),
        "group_id": ("D+G or B+F+C", "identifier", "derived", "derived", "Connected run/sample graph over all observations; conservative ambiguous51a link"),
        "aging_index": ("row order within G numeric prefix", "index", "derived", "derived", "Sequential reading index, not independent experiment"),
    }
    known = {item["name"] for item in dictionary}
    for name in df.columns:
        if name in known:
            continue
        source, unit, role, provenance, assumptions = details.get(name, ("processing/source workbook", "1" if pd.api.types.is_numeric_dtype(df[name]) else "text", "metadata", "derived", "Status, identifier or deterministic processing metadata; see preprocessing code"))
        dictionary.append({"name": name, "unit": unit, "role": role, "provenance": provenance, "source": f"{sheet.title}!{source}", "assumptions": assumptions})
    for item in dictionary:
        item["type"] = str(df[item["name"]].dtype)
        item["missing_markers"] = ["blank", "NA", "n/a", "?", "??", "Excel error"]
        item.setdefault("assumptions", "No conversion or additional physical model")
        if item["role"] in ["measured", "source_reduced_measurement"]:
            item["instrument_limits"] = "Per-row LOD/saturation cannot be reconstructed from the summary. Do not use generic instrument limits after source dilution/calibration. Only AW2V threshold used for learning."
    (out / "data_dictionary.json").write_text(json.dumps(dictionary, indent=2))
    (out / "harmonization.json").write_text(json.dumps({"campaigns": ["SAME", "SAME-R"], "source": "author-combined workbook", "controls": MAP, "units": "identity; no recalibration", "target": "AW volts; common ISS sensor alarm reference", "not_harmonized": ["STS AX requires AY baseline and device-use flags", "MPASS not common", "ground experiments excluded", "DBP calibration excluded", "moment concentrations retain author calibration; never model inputs"]}, indent=2))
    return df
