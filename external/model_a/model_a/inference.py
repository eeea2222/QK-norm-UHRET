"""Notebook-free CPU inference. Load only artifacts you trust (joblib uses pickle)."""
import json, os, math, struct
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=4)
def _load(directory):
    path=Path(directory)
    if (path/'model.json').exists(): model=json.loads((path/'model.json').read_text())
    else:
        import joblib
        model=joblib.load(path/'model.joblib')
    return model, json.loads((path/'config.json').read_text())

@lru_cache(maxsize=4)
def _load_ood(directory):
    return json.loads((Path(directory)/'ood.json').read_text())

def _coverage(row, reference):
    features = reference['features']
    standardized = [(row[name]-mean)/std for name,mean,std in
                    zip(features, reference['mean'], reference['std'])]
    distances = [math.dist(standardized, [(value-mean)/std for value,mean,std in
                 zip(point['condition'], reference['mean'], reference['std'])])
                 for point in reference['conditions']]
    nearest = min(range(len(distances)), key=distances.__getitem__)
    return distances[nearest], reference['conditions'][nearest]['experiment_id']

def _predict(model,row,features):
    if isinstance(model,dict) and model.get('format')=='bass_random_forest_v1':
        # sklearn forests evaluate float32 after fitted float64 numeric scaling.
        x=[struct.unpack('f',struct.pack('f',(float(row[k])-m)/s))[0] for k,m,s in zip(model['features'],model['mean'],model['scale'])]
        values=[]
        for tree in model['trees']:
            node=0
            while tree['left'][node]!=-1:
                node=tree['left'][node] if x[tree['feature'][node]]<=tree['threshold'][node] else tree['right'][node]
            values.append(tree['value'][node])
        return math.fsum(values)/len(values)
    import pandas as pd
    return float(model.predict(pd.DataFrame([row],columns=features))[0])

def predict_model_a(input_data: dict) -> dict:
    """Validate units/domain and estimate BASS-II segment flame spread rate."""
    if not isinstance(input_data,dict):
        raise ValueError('input_data must be a dictionary')
    directory=os.environ.get('MODEL_A_ARTIFACT_DIR',str(Path(__file__).resolve().parents[1]/'artifacts'/'model_a_v1'))
    model, config=_load(directory)
    expected=set(config['features'])|{'units','material'}
    missing=expected-set(input_data); extra=set(input_data)-expected
    if missing or extra: raise ValueError(f'Missing fields: {sorted(missing)}; unexpected fields: {sorted(extra)}')
    if input_data['material']!=config['material']: raise ValueError(f"Supported material: {config['material']}")
    if input_data['units']!=config['input_units']: raise ValueError(f"units must equal {config['input_units']}")
    row={}; warnings=[]
    for name in config['features']:
        value=input_data[name]; domain=config['domain'][name]
        if domain['type']=='numeric':
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                raise ValueError(f'{name} must be a finite number')
            if value < domain['min'] or value > domain['max']:
                raise ValueError(f'{name} outside training range [{domain["min"]}, {domain["max"]}]')
            row[name]=float(value)
        else:
            if value not in domain['categories']: raise ValueError(f'{name} must be in {domain["categories"]}')
            row[name]=value
    reference = _load_ood(directory)
    if reference['features'] != config['features']:
        raise ValueError('OOD reference feature order differs from model config')
    nearest_distance, nearest_experiment_id = _coverage(row, reference)
    threshold = reference['threshold']
    out_of_distribution = nearest_distance > threshold
    if out_of_distribution:
        warnings.append('Condition is outside the distance-based training coverage threshold. This rough check uses only 18 groups, not a calibrated novelty probability; treat this estimate as exploratory.')
    prediction=_predict(model,row,config['features'])
    if prediction<0: warnings.append('Model returned a nonphysical negative rate; do not interpret as a physical rate.')
    warnings.extend(config['scientific_warnings'])
    return {'predicted_flame_spread_rate':prediction, 'unit':'mm/s','value_kind':'predicted', 'model_version':config['model_version'], 'algorithm':config['algorithm'], 'applicable_domain':config['domain'], 'out_of_distribution':out_of_distribution, 'nearest_distance':nearest_distance, 'ood_threshold':threshold, 'nearest_experiment_id':nearest_experiment_id, 'ood_check':'standardized_nearest_condition_distance', 'warnings':warnings}
