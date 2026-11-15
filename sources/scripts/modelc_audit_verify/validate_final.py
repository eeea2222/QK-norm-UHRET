import json, re, sys, openpyxl
P='/home/efeai/Desktop/NasaSpaceApps'; R=P+'/external/model_c'
FN = P+'/sources/extracted/modelc_audit.final.json'
f = json.load(open(FN))
f.pop('verifier_summary', None)
json.dump(f, open(FN, 'w'), indent=1, ensure_ascii=False)
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
docs = {d['doc_id']: d for d in f['documents']}
CATS = set("missed_alarm false_alarm particle_property measurement_limitation technology_need research_question recommendation test_condition investigation_profile followup_solution context reference definition modelc_measured external_check model_limitation checksum".split())
W = R+'/data/raw/PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx'
wbf = openpyxl.load_workbook(W)
XL = {'modelc_audit-25': ('Combined Rslts Copy this sheet','AW2'), 'modelc_audit-28': ('Combined Rslts Copy this sheet','AW3'), 'modelc_audit-44': ('Teflon R&T plots','BR28'), 'modelc_audit-45': ('Kapton R&T plots','BR41'), 'modelc_audit-46': ('Teflon R&T plots','BR29')}
bad = 0; from collections import Counter; verd = Counter(); added = 0
for it in f['items']:
    a = norm(it['anchor_quote']); nw = len(a.split()); doc = it['doc_id']
    if it['item_id'] in XL:
        sh, c = XL[it['item_id']]; ok = str(wbf[sh][c].value) == it['anchor_quote']
    elif doc.startswith('modelc-') and doc != 'modelc-pmc7918997':
        ok = a in norm(open(f"{P}/sources/text/{doc}.txt").read().split('\f')[it['pdf_page']-1])
    else:
        lp = docs[doc]['local_path'] if doc != 'modelc-pmc7918997' else P+'/sources/text/modelc-pmc7918997.txt'
        ok = a in norm(open(lp).read())
    v = it.get('verification', {}).get('verdict'); verd[v] += 1; added += int(bool(it.get('added_by_verifier')))
    good = ok and nw <= 15 and it['category'] in CATS and v in ('CONFIRMED','CORRECTED','REJECTED') and 'location' in it and it['location']
    if not good: bad += 1; print('BAD', it['item_id'], ok, nw, it['category'], v)
print('items', len(f['items']), 'bad', bad, dict(verd), 'added', added, 'docs', len(f['documents']))
