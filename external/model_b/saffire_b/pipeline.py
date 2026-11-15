"""One command: original data -> integrity -> fit -> evaluate -> export -> CPU demo."""
import argparse,json,sys,platform
from pathlib import Path
from .data import prepare
from .calibration import calibrate
from .train import train
from .evaluate import evaluate
from .integrity import write_checksums,verify_checksums
from .inference import predict_model_b
from .stress import evaluate_stress


def run(root, cache_dir=None):
    root=Path(root);(root/'artifacts').mkdir(exist_ok=True)
    grid=prepare(root,cache_dir)
    (root/'artifacts/calibration.json').write_text(json.dumps(calibrate(grid),indent=2)+'\n')
    train(root)
    metrics=evaluate(root)
    evaluate_stress(root,cache_dir)
    finalize(root)
    return metrics


def finalize(root):
    root=Path(root)
    import numpy,sklearn,PIL,joblib,matplotlib
    (root/'artifacts/environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),
      'packages':{'numpy':numpy.__version__,'scikit-learn':sklearn.__version__,'Pillow':PIL.__version__,
                  'joblib':joblib.__version__,'matplotlib':matplotlib.__version__}},indent=2)+'\n')
    n=write_checksums(root/'artifacts');verify_checksums(root/'artifacts')
    frame=json.loads((root/'data/frames/frames.json').read_text())[20]
    request={'frame_path':str(root/'data/frames'/frame['filename']),'camera_id':'C1','image_mapping':'NASA_mapped','material':'SIBAL','units':'mm','timestamp_ms':frame['timestamp_ms']}
    response=predict_model_b(request,root/'artifacts')
    (root/'artifacts/sample_request_response.json').write_text(json.dumps({'request':request,'response':response},indent=2)+'\n')
    write_checksums(root/'artifacts')
    print('Export verified; standalone CPU sample:',json.dumps(response))
    return response

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path.cwd());parser.add_argument('--cache-dir',type=Path)
    args=parser.parse_args();run(args.root,args.cache_dir)
