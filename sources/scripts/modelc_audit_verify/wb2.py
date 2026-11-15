import openpyxl, re, json, csv
P='/home/efeai/Desktop/NasaSpaceApps'; R=P+'/external/model_c'
f = R+'/data/raw/PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx'
wbf = openpyxl.load_workbook(f, data_only=False)
wbv = openpyxl.load_workbook(f, data_only=True)
cf = wbf['Combined Rslts Copy this sheet']; cv = wbv['Combined Rslts Copy this sheet']
print('AW3 formula', cf['AW3'].value, 'value', cv['AW3'].value)
# item 27 rows
dt = {row['test_id']: row for row in csv.DictReader(open(R+'/data/processed/dashboard_table.csv'))}
claims = [('SAME-R:81','Teflon',2.16257,105,1),('SAME:26a','Teflon',0.935562,12,0),('SAME-R:105a','Teflon',0.696808,154,0),('SAME-R:60','Silicone',6.25,65,1),('SAME-R:88','Lampwick',6.24727,119,1),('SAME-R:62','Kapton',6.242,70,1),('SAME-R:102a','Kapton',5.12692,147,1),('SAME-R:64','Pyrell',6.248,74,1),('SAME:47a','Kapton',5.88333,47,1),('SAME:30','Kapton',4.20316,17,1),('SAME-R:73','Kapton',0.437256,88,0),('SAME-R:113','Pyrell',6.28368,166,1)]
for tid, m, v, row, lab in claims:
    r = dt[tid]
    wv = cv[f'AW{row}'].value; wm = cv[f'C{row}'].value; wg = cv[f'G{row}'].value
    print(tid, m == r['material'] == wm, abs(float(r['iss_scatter_v'])-v) < 1e-5, abs(wv - v) < 1e-5, int(r['source_row'])==row, int(r['alarm_level_reached'])==lab, str(wg), wv)
# item 28: formula targets and cached-value agreement
same_r = wbv['SAME R Results']; same1 = wbv['SAME1 Flight Tests 8-27-09']
cnt = {'SAME-R': [0, 0], 'SAME': [0, 0]}; refs = {}
for r in range(3, cf.max_row+1):
    a = cv[f'A{r}'].value; m = cv[f'C{r}'].value
    if a not in (1, 2) or m not in {'Kapton','Lampwick','Pyrell','Silicone','Teflon'}: continue
    fml = cf[f'AW{r}'].value
    mm = re.match(r"='([^']+)'!([A-Z]+)(\d+)$", str(fml))
    if not mm: print('nonformula', r, fml); continue
    sh, c, rr = mm.groups(); refs.setdefault((sh, c), 0); refs[(sh, c)] += 1
    tv = wbv[sh][f'{c}{rr}'].value
    k = 'SAME-R' if a == 2 else 'SAME'
    cnt[k][0] += 1; cnt[k][1] += int(tv == cv[f'AW{r}'].value)
print('formula refs', refs, 'agreement', cnt)
# items 44-46 formula anchors
tf = wbf['Teflon R&T plots']; tv = wbv['Teflon R&T plots']; kf = wbf['Kapton R&T plots']; kv = wbv['Kapton R&T plots']
for c in ['BR','BS','BT','BU','BV','BW']:
    print('Teflon', c, '28', tf[f'{c}28'].value, tv[f'{c}28'].value, '| 29', tf[f'{c}29'].value, tv[f'{c}29'].value)
print('Teflon row 28 label cells', [tf.cell(28, i).value for i in range(1, 12)])
print('Teflon row 29 label cells', [tf.cell(29, i).value for i in range(1, 12)])
for c in ['BR','BS','BU','BV']:
    print('Kapton', c, '41', kf[f'{c}41'].value, kv[f'{c}41'].value)
print('Kapton row 41 label', [kf.cell(41, i).value for i in range(1, 12)])
print('Teflon hdr', {tf.cell(r, c).column_letter + str(r): tf.cell(r, c).value for r in (1,2,3,4,5,6,7,8,9) for c in range(66, 76) if tf.cell(r, c).value is not None})
for r in (10, 11, 15, 16, 25):
    print('Teflon row', r, [tv.cell(r, i).value for i in range(1, 10)], 'AW', tv[f'AW{r}'].value, 'BR..BV', [tv[f'{c}{r}'].value for c in ['BR','BS','BT','BU','BV']])
for r in (12, 13, 14, 15):
    print('Kapton row', r, [kv.cell(r, i).value for i in range(1, 10)], 'AW', kv[f'AW{r}'].value, 'BR..BV', [kv[f'{c}{r}'].value for c in ['BR','BS','BT','BU','BV']])
ices_f = wbf['ICES 2012 Paper data table']; ices_v = wbv['ICES 2012 Paper data table']
for r in range(1, 30):
    rowf = [(ices_f.cell(r, c).column_letter, ices_f.cell(r, c).value) for c in range(1, 20) if ices_f.cell(r, c).value is not None]
    if rowf: print('ICES', r, rowf[:14])
