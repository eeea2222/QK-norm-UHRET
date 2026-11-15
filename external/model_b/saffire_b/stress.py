"""Evaluate opposed acquisition-record input availability separately from accuracy."""
import json
from pathlib import Path
from .data import prepare
from .inference import predict_model_b


def evaluate_stress(root, cache_dir=None):
    root=Path(root);prepare(root,cache_dir,'stress')
    rows=json.loads((root/'data/stress/frames.json').read_text())
    results=[]
    for row in rows:
        response=predict_model_b({'frame_path':str(root/'data/stress'/row['filename']),
            'camera_id':'C1','image_mapping':'NASA_mapped','material':'SIBAL','units':'mm'},root/'artifacts')
        results.append({**row,'ood':response['ood'],'output_value':response['value']})
    obj={'stress_test':'Fit concurrent I-1, apply frozen selection to opposed I-2 acquisition record C1',
      'n':len(results),'rejected':sum(r['ood']['flag'] for r in results),'independent_samples':1,
      'localization_metric':None,'label_provenance':'agent_annotated',
      'interpretation':'Availability check only. This uniformly sampled opposed acquisition record includes pre/post-burn frames; no center-band ridge is localizable in the inspected C1 subset. It does not yield a leave-one-independent-burn-out accuracy estimate. C2 is unsupported. Do not pool these records with the primary test block.',
      'results':results}
    (root/'artifacts/domain_shift.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({k:v for k,v in obj.items() if k!='results'}));return obj

if __name__=='__main__':evaluate_stress(Path.cwd(),Path('/content/saffire_sources') if Path('/content/saffire_sources').exists() else None)
