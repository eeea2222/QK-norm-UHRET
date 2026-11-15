"""Select and fit measurement candidates using development labels only."""
import json,platform,sys
from pathlib import Path
import joblib
import numpy as np
import sklearn
from sklearn.linear_model import LinearRegression
from .inference import image_features,extract_x
from .integrity import sha256,write_checksums


def train(root):
    root=Path(root);out=root/'artifacts';out.mkdir(exist_ok=True)
    frames=json.loads((root/'data/frames/frames.json').read_text())
    labels=json.loads((root/'data/annotations.json').read_text())
    if labels['label_provenance']!='agent_annotated':raise ValueError('Unexpected annotation provenance')
    anns=[a for a in labels['annotations'] if a['valid']]
    ids=np.array([a['frame_id'] for a in anns]);y=np.array([a['x_px'] for a in anns],dtype=float)
    if set(ids)!=set(range(18)):raise ValueError('Expected preregistered development IDs0..17 only')
    features={i:image_features(root/'data/frames'/frames[i]['filename']) for i in ids}
    scale=json.loads((out/'calibration.json').read_text())['mm_per_px_x']
    folds=[]
    for f in range(3):
        val=np.arange(f*6,(f+1)*6)
        tr=np.array([i for i in ids if np.min(np.abs(i-val))>1])
        folds.append((tr,val))
    candidates=[]
    for method in ['binary_median','weighted_median','projection_peak']:
        x=np.array([extract_x(features[i],method,20) for i in ids],dtype=float)
        for learned in [False,True]:
            name=method+('_linear_correction' if learned else '')
            results=[]
            for f,(tr,val) in enumerate(folds):
                estimator=LinearRegression().fit(x[tr,None],y[tr]) if learned else None
                pred=estimator.predict(x[val,None]) if learned else x[val]
                baseline=np.full(len(val),float(y[tr].mean()))
                results.append({'fold':f,'train_frame_ids':tr.tolist(),'val_frame_ids':val.tolist(),
                    'mae_mm':float(np.mean(np.abs(pred-y[val]))*scale),
                    'rmse_mm':float(np.sqrt(np.mean((pred-y[val])**2))*scale),
                    'trivial_baseline_mae_mm':float(np.mean(np.abs(baseline-y[val]))*scale),
                    'paired_mae_difference_vs_trivial_mm':float(np.mean(np.abs(pred-y[val]))*scale-np.mean(np.abs(baseline-y[val]))*scale)})
            errors=[r['mae_mm'] for r in results]
            candidates.append({'name':name,'method':method,'learned_correction':learned,'threshold':20,
                               'folds':results,'mae_mean_mm':float(np.mean(errors)),
                               'mae_std_mm':float(np.std(errors,ddof=1))})
    best=min(candidates,key=lambda c:c['mae_mean_mm'])
    eligible=[c for c in candidates if c['mae_mean_mm']<=best['mae_mean_mm']+best['mae_std_mm']]
    selected=min(eligible,key=lambda c:(c['mae_std_mm'],c['learned_correction'],c['name']))
    simple=next(c for c in candidates if c['name']=='binary_median')
    for c in candidates:
        for f,r in enumerate(c['folds']):r['paired_mae_difference_vs_simple_mm']=r['mae_mm']-simple['folds'][f]['mae_mm']
    counts=[features[i]['red_pixel_count'] for i in ids]
    config={'version':'0.1.0','method':selected['method'],'threshold':20,
            'learned_correction':selected['learned_correction'],'selected_candidate':selected['name'],
            'min_x_px':200,'max_x_px':1500,
            'input_statistics_domain':{'max_green_fraction':.02,
               'red_pixel_count_min':max(10,int(min(counts)*.1)),
               'red_pixel_count_max':int(max(counts)*10)},
            'ood_procedure':'Dark-frame green fraction <=2%; luminous count [0.1*development_min,10*development_max]; visible spatial ROI x200:1500px. Fixed margins intentionally allow intensity variation; this is an input-quality envelope, not calibrated novelty probability.',
            'applicable_domain':{'mission':'Saffire-I','material':'SIBAL','camera_id':'C1','mapping':'NASA mapped','size_px':[1702,1226],
               'illumination':'dark/backlight off','ridge_band_y_px':[500,720],
               'development_time_s':[30,200],'development_frame_count':18,
               'independent_samples':1,'claim':'within-view measurement agreement with agent visual annotations; no cross-experiment prediction'}}
    if selected['learned_correction']:
        x=np.array([extract_x(features[i],selected['method'],20) for i in ids])
        config['correction_fit_input_range_px']=[float(x.min()),float(x.max())]
        estimator=LinearRegression().fit(x[:,None],y)
        joblib.dump(estimator,out/'ridge_correction.joblib')
    elif (out/'ridge_correction.joblib').exists():
        (out/'ridge_correction.joblib').unlink()
    selection={'status':'TRAINED' if selected['learned_correction'] else 'TESTED_LOCALLY',
       'label_provenance':'agent_annotated','objective':'MAE of representative luminous-ridge x, nominal mm',
       'selection_rule':'Minimum CV mean MAE; within best fold std, prefer lowest fold std, then no learned correction, then name.',
       'fold_standard_deviation_ddof':1,'minimum_train_validation_gap_s':20,
       'candidates':candidates,'selected':selected['name'],
       'heldout_frame_ids':[20,21,22,23,24,25],
       'test_label_accessed':False,
       'development_label_sha256':sha256(root/'data/annotations.json'),
       'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scikit_learn':sklearn.__version__},
       'note':'All six candidates share the same input frames, preprocessing and splits. No neural-network search; one linear fit or no fit per fold. No R2 claim at this sample size.'}
    (out/'model_config.json').write_text(json.dumps(config,indent=2)+'\n')
    (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    frozen={'selection_sha256':sha256(out/'selection.json'),'model_config_sha256':sha256(out/'model_config.json'),
            'frozen_before_test_label_access':True,'test_ids':[20,21,22,23,24,25]}
    (out/'selection_frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
    print(json.dumps({'selected':selected['name'],'development_mae_mean_mm':selected['mae_mean_mm'],'development_mae_std_mm':selected['mae_std_mm']}))
    return selection

if __name__=='__main__':
    train(Path.cwd())
