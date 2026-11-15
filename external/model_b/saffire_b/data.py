"""Deterministic original-member acquisition, integrity checks and metadata preparation."""
import csv,json,zipfile
import numpy as np
from PIL import Image
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from .acquire import API,download_file
from .remote_zip import RangeReader
from .integrity import sha256
from .inference import image_features


def prepare(root, cache_dir=None, frame_subdir='frames'):
    root=Path(root)
    manifest=json.loads((root/'data/source_manifest.json').read_text())
    frame_dir=root/'data'/frame_subdir
    frames=json.loads((frame_dir/'frames.json').read_text())
    entries={Path(e['key']).name:e for e in manifest['files']}
    by_archive={}
    for row in frames:by_archive.setdefault(row['source_archive'],[]).append(row)
    for archive,rows in by_archive.items():
        missing=[r for r in rows if not (frame_dir/r['filename']).exists()]
        if not missing:continue
        e=entries[archive]
        cached=Path(cache_dir)/archive if cache_dir else root/'data/raw/audit'/archive
        if cached.is_file() and cached.stat().st_size==int(e['bytes_size']):
            if sha256(cached)!=e['sha256']:raise ValueError('Cached archive checksum mismatch')
            reader=cached
        else:
            query=urlencode({'file':e['id'],'version':e['version'],'studyVersion':4,'redirect':'false'})
            with urlopen(f'{API}/studies/PSI-98/download?{query}',timeout=90) as response:
                url=response.read().decode().strip()
            reader=RangeReader(url,int(e['bytes_size']))
        with zipfile.ZipFile(reader) as z:
            for row in missing:
                # zipfile validates each original member's CRC before returning bytes.
                b=z.read(row['source_member']);dest=frame_dir/row['filename']
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
                if sha256(dest)!=row['sha256']:raise ValueError('Original frame checksum mismatch')
    calibration_entry=next(e for e in manifest['files'] if Path(e['key']).name=='PSI-98_Raw Data_Mapped_SAFFIRE-1_F1C1_DistortionGrid_1280x920.zip')
    calibration_path=root/'data/calibration'/manifest['calibration_member']
    if not calibration_path.exists():
        info=download_file(calibration_entry,root/'data/raw/audit',calibration_entry['sha256'])
        with zipfile.ZipFile(info['path']) as z:
            calibration_path.parent.mkdir(parents=True,exist_ok=True)
            calibration_path.write_bytes(z.read(manifest['calibration_member']))
    if sha256(calibration_path)!=manifest['calibration_member_sha256']:raise ValueError('Calibration member checksum mismatch')
    rows=[];seen={};last=None;previous_hash=None
    for row in frames:
        path=frame_dir/row['filename']
        if sha256(path)!=row['sha256']:raise ValueError(f'Frame content changed: {path.name}')
        f=image_features(path)
        with Image.open(path) as image:
            tiny=np.asarray(image.convert('L').resize((9,8)),dtype=int)
        dhash=int(''.join('1' if b else '0' for b in (tiny[:,1:]>tiny[:,:-1]).ravel()),2)
        hamming=None if previous_hash is None else (dhash^previous_hash).bit_count()
        ts=int(path.stem.rsplit('-',1)[1])
        if ts!=row['timestamp_ms']:raise ValueError('Filename timestamp mismatch')
        if last is not None and ts<=last:raise ValueError('Unordered or duplicate timestamp')
        rows.append({'frame_id':row['frame_id'],'burn_id':row['burn_id'],'sample_id':row['sample_id'],
            'dependency_group':row['sample_id'],'timestamp_ms':ts,'time_s':row['time_s'],
            'sha256':row['sha256'],'exact_duplicate_of':seen.get(row['sha256'],''),
            'adjacent_dhash_hamming':hamming,'near_duplicate_flag':hamming is not None and hamming<=5,
            'temporally_correlated':True,'near_duplicate_policy':'All frames share one sample; time-block splits with 20s nominal gap. No independent-frame claim.',
            'green_fraction':f['green_fraction'],'red_pixel_count':f['red_pixel_count']})
        seen[row['sha256']]=row['frame_id'];last=ts;previous_hash=dhash
    proc=root/'data/processed';proc.mkdir(exist_ok=True)
    with (proc/f'{frame_subdir}.csv').open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'Acquisition and preprocessing verified: {len(rows)} original frames')
    return calibration_path
