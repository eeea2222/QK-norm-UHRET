"""Evaluate frozen selection exactly once against the untouched time block."""
import json,csv
from pathlib import Path
import numpy as np
from .inference import predict_model_b,image_features,extract_x
from .integrity import sha256


def evaluate(root):
    root=Path(root);out=root/'artifacts'
    frozen=json.loads((out/'selection_frozen.json').read_text())
    if sha256(out/'selection.json')!=frozen['selection_sha256'] or sha256(out/'model_config.json')!=frozen['model_config_sha256']:
        raise ValueError('Selection changed after freeze')
    labels=json.loads((root/'data/annotations_test.json').read_text())
    if labels['label_provenance']!='agent_annotated':raise ValueError('Unexpected test provenance')
    annotations={a['frame_id']:a for a in labels['annotations']}
    if sorted(annotations)!=frozen['test_ids']:raise ValueError('Unexpected held-out IDs')
    frames=json.loads((root/'data/frames/frames.json').read_text())
    dev=json.loads((root/'data/annotations.json').read_text())['annotations']
    scale=json.loads((out/'calibration.json').read_text())['mm_per_px_x']
    constant=float(np.mean([a['x_px'] for a in dev if a['valid']]))
    preds=[];reference=[];simple=[];details=[]
    for i in frozen['test_ids']:
        a=annotations[i];frame=frames[i]
        request={'frame_path':str(root/'data/frames'/frame['filename']),'camera_id':'C1',
                 'image_mapping':'NASA_mapped','material':'SIBAL','units':'mm','timestamp_ms':frame['timestamp_ms']}
        result=predict_model_b(request,out)
        if result['ood']['flag']:raise ValueError(f'Held-out measurement rejected: {i}, {result["ood"]}')
        p=result['position_px'];s=extract_x(image_features(request['frame_path']),'binary_median',20)
        preds.append(p);simple.append(s);reference.append(a['x_px'])
        details.append({'frame_id':i,'time_s':frame['time_s'],'reference_x_px':a['x_px'],
                        'predicted_x_px':p,'simple_x_px':s,'label_provenance':'agent_annotated',
                        'error_mm':float(abs(p-a['x_px'])*scale)})
    p=np.array(preds);y=np.array(reference);s=np.array(simple)
    def score(pred):return {'mae_mm':float(np.mean(abs(pred-y))*scale),'rmse_mm':float(np.sqrt(np.mean((pred-y)**2))*scale)}
    metrics={'headline':'Untouched later time block, not cross-burn generalization',
       'test_frame_ids':frozen['test_ids'],'test_n':len(y),'test_time_s':[frames[20]['time_s'],frames[25]['time_s']],
       'minimum_development_test_gap_s':float(frames[20]['time_s']-frames[17]['time_s']),
       'label_provenance':'agent_annotated','value_kind':'derived',
       'nominal_physical_calibration':True,
       'selected':score(p),'simple_binary_median':score(s),'trivial_constant':score(np.full_like(y,constant)),
       'per_frame_results':details,'selection_sha256':frozen['selection_sha256'],
       'test_label_sha256':sha256(root/'data/annotations_test.json'),
       'uncertainty':None,'r2':None,
       'limitations':'Six correlated frames in one later 50s block of the same burn. Visual agent labels are not independent human truth. Nominal grid scale has unquantified systematic error; no confidence interval or claim about another experiment.'}
    metrics['paired_mae_difference_vs_simple_mm']=metrics['selected']['mae_mm']-metrics['simple_binary_median']['mae_mm']
    metrics['paired_mae_difference_vs_trivial_mm']=metrics['selected']['mae_mm']-metrics['trivial_constant']['mae_mm']
    # Derived trajectory uses only accepted measurements. Reference rates are not targets.
    trajectory=[]
    for frame in frames:
        result=predict_model_b({'frame_path':str(root/'data/frames'/frame['filename']),
            'camera_id':'C1','image_mapping':'NASA_mapped','material':'SIBAL','units':'mm'},out)
        trajectory.append({'frame_id':frame['frame_id'],'time_s':frame['time_s'],
            'position_mm':result['value'],'value_kind':result['value_kind'],'ood':result['ood']['flag'],
            'ood_reason':'; '.join(result['ood']['reasons'])})
    accepted=[r for r in trajectory if r['position_mm'] is not None]
    t=np.array([r['time_s'] for r in accepted]);v=np.array([r['position_mm'] for r in accepted])
    speed=float(-np.polyfit(t,v,1)[0])
    ref=json.loads((root/'data/source_reported_reference.json').read_text())
    source_rate=next(r['spread_rate_mm_s'] for r in ref['rows'] if r['test_id']=='I-1')
    metrics['trajectory']={'accepted_frames':len(accepted),'rejected_frames':len(frames)-len(accepted),
       'time_range_s':[float(t.min()),float(t.max())],'luminous_ridge_speed_mm_s':speed,
       'value_kind':'derived','source_reported_concurrent_spread_mm_s':source_rate,
       'signed_consistency_difference_mm_s':speed-source_rate,
       'comparison_note':'Least-squares image ridge velocity over accepted visible-camera interval. Published 1.8mm/s is a burn-level spread quantity, so this difference is a consistency check, not task prediction error or a matched-quantity accuracy metric.'}
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    proc=root/'data/processed';proc.mkdir(exist_ok=True)
    with (proc/'trajectory.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(trajectory[0]));writer.writeheader();writer.writerows(trajectory)
    figs=root/'figures';figs.mkdir(exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    axes[0].plot(t,v,'o-',label='Extracted luminous ridge')
    for filename,style in [('annotations.json','o'),('annotations_test.json','s')]:
        rows=json.loads((root/'data'/filename).read_text())['annotations']
        axes[0].scatter([frames[r['frame_id']]['time_s'] for r in rows if r['valid']],
          [r['x_px']*scale for r in rows if r['valid']],marker=style,label='Agent labels '+('test' if 'test' in filename else 'development'))
    axes[0].set(xlabel='Time since first archived C1 frame (s)',ylabel='Ridge x from image left (nominal mm)')
    axes[0].axvspan(frames[20]['time_s'],frames[25]['time_s'],color='grey',alpha=.15)
    axes[0].legend(fontsize=7)
    axes[1].plot(y*scale,p*scale,'o',label='Held-out frames')
    lo,hi=min(y.min(),p.min())*scale,max(y.max(),p.max())*scale
    axes[1].plot([lo,hi],[lo,hi],'k--');axes[1].set(xlabel='Agent reference (nominal mm)',ylabel='Extracted position (nominal mm)')
    axes[1].legend();fig.tight_layout();fig.savefig(figs/'measurement_evaluation.png',dpi=170);plt.close(fig)
    print(json.dumps({'heldout_mae_mm':metrics['selected']['mae_mm'],'simple_mae_mm':metrics['simple_binary_median']['mae_mm'],'trajectory_speed_mm_s':speed}))
    return metrics

if __name__=='__main__':evaluate(Path.cwd())
