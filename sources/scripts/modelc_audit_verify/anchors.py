import json, re, sys
P = '/home/efeai/Desktop/NasaSpaceApps'
R = P + '/external/model_c'
FILES = {
 'release_checksums.json': R+'/release_checksums.json',
 'checksums.json': R+'/artifacts/model_c/checksums.json',
 'source_manifest.json': R+'/data/raw/source_manifest.json',
 'STATUS.json': R+'/STATUS.json',
 'data_dictionary.json': R+'/data/processed/data_dictionary.json',
 'dashboard_measured_only.csv': R+'/data/processed/dashboard_measured_only.csv',
 'dashboard_table.csv': R+'/data/processed/dashboard_table.csv',
 'evaluation.md': R+'/reports/evaluation.md',
 'evaluation_followup.md': R+'/reports/evaluation_followup.md',
 'metrics.json': R+'/reports/metrics.json',
 'followup_metrics.json': R+'/reports/followup_metrics.json',
 'external_checks.csv': R+'/reports/external_checks.csv',
 'ood_example.json': R+'/reports/ood_example.json',
 'teflon_table1_check.json': R+'/data/references/teflon_table1_check.json',
 'MODEL_CARD.md': R+'/MODEL_CARD.md',
 'domain.json': R+'/artifacts/model_c/domain.json',
 'data.py': R+'/model_c/data.py',
 'train.py': R+'/model_c/train.py',
 'modelc-pmc7918997': P+'/sources/text/modelc-pmc7918997.txt',
}
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
d = json.load(open(P+'/sources/extracted/modelc_audit.json'))
for it in d['items']:
    a = norm(it['anchor_quote']); doc = it['doc_id']; pg = it['pdf_page']
    nw = len(a.split())
    if doc.startswith('modelc-') and doc != 'modelc-pmc7918997':
        pages = open(f'{P}/sources/text/{doc}.txt').read().split('\f')
        ok = a in norm(pages[pg-1])
        other = [i+1 for i,p in enumerate(pages) if a in norm(p)]
        print(it['item_id'], doc, 'p', pg, 'OK' if ok else 'MISSING', 'found_on', other, 'words', nw)
    elif doc in FILES:
        txt = open(FILES[doc]).read()
        ok = a in norm(txt)
        # also raw (json-escaped) check
        print(it['item_id'], doc, 'OK' if ok else 'MISSING', 'words', nw, '' if ok else repr(a))
    else:
        print(it['item_id'], doc, 'XLSX/OTHER', repr(a), 'words', nw)
