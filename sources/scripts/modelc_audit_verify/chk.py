import json, hashlib, os, sys
R = '/home/efeai/Desktop/NasaSpaceApps/external/model_c'
def h(p):
    m = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            m.update(b)
    return m.hexdigest()
out = {}
rel = json.load(open(f'{R}/release_checksums.json'))
res = {'n': len(rel), 'match': [], 'mismatch': [], 'missing': []}
for k, v in rel.items():
    p = os.path.join(R, k)
    if not os.path.exists(p): res['missing'].append(k)
    elif h(p) == v: res['match'].append(k)
    else: res['mismatch'].append(k)
out['release'] = {k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}
out['release_missing'] = res['missing']; out['release_mismatch'] = res['mismatch']
# files on disk not in manifest
ondisk = []
for dp, dn, fn in os.walk(R):
    if '/.git' in dp or dp.endswith('.git'): continue
    for f in fn:
        rp = os.path.relpath(os.path.join(dp, f), R)
        if rp.startswith('.git/'): continue
        if rp not in rel: ondisk.append(rp)
out['ondisk_not_in_release'] = sorted(ondisk)
art = json.load(open(f'{R}/artifacts/model_c/checksums.json'))
out['artifacts'] = {k: h(f'{R}/artifacts/model_c/{k}') == v for k, v in art.items()}
man = json.load(open(f'{R}/data/raw/source_manifest.json'))
out['manifest'] = [(e['path'], h(os.path.join(R, e['path'])) == e['sha256'], (os.path.getsize(os.path.join(R, e['path'])) == e['bytes']) if 'bytes' in e else None) for e in man]
st = json.load(open(f'{R}/STATUS.json'))
out['status'] = {k: h(os.path.join(R, k)) == v for k, v in st['followup']['protected_artifact_sha256'].items()}
print(json.dumps(out, indent=1))
