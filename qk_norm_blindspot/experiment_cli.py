"""Recorded presets and reproducible model-input trials from the terminal."""
import argparse
import json
import math
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from . import paths


def execute(model, payload):
    if model == "a":
        from .side_panels import model_a_panel
        return model_a_panel(payload)
    if model == "b":
        from .side_panels import model_b_panel
        return model_b_panel()
    if model == "c":
        from .model_c import predict
        return predict(payload)
    from .wt4 import get_wt4
    model = get_wt4()
    if not 1 <= int(payload["max_new_tokens"]) <= 512 or len(payload["prompt"]) > 6000:
        raise ValueError("İstek sınırı: 6000 karakter, 1–512 yeni token")
    return {"generation": model.generate("Respond concisely. Do not invent scientific claims or numbers.",
                                       payload["prompt"], max_new_tokens=int(payload["max_new_tokens"])),
            "value_kind": "predicted", "model_report": model.report}


def main(argv=None):
    parser = argparse.ArgumentParser(description="QK norm · kayıtlı örneklerle model denemeleri")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Hazır örnekleri göster")
    for command in ("run", "sweep"):
        child = commands.add_parser(command, help="Tek deneme" if command == "run" else "Bir girdiyi değiştirerek karşılaştır")
        child.add_argument("model", choices=["a", "b", "c", "wt4"])
        child.add_argument("--preset", type=int, default=0)
        child.add_argument("--set", action="append", default=[], metavar="ALAN=DEĞER")
        child.add_argument("--output", type=Path)
        if command == "sweep":
            child.add_argument("--field", required=True)
            child.add_argument("--values", required=True, help="Virgülle ayrılmış sayılar")
    args = parser.parse_args(argv)
    presets = json.loads((paths.ROOT / "dashboard/dashboard_data.json").read_text())["ai_presets"]
    if args.command == "list":
        print(json.dumps({k: [{"preset": i, "label": p["label"], "input": p["input"]}
                              for i, p in enumerate(v)] for k, v in presets.items()}, ensure_ascii=False, indent=2))
        return 0
    if not 0 <= args.preset < len(presets[args.model]):
        parser.error("Geçersiz örnek numarası. experiment list ile seçenekleri görün.")
    payload = deepcopy(presets[args.model][args.preset]["input"])
    for assignment in args.set:
        key, sep, value = assignment.partition("=")
        if not sep or key not in payload or key == "units":
            parser.error("Geçersiz girdi alanı")
        try:
            payload[key] = float(value) if isinstance(payload[key], (float, int)) else value
            if isinstance(payload[key], (float, int)) and not math.isfinite(payload[key]):
                raise ValueError("Sonlu sayı bekleniyor")
        except ValueError:
            parser.error("Sonlu sayısal girdi bekleniyor")
    trials = [payload]
    if args.command == "sweep":
        if args.model not in ("a", "c") or not isinstance(payload.get(args.field), (int, float)):
            parser.error("Tarama için A/C modelinden sayısal bir girdi seçin")
        try:
            values = [float(v) for v in args.values.split(",")]
        except ValueError:
            parser.error("Değerler sayı olmalı")
        if not all(math.isfinite(v) for v in values):
            parser.error("Sonlu değerler girin")
        if not 1 <= len(values) <= 50:
            parser.error("1–50 değer girin")
        trials = [dict(payload, **{args.field: v}) for v in values]
    report = {"created_utc": datetime.now(timezone.utc).isoformat(), "model": args.model,
              "purpose": "Model girdisi denemesi", "value_kind": "predicted", "runs": []}
    try:
        for request in trials:
            report["runs"].append({"input": request, "output": execute(args.model, request)})
    except Exception as exc:
        report["error"] = str(exc)
        report["status"] = "PARTIAL" if report["runs"] else "FAILED"
    else:
        report["status"] = "COMPLETED"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
