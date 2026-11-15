import re,sys
L=open(sys.argv[1]).read().split('\n')
def toks(line, start=40):
    return [(m.start()+len(m.group())/2, m.group()) for m in re.finditer(r'\S+', line) if m.start()>=start]
rows={}
blocks=[]
cur=None
for i,l in enumerate(L):
    s=l.strip()
    if s.startswith('Sample Type'): cur={'type':toks(l)}; blocks.append(cur)
    elif s.startswith('Sample ID') and cur is not None: cur['id']=toks(l)
    elif s.startswith('SAME Test #') and cur is not None: cur['test']=toks(l)
    elif s.startswith('Inlet Velocity') and cur is not None and 'vel' not in cur: cur['vel']=toks(l)
    elif s.startswith('Rt/R0') and cur is not None and 'rt' not in cur: cur['rt']=toks(l)
    elif s.startswith('Use STS Detector') and cur is not None: cur['sts']=toks(l)
    elif s.startswith('Secondary Aging Duration') and cur is not None: cur['sad_line']=i
    elif s.startswith('(sec)') and cur is not None and 'sad' not in cur: cur['sad']=toks(l)
    elif s.startswith('Description') and cur is not None: cur['desc']=toks(l)
def near(x, lst, tol=6):
    best=None
    for xx,t in lst or []:
        if abs(xx-x)<=tol and (best is None or abs(xx-x)<abs(best[0]-x)): best=(xx,t)
    return best[1] if best else ''
out=[]
for b in blocks:
    for x,t in b.get('test',[]):
        out.append((t, near(x,b.get('type')), near(x,b.get('id')), near(x,b.get('vel')), near(x,b.get('rt')), near(x,b.get('sts')), near(x,b.get('sad'))))
for o in out: print(o)
prim=[o for o in out if not o[0].endswith('a')]
print('n entries',len(out),'primary',len(prim))
print('STS y:',[o[0] for o in prim if o[5]=='y'], len([o for o in prim if o[5]=='y']))
print('STS other:',[ (o[0],o[5]) for o in prim if o[5] not in ('y','n')])
