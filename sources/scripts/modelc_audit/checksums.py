import json, hashlib, os, sys
root = "/home/efeai/Desktop/NasaSpaceApps/external/model_c"
def sha(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()
out = {}
# release_checksums
rc = json.load(open(os.path.join(root,"release_checksums.json")))
def check(entries, base):
    res = {"pass":[], "fail":[], "missing":[]}
    for rel, exp in entries:
        p = os.path.join(base, rel)
        if not os.path.exists(p):
            res["missing"].append(rel); continue
        got = sha(p)
        (res["pass"] if got==exp else res["fail"]).append((rel, exp, got) if got!=exp else rel)
    return res
out["release_checksums"] = check(list(rc.items()), root)
ac = json.load(open(os.path.join(root,"artifacts/model_c/checksums.json")))
out["artifact_checksums"] = check(list(ac.items()), os.path.join(root,"artifacts/model_c"))
sm = json.load(open(os.path.join(root,"data/raw/source_manifest.json")))
out["source_manifest"] = check([(e["path"], e["sha256"]) for e in sm], root)
# bytes check in manifest
bc = []
for e in sm:
    if "bytes" in e:
        bc.append((e["path"], e["bytes"], os.path.getsize(os.path.join(root,e["path"]))))
out["manifest_bytes"] = bc
# STATUS protected
st = json.load(open(os.path.join(root,"STATUS.json")))
out["status_protected"] = check(list(st["followup"]["protected_artifact_sha256"].items()), root)
# files on disk not in release_checksums
ondisk = []
for dp, dn, fn in os.walk(root):
    if '.cache' in dp or '/.git' in dp: continue
    for f in fn:
        ondisk.append(os.path.relpath(os.path.join(dp,f), root))
out["on_disk_not_in_release"] = sorted(set(ondisk)-set(rc.keys()))
out["n_release_entries"] = len(rc)
for k,v in out.items():
    if isinstance(v, dict):
        print(k, {kk: len(vv) for kk,vv in v.items()})
        print("  fail:", v["fail"]); print("  missing:", v["missing"])
    else:
        print(k, v)
json.dump(out, open("checksums_result.json","w"), indent=1)
