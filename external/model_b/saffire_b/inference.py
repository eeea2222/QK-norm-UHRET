"""Notebook-free CPU measurement of the luminous ridge in NASA mapped C1 images."""
import json
from pathlib import Path
import numpy as np
from PIL import Image


def image_features(path):
    with Image.open(path) as image:
        if image.size != (1702,1226) or image.mode != 'RGB':
            raise ValueError('Expected unresized RGB NASA mapped C1 frame, 1702x1226')
        rgb=np.asarray(image,dtype=float)
    band=rgb[500:720]
    r,g,b=band[:,:,0],band[:,:,1],band[:,:,2]
    excess=np.maximum(r-np.maximum(g,b),0)
    return {'r':r,'excess':excess,
            'green_fraction':float(((rgb[:,:,1]>1.5*rgb[:,:,0])&(rgb[:,:,1]>50)).mean()),
            'red_pixel_count':int(((r>20)&(excess>10)).sum()),
            'mean_red_excess':float(excess.mean())}


def extract_x(features, method='binary_median', threshold=20):
    r,excess=features['r'],features['excess']
    mask=(r>threshold)&(excess>threshold/2)
    ys,xs=np.nonzero(mask)
    if len(xs)<10:
        return None
    if method=='binary_median':
        return float(np.median(xs))
    if method=='weighted_median':
        mass=np.sum(np.where(mask,excess**2,0),axis=0)
        return float(np.searchsorted(np.cumsum(mass),mass.sum()/2))
    if method=='projection_peak':
        mass=np.sum(np.where(mask,excess,0),axis=0)
        return float(np.argmax(np.convolve(mass,np.ones(21)/21,mode='same')))
    raise ValueError(f'Unsupported extraction method: {method}')


def predict_model_b(input_data, artifact_dir=None):
    """Accept a frame request and return a derived camera-plane luminous-ridge position.

    Required: frame_path, camera_id='C1', image_mapping='NASA_mapped',
    material='SIBAL', units='mm'. Optional: timestamp_ms. No extrapolation to C2.
    """
    if not isinstance(input_data,dict):
        raise TypeError('input_data must be a dict')
    allowed={'frame_path','camera_id','image_mapping','material','units','timestamp_ms'}
    if set(input_data)-allowed:
        raise ValueError(f'Unknown fields: {sorted(set(input_data)-allowed)}')
    for key,value in {'camera_id':'C1','image_mapping':'NASA_mapped','material':'SIBAL','units':'mm'}.items():
        if input_data.get(key)!=value:
            raise ValueError(f'{key} must be {value!r}')
    if not input_data.get('frame_path'):
        raise ValueError('frame_path is required')
    if 'timestamp_ms' in input_data and (isinstance(input_data['timestamp_ms'],bool) or not isinstance(input_data['timestamp_ms'],(int,float)) or not np.isfinite(input_data['timestamp_ms'])):
        raise ValueError('timestamp_ms must be a finite epoch-millisecond number')
    artifact_dir=Path(artifact_dir) if artifact_dir else Path(__file__).resolve().parents[1]/'artifacts'
    config=json.loads((artifact_dir/'model_config.json').read_text())
    calibration=json.loads((artifact_dir/'calibration.json').read_text())
    f=image_features(input_data['frame_path'])
    x=extract_x(f,config['method'],config['threshold'])
    raw_x=x
    if x is not None and config.get('learned_correction',False):
        import joblib
        x=float(joblib.load(artifact_dir/'ridge_correction.joblib').predict([[x]])[0])
    reasons=[]
    domain=config['input_statistics_domain']
    if f['green_fraction']>domain['max_green_fraction']:
        reasons.append('Backlight-on image outside dark-frame validation domain')
    if not domain['red_pixel_count_min']<=f['red_pixel_count']<=domain['red_pixel_count_max']:
        reasons.append('Luminous-pixel count outside development-frame statistics envelope')
    if x is None:
        reasons.append('No measurable luminous ridge in the specified center band')
    elif x<config['min_x_px'] or x>config['max_x_px']:
        reasons.append('Ridge is near the image boundary or outside validated spatial support')
    value=None if reasons else float(x*calibration['mm_per_px_x'])
    warnings=[]
    if raw_x is not None and config.get('learned_correction',False):
        low,high=config['correction_fit_input_range_px']
        if raw_x<low or raw_x>high:
            warnings.append('Linear correction uses a coordinate outside its development-fit range; later-block error is reported separately, with no cross-experiment guarantee')
    result={'model_id':'model_b','model_version':config['version'],
            'quantity':'luminous_ridge_x_from_image_left','value':value,'unit':'mm',
            'value_kind':'predicted' if config.get('learned_correction',False) else 'derived',
            'position_px':None if reasons else x,
            'raw_extracted_position_px':None if reasons else raw_x,
            'raw_extracted_value_kind':'derived',
            'ood':{'flag':bool(reasons),'reasons':reasons},
            'warnings':warnings,
            'applicable_domain':config['applicable_domain'],
            'uncertainty':None,
            'uncertainty_note':calibration['uncertainty_note'],
            'calibration_nominal':True,
            'interpretation':'Median luminous-ridge position in image rows500:720. This is not a danger score or a prediction for a new burn.'}
    if 'timestamp_ms' in input_data:result['timestamp_ms']=input_data['timestamp_ms']
    return result
