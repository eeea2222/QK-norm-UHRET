"""Actual localhost HTTP smoke test; no scientific evaluation."""
import json
import urllib.request
from pathlib import Path
base='http://127.0.0.1:8005'
checks=[]
def call(route,payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(base+route,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=120) as r:
        blob=r.read().decode()
        return r.status, json.loads(blob) if 'application/json' in r.headers.get('Content-Type','') else blob
for route,payload in [('/health',None),('/',None),('/blindspots',{'question':'Show catalog','filters':{'material':'Teflon'}}),('/models/b/sample',None),('/models/c',json.loads(Path('examples/model_c_request.json').read_text())),('/models/wt4/generate',{'prompt':'Say hello.','max_new_tokens':12})]:
    try:
        status,result=call(route,payload)
        checks.append({'route':route,'expected':'HTTP 200 with usable result','status':status,'passed':status==200,'actual':result if isinstance(result,dict) else result[:100]})
    except Exception as exc:
        checks.append({'route':route,'expected':'HTTP 200 with usable result','passed':False,'error':str(exc)})
report={'type':'SOFTWARE_HTTP_SMOKE','scientific_validation_status':'DEFERRED_BY_REQUEST','passed':sum(x['passed'] for x in checks),'executed':len(checks),'checks':checks}
Path('outputs/http_smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
raise SystemExit(0 if all(x['passed'] for x in checks) else 1)
