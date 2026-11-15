"""Display recorded evaluations without fitting models or comparing incompatible tasks."""
import json
import statistics
from . import paths
from .sources import sha256_file

def build_benchmarks():
    files={'a':paths.MODEL_A_DIR/'artifacts/model_a_v1/metrics.json','b':paths.MODEL_B_DIR/'artifacts/metrics.json','c':paths.MODEL_C_DIR/'reports/followup_metrics.json'}
    a,b,c=[json.loads(files[k].read_text()) for k in ('a','b','c')]
    def row(name,score,ours=False,sd=None,winner=False,note=''):
        return dict(name=name,score=score,ours=ours,sd=sd,winner=winner,note=note,value_kind='source_reported')
    names={'mean':'Training-mean predictor','ridge':'Ridge regression','rbf_svr':'RBF support-vector regression','random_forest':'QK norm Model A · random forest','extra_trees':'Extra Trees','hist_gradient_boosting':'Histogram gradient boosting','inverse_thickness_ridge':'Inverse-thickness ridge'}
    candidates={k:v for k,v in a['summary'].items() if k in names}
    best=min(v['mae']['mean'] for v in candidates.values())
    rows=[row(names[k],v['mae']['mean'],k=='random_forest',v['mae']['std'],v['mae']['mean']==best) for k,v in candidates.items()]
    others=[v['mae']['mean'] for k,v in candidates.items() if k!='random_forest']
    median=statistics.median(others)
    median_row=row('Median of six comparison methods',median,note='Derived reference statistic; not an additional fitted model.')
    median_row['value_kind']='derived';rows.append(median_row)
    groups=[dict(title='Model A · BASS-II PMMA flame spread',metric='Experiment-macro MAE (mm/s) ↓',direction='lower',rows=rows,
       protocol='18 physical samples / 39 airflow segments; five grouped outer folds. Fixed-candidate results are retrospective diagnostics. No independent external test.',
       conclusion=f"Recorded Model A MAE is {(median-best)/median*100:.1f}% lower than the median of six comparison methods (derived descriptive difference).",
       caveat=f"The selection-unbiased nested procedure has MAE {a['summary']['nested_selection']['mae']['mean']:.5f} mm/s and mean R² {a['summary']['nested_selection']['r2']['mean']:.3f}. Fixed-candidate ranking does not replace that result.",
       source='https://huggingface.co/efe-T/nasa-bass-ii-model-a/blob/0096ac5a4959c13e0f7d1561160844db5f873ba3/artifacts/model_a_v1/metrics.json')]
    groups.append(dict(title='Model B · Saffire-I luminous ridge',metric='Held-out MAE (mm) ↓',direction='lower',
      rows=[row('QK norm Model B · learned correction',b['selected']['mae_mm'],True),row('Binary-median image baseline',b['simple_binary_median']['mae_mm'],winner=True),row('Constant-position baseline',b['trivial_constant']['mae_mm'])],
      protocol='Six correlated frames from a later time block of one burn; agent-annotated labels. These are frames, not six independent experiments.',
      conclusion='Binary-median baseline wins; the learned correction does not improve MAE.',caveat='No cross-burn validation. No meaningful population-average model can be inferred from these two baselines.',
      source='https://huggingface.co/efe-T/nasa-saffire-i-model-b/blob/7ca05303bf350d300f98011528cb4e1c4d28b612/artifacts/metrics.json'))
    v=c['baseline_comparison']
    groups.append(dict(title='Model C · SAME / SAME-R threshold label',metric='Mean balanced accuracy ↑',direction='higher',
      rows=[row('QK norm Model C · fixed forest',v['fixed_forest']['mean'],True,v['fixed_forest']['std'],True,'Tie under the released one-fold-SD rule; highest numerical mean.'),row('Training-fold material-majority baseline',v['material_majority']['mean'],sd=v['material_majority']['std'],winner=True,note='Tied with fixed forest under the released rule.'),row('Original nested model-selection procedure',v['original_nested_selection']['mean'],sd=v['original_nested_selection']['std'])],
      protocol='84 primary heating runs / 81 conservative groups; same five saved outer folds. Fixed-forest and material-majority comparisons are post-hoc.',
      conclusion='Tie: 0.00909 mean advantage for the forest is within the released variability rule; four of five paired differences are zero.',
      caveat='Fold SD is not a confidence interval. The label is derived ISS scatter ≥2.0 V, not operational alarm truth. Kapton/Teflon positive recall remains weak.',
      source='https://huggingface.co/efe-T/nasa-same-model-c/blob/91292a40886564d146dc9e9d496b74c2aefaab5c/reports/evaluation_followup.md'))
    groups.append(dict(title='WeightSeek-WT4 · language model',metric='Comparable task quality score',direction=None,
      rows=[row('QK norm · WeightSeek-WT4',None,True,note='No matched quality benchmark run.'),row('Unpatched Qwen3.5-0.8B weight-space-programming base',None,note='No matched quality benchmark run.')],
      protocol='Existing smoke tests establish loading and generation only.',conclusion='Unranked: no measured task-quality comparison is available.',caveat='Successful loading, checksum integrity and generated tokens are not quality scores.',source='https://huggingface.co/efe-T/WeightSeek-WT4'))
    related=[dict(title='CNN flame-front extraction (Strässle et al., 2024)',url='https://link.springer.com/article/10.1007/s00348-024-03814-z',location='Abstract; Sections 2–5',relevance='Related to Model B: learned flame-front segmentation.',comparability='OH-PLIF turbulent flames; segmentation IoU/recall, rather than Saffire luminous-ridge error in mm. Not ranked against ours.'),
      dict(title='Industrial burner flame segmentation comparison (2023)',url='https://isprs-annals.copernicus.org/articles/X-1-W1-2023/953/2023/isprs-annals-X-1-W1-2023-953-2023.html',location='Abstract / comparative study',relevance='Related to Model B: traditional image processing, ML and deep learning.',comparability='Industrial burner images and segmentation task; no shared Saffire split. Not ranked against ours.'),
      dict(title='Bayesian PMMA flame-spread parameter estimation',url='https://doi.org/10.1016/j.combustflame.2024.113828',location='Publisher abstract discovered in search; full text access blocked',relevance='Related to Model A: parameter estimation over cylindrical PMMA across gravity conditions.',comparability='Cylindrical samples and a different estimation task. No matched slab-regression MAE. Not ranked against ours.')]
    result={'groups':groups,'related_work':related,'selection_policy':'All eligible comparison methods in the frozen recorded evaluations are shown. Median uses all six Model A alternatives, excluding ours and the nested-selection procedure. No competitor was chosen to guarantee a win. There is no defensible global average across these different tasks.',
       'evaluation_status':'EXISTING_RECORDED_RESULTS_ONLY','source_files':{k:{'path':paths.rel(p),'sha256':sha256_file(p)} for k,p in files.items()}}
    paths.OUTPUTS.mkdir(exist_ok=True)
    (paths.OUTPUTS/'benchmarks.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
