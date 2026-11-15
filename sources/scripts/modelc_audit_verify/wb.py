import openpyxl, re, json, random, csv, sys
P='/home/efeai/Desktop/NasaSpaceApps'; R=P+'/external/model_c'
wb = openpyxl.load_workbook(R+'/data/raw/PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx', data_only=True)
print(wb.sheetnames)
ws = wb['Combined Rslts Copy this sheet']
hdr = {}
for c in ws[2]:
    if c.value is not None: hdr[str(c.value).strip()] = c.column_letter
def col(name_sub):
    m = [v for k, v in hdr.items() if name_sub.lower() in k.lower()]
    return m
print('campaign col', col('Flight 1'), 'material', col('Sample Type'), 'same#', col('SAME #'), 'iss', col('ISS Detector Scatter'), 'heat', col('Duration (sec)'), 'vel', col('Inlet Velocity'), 'rt', col('Rt/R0'))
cA = col('Flight 1')[0]; cM = col('Sample Type')[0]; cG = col('SAME #')[0]; cAW = col('ISS Detector Scatter')[0]
cN = col('Inlet Velocity')[0]; cO = col('Rt/R0')[0]
cP = [v for k,v in hdr.items() if k=='Duration (sec)'][0]
cQ = col('Primary Aging Duration')[0]; cR = col('Primary Mixing')[0]; cD = col('Sample ID')[0]; cH = col('Description')[0]
print(cA,cM,cG,cAW,cN,cO,cP,cQ,cR,cD,cH, 'ISS header text:', repr(ws[f'{cAW}2'].value))
MATS = {'Kapton','Lampwick','Pyrell','Silicone','Teflon'}
recs = []
for r in range(3, ws.max_row+1):
    camp = ws[f'{cA}{r}'].value; mat = ws[f'{cM}{r}'].value
    if camp not in (1, 2) or mat not in MATS: continue
    g = str(ws[f'{cG}{r}'].value).strip()
    recs.append(dict(row=r, camp={1:'SAME',2:'SAME-R'}[camp], mat=mat, same=g, iss=ws[f'{cAW}{r}'].value,
        vel=ws[f'{cN}{r}'].value, rt=ws[f'{cO}{r}'].value, heat=ws[f'{cP}{r}'].value, age=ws[f'{cQ}{r}'].value, mix=ws[f'{cR}{r}'].value,
        sid=ws[f'{cD}{r}'].value, desc=ws[f'{cH}{r}'].value))
print('flight material records', len(recs))
prim = [x for x in recs if re.fullmatch(r'\d+', x['same'])]
sec = [x for x in recs if not re.fullmatch(r'\d+', x['same'])]
print('primary', len(prim), 'secondary', len(sec), 'sec by camp', {c: sum(1 for x in sec if x['camp']==c) for c in ('SAME','SAME-R')})
print('primary by camp', {c: sum(1 for x in prim if x['camp']==c) for c in ('SAME','SAME-R')})
summary = {}
for m in sorted(MATS):
    pm = [x for x in prim if x['mat']==m]
    summary[m] = dict(n=len(pm), n2=sum(1 for x in pm if isinstance(x['iss'],(int,float)) and x['iss']>=2.0),
        ids=sorted([f"{x['camp']}:{x['same']}" for x in pm], key=lambda s:(s.split(':')[0]!='SAME', int(s.split(':')[1]))),
        bycamp={c:(sum(1 for x in pm if x['camp']==c), sum(1 for x in pm if x['camp']==c and x['iss']>=2.0)) for c in ('SAME','SAME-R')},
        issmin=min(x['iss'] for x in pm), issmax=max(x['iss'] for x in pm))
    print(m, summary[m])
# compare with dashboard_table.csv
dt = {row['test_id']: row for row in csv.DictReader(open(R+'/data/processed/dashboard_table.csv'))}
print('dashboard rows', len(dt))
mism = []
for x in recs:
    tid = f"{x['camp']}:{x['same']}"
    row = dt.get(tid)
    if row is None: mism.append(('missing', tid)); continue
    if row['material'] != x['mat'] or float(row['iss_scatter_v']) != float(x['iss']) or int(row['source_row']) != x['row'] or int(row['alarm_level_reached']) != int(x['iss'] >= 2.0):
        mism.append(('diff', tid, row['material'], row['iss_scatter_v'], x['iss']))
print('full-table mismatches', mism, 'extra in csv', set(dt) - {f"{x['camp']}:{x['same']}" for x in recs})
te = {k for k, v in dt.items() if v['training_eligible'] == 'True'}
print('training_eligible == my primary:', te == {f"{x['camp']}:{x['same']}" for x in prim}, len(te))
# my own random sample, different seed
rng = random.Random(4242)
samp = rng.sample(recs, 12)
for x in samp:
    tid = f"{x['camp']}:{x['same']}"; row = dt[tid]
    ok = row['material']==x['mat'] and float(row['iss_scatter_v'])==float(x['iss']) and int(row['source_row'])==x['row']
    print('SAMPLE', tid, x['mat'], x['iss'], 'row', x['row'], '| csv', row['material'], row['iss_scatter_v'], row['source_row'], 'label', row['alarm_level_reached'], 'MATCH' if ok else 'MISMATCH')
json.dump(dict(recs=recs), open(sys.argv[1], 'w'), default=str)
