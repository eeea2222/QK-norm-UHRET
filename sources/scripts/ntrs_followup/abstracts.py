import json, glob, sys, os
want = set(sys.argv[1:])
seen = {}
for fn in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'q', '*.json')):
    try: d = json.load(open(fn))
    except: continue
    for r in d['results']:
        if str(r['id']) in want and str(r['id']) not in seen:
            seen[str(r['id'])] = r
for i in sys.argv[1:]:
    r = seen.get(i)
    if not r: print('MISSING', i); continue
    auth = [a['meta']['author']['name'] for a in r.get('authorAffiliations', [])]
    print('#####', i, r['title']); print('  authors:', auth); print('  sti:', r.get('stiType'), 'center:', r.get('center', {}).get('code'), 'pubs:', [(p.get('publicationName'), p.get('publicationDate','')[:10], p.get('doi')) for p in r.get('publications', [])])
    print('  other:', r.get('otherReportNumbers'), 'srcIds:', [s.get('number') for s in r.get('sourceIdentifiers', [])])
    print('  downloads:', [(x['name'], x['links'].get('pdf') or x['links'].get('original')) for x in r.get('downloads', [])])
    print('  ABS:', (r.get('abstract') or '')[:1800])
