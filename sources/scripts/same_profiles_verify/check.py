import json, re, sys
R='/home/efeai/Desktop/NasaSpaceApps/'
d=json.load(open(R+'sources/extracted/same_profiles.json'))
docs={x['doc_id']:x for x in d['documents']}
def norm(s): return re.sub(r'\s+',' ',s).strip()
texts={}
for k,v in docs.items():
    texts[k]=open(R+v['text_path']).read()
bad=[]
for it in d['items']:
    t=texts[it['doc_id']]
    if it['pdf_page']:
        pages=t.split('\f'); pg=pages[it['pdf_page']-1]
    else: pg=t
    a=norm(it['anchor_quote']); P=norm(pg)
    ok = a in P
    nw=len(it['anchor_quote'].split())
    nums=[]
    for n in it.get('numbers') or []:
        v=n.get('verbatim')
        if v and norm(v) not in P: nums.append(v)
    if not ok or nw>15 or nums:
        bad.append((it['item_id'],it['doc_id'],it['pdf_page'],ok,nw,nums,it['anchor_quote']))
for b in bad: print(b)
print(len(bad))
