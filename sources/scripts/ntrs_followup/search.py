import json, sys, subprocess, urllib.parse, os, time
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'q')
queries = sys.argv[1:]
log = []
for q in queries:
    fn = os.path.join(outdir, q.replace(' ', '_').replace('/', '_') + '.json')
    url = 'https://ntrs.nasa.gov/api/citations/search?q=' + urllib.parse.quote(q) + '&page.size=25'
    if not os.path.exists(fn):
        subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0', '--max-time', '60', url, '-o', fn])
        time.sleep(0.5)
    try:
        d = json.load(open(fn))
    except Exception as e:
        print('ERR', q, e); continue
    tot = d['stats']['total']
    print(f'=== {q!r} total={tot}')
    for r in d['results']:
        yr = (r.get('publications') or [{}])[0].get('publicationDate', '') or r.get('distributionDate', '') or r.get('created', '')
        dl = [x['name'] for x in r.get('downloads', [])]
        print(f"  {r['id']} | {yr[:4]} | {r.get('stiType')} | {r['title'][:110]} | dl={dl[:2]}")
