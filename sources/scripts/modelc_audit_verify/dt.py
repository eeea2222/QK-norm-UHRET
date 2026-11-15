import pandas as pd, numpy as np
R='/home/efeai/Desktop/NasaSpaceApps/external/model_c'
d = pd.read_csv(R+'/data/processed/dashboard_table.csv')
p = d[d.training_eligible]
cols = ['test_id','material','campaign','sample_id','description','airflow_cm_s','resistance_ratio','heating_s','aging_s','mixing_s','iss_scatter_v','group_id']
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200); pd.set_option('display.max_colwidth', 40)
for m in ['Kapton','Teflon']:
    print(p[p.material==m][cols].to_string())
print('groups per material', p.groupby('material').group_id.nunique().to_dict())
print('n runs per campaign', p.groupby('campaign').size().to_dict(), '>=2', (p.iss_scatter_v>=2).sum(), '<2', (p.iss_scatter_v<2).sum())
print('below2 by material', p[p.iss_scatter_v<2].groupby('material').size().to_dict())
k = p[p.material=='Kapton']
print('Kapton SAME-R groups', k[k.campaign=='SAME-R'].group_id.nunique())
lo = k[k.airflow_cm_s<=2]; print('Kapton <=2', len(lo), (lo.iss_scatter_v>=2).sum(), lo.test_id.tolist())
hi = k[(k.airflow_cm_s==8.1)&(k.campaign=='SAME-R')]; print('Kapton 8.1 SAME-R', len(hi), (hi.iss_scatter_v>=2).sum(), hi.group_id.nunique(), hi[hi.iss_scatter_v>=2].test_id.tolist())
s8 = k[(k.airflow_cm_s==8.0)&(k.campaign=='SAME')]; print('Kapton SAME 8.0', len(s8), (s8.iss_scatter_v>=2).sum())
print('Kapton airflow values', sorted(k.airflow_cm_s.unique()))
t = p[p.material=='Teflon']
b = t[t.resistance_ratio<=1.445]; print('Teflon rt<=1.445', len(b), (b.iss_scatter_v>=2).sum(), b.test_id.tolist(), b.iss_scatter_v.max(), sorted(b.airflow_cm_s.unique()))
h = t[t.resistance_ratio>=1.448]; print('Teflon rt>=1.448', len(h), (h.iss_scatter_v>=2).sum(), h.test_id.tolist(), sorted(h.campaign.unique()))
print('Teflon >=2', t[t.iss_scatter_v>=2][['test_id','resistance_ratio']].values.tolist())
z = p[p.airflow_cm_s==0]; print('no flow', z.groupby('material').apply(lambda g: (len(g), int((g.iss_scatter_v>=2).sum()))).to_dict(), sorted(z.campaign.unique()), z.groupby('material').group_id.nunique().sum())
print(z[['test_id','material','iss_scatter_v','heating_s','aging_s','description']].to_string())
a = p[p.aging_s==720]; print('720 aging', a[['test_id','material','iss_scatter_v','description']].values.tolist())
print('heating by material', p.groupby('material').heating_s.agg(['min','max']).to_dict())
print('mixing != 8', p[p.mixing_s!=8][['test_id','material','mixing_s']].values.tolist())
print('SAME:41', d[d.test_id=='SAME:41'][cols].values.tolist())
print('reburns', d[d.test_id.isin(['SAME-R:90','SAME-R:85','SAME-R:57','SAME-R:54'])][cols].values.tolist())
print('51/51a/61', d[d.test_id.isin(['SAME-R:51','SAME-R:51a','SAME-R:61','SAME-R:61a'])][cols+['training_eligible','exclusion_reasons']].values.tolist())
allk = d[d.material=='Kapton']; allt = d[d.material=='Teflon']
print('Kapton all records', len(allk), (allk.iss_scatter_v<2).sum(), 'Teflon all', len(allt), (allt.iss_scatter_v<2).sum())
ts = t[t.campaign=='SAME-R']; print('Teflon SAME-R primary', len(ts), (ts.iss_scatter_v<2).sum())
print('secondary count', (~d.training_eligible).sum(), d[~d.training_eligible].exclusion_reasons.value_counts().to_dict())
print('ISS high-end LPS', p[p.material.isin(['Lampwick','Pyrell','Silicone'])].iss_scatter_v.describe().to_dict())
print('Lampwick/Pyrell below 6.2', p[p.material.isin(['Lampwick','Pyrell','Silicone'])&(p.iss_scatter_v<6.2)][['test_id','material','iss_scatter_v']].values.tolist())
print('primary samples', p.sample_id.nunique())
print('Kapton groups list', k.groupby('group_id').test_id.apply(list).to_dict())
