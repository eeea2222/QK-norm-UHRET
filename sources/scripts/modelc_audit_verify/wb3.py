import openpyxl
f='/home/efeai/Desktop/NasaSpaceApps/external/model_c/data/raw/PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx'
wbf = openpyxl.load_workbook(f); wbv = openpyxl.load_workbook(f, data_only=True)
a = wbf['AIAA 2012 Paper data table']
for r in range(1, 14):
    print('AIAA', r, [(a.cell(r,c).column_letter, a.cell(r,c).value) for c in range(1, 20) if a.cell(r,c).value is not None])
for sh, cells in [('Kapton R&T plots', ['BR42','BR43']), ('Lampwick R&T Plots', ['BR31','BR32']), ('Pyrell R&T plots', ['BR26','BR27']), ('Silicone R&T plots', ['BR34','BR35'])]:
    for c in cells:
        print(sh, c, wbf[sh][c].value, wbv[sh][c].value)
# identify referenced rows' SAME# (col G) and description
import re
for sh, c in [('Kapton R&T plots','BR42'),('Lampwick R&T Plots','BR32'),('Pyrell R&T plots','BR27'),('Silicone R&T plots','BR35'),('Teflon R&T plots','BR29'),('Lampwick R&T Plots','BR31'),('Pyrell R&T plots','BR26'),('Silicone R&T plots','BR34')]:
    fml = wbf[sh][c].value
    rows = sorted(set(int(x) for x in re.findall(r'BR(\d+)', str(fml))))
    if ':' in str(fml):
        m = re.findall(r'BR(\d+):BR(\d+)', str(fml)); rows = sorted(set(sum([list(range(int(x), int(y)+1)) for x, y in m], [])) | set(rows))
    print(sh, c, fml, [(r, wbv[sh][f'G{r}'].value, wbv[sh][f'H{r}'].value, wbv[sh][f'D{r}'].value) for r in rows])
