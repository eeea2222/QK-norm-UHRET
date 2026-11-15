import math, json
def chk(name, rows):
    print('==', name)
    for mat, age, dg, dc, dm, sg in rows:
        out = []
        for c, printed in ((0.5, dc), (1.5, dm)):
            v = dg*math.exp(c*math.log(sg)**2)
            lo = (dg-.0005)*math.exp(c*math.log(sg-.0005)**2); hi = (dg+.0005)*math.exp(c*math.log(sg+.0005)**2)
            ok = not (hi < printed-.0005 or lo > printed+.0005)
            out.append((round(v,6), round(lo,6), round(hi,6), printed, 'OK' if ok else 'FAIL'))
        print(mat, age, out)
ntrs = [('Kapton','U',0.042,0.056,0.101,2.154),('Kapton','A',0.089,0.109,0.161,1.872),('Lampwick','U',0.090,0.128,0.258,2.312),('Lampwick','A',0.229,0.276,0.398,1.834),
        ('Silicone','U',0.128,0.196,0.465,2.530),('Silicone','A',0.269,0.355,0.619,2.108),('Teflon','U',0.081,0.101,0.170,2.198),('Teflon','A',0.070,0.105,0.232,2.442),
        ('Pyrell','U',0.149,0.204,0.384,2.211),('Pyrell','A',0.293,0.359,0.539,1.892)]
samer = [('Kapton','U',0.047,0.062,0.106,2.072),('Kapton','A',0.102,0.121,0.169,1.790),('Lampwick','U',0.103,0.142,0.271,2.232),('Lampwick','A',0.269,0.308,0.401,1.673),
        ('Silicone','U',0.152,0.221,0.468,2.382),('Silicone','A',0.320,0.400,0.628,1.956),('Teflon','U',0.093,0.111,0.173,2.081),('Teflon','A',0.080,0.115,0.237,2.342),
        ('Pyrell','U',0.177,0.227,0.377,2.032),('Pyrell','A',0.348,0.400,0.529,1.697)]
chk('NTRS 20130000422 Table 1', ntrs); chk('SAME-R report Table 1', samer)
# implied
r = math.log(0.170/0.101); s = math.exp(math.sqrt(r)); dg = 0.101/math.exp(0.5*r); print('implied sg', s, 'dg', dg)
# workbook averaged params
dg, sg = 0.0814749578294521, 2.198321695711983
print('from averaged', dg*math.exp(.5*math.log(sg)**2), dg*math.exp(1.5*math.log(sg)**2))
# per-run consistency (Teflon rows 10,11,15,16): CMD, DAM, sigma, Dg
runs = {58:(0.0531282678168605,0.14934491754394455,2.7638822532432576,0.031687885565052865),79:(0.16283968830998286,0.19310173093440533,1.5111289946801014,0.14953653401481964),
        89:(0.05508867666449692,0.15132510528359466,2.732534317487376,0.03323823985693733),56:(0.13183675328073566,0.18452250171432627,1.785741217437197,0.11143717188099855)}
for k,(cmd,dam,s,d) in runs.items():
    print(k, 'cmd rel err', d*math.exp(.5*math.log(s)**2)/cmd-1, 'dam rel err', d*math.exp(1.5*math.log(s)**2)/dam-1)
