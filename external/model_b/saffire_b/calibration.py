"""Derive nominal mapped-camera scale from NASA 30mmBlock checkerboard."""
import numpy as np
from PIL import Image
from .integrity import sha256


def calibrate(grid_path):
    a = np.asarray(Image.open(grid_path).convert('RGB'), dtype=float)
    if a.shape != (1226, 1702, 3):
        raise ValueError('Expected mapped camera-1 1702x1226 calibration image')
    spacings=[]
    for y in [300,400,500,850,950,1050]:
        row=a[y,300:1450,1]
        smooth=np.convolve(row,np.ones(5)/5,mode='same')
        binary=smooth > (np.quantile(smooth,.1)+np.quantile(smooth,.9))/2
        changes=np.flatnonzero(binary[1:]!=binary[:-1])+1
        distances=np.diff(changes)
        spacings.extend(float(x) for x in distances if 45<x<85)
    if len(spacings)<20:
        raise ValueError('Insufficient regular checkerboard transitions')
    px=float(np.median(spacings))
    return {'camera_id':'C1','image_width_px':1702,'image_height_px':1226,
            'nominal_square_mm':30.0,'square_size_provenance':'source_reported_filename_30mmBlock',
            'median_square_width_px':px,'mm_per_px_x':30/px,
            'spacing_count':len(spacings),'spacing_std_px':float(np.std(spacings,ddof=1)),
            'value_kind':'derived','label_provenance':'derived',
            'procedure':'green-channel threshold crossings on six fixed grid scanlines; retain 45-85px spacings; median',
            'source_sha256':sha256(grid_path),
            'uncertainty_note':'Spacing scatter is a repeatability diagnostic, not a full physical calibration uncertainty. Nominal grid square tolerance and mapping systematic error unavailable.'}
