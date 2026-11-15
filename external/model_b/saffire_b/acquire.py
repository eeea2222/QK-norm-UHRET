"""NASA PSI-98 public v4 catalog acquisition; no login or credentials."""
import json
import shutil
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .integrity import sha256

API = 'https://psi.nasa.gov/geode-py/ws'


def request_json(url, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {'User-Agent': 'Saffire-I-reproducible-audit/0.1'}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    with urlopen(Request(url, data=data, headers=headers), timeout=90) as response:
        return json.load(response)


def catalog(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = request_json(f'{API}/studies/PSI-98/metadata')
    files = request_json(f'{API}/files/v2', {
        'folder': 'PSI-98/', 'fileType': 'study', 'studyId': 'PSI-98', 'version': 4})
    for name, value in [('metadata.json', metadata), ('files_v2.json', files)]:
        (output_dir / name).write_text(json.dumps(value, indent=2) + '\n')
    return metadata, files


def download_file(entry, output_dir, expected_sha256=None):
    """Resolve a fresh temporary URL, save bytes atomically, verify pinned content."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / Path(entry['key']).name
    if not target.exists():
        query = urlencode({'file': entry['id'], 'version': entry['version'],
                           'studyVersion': 4, 'redirect': 'false'})
        with urlopen(f'{API}/studies/PSI-98/download?{query}', timeout=90) as response:
            signed_url = response.read().decode().strip().strip('"')
        if not signed_url.startswith('https://'):
            raise ValueError('NASA returned no HTTPS download URL')
        partial = target.with_suffix(target.suffix + '.partial')
        with urlopen(signed_url, timeout=180) as response, partial.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        if 'bytes_size' in entry and partial.stat().st_size != int(entry['bytes_size']):
            partial.unlink()
            raise ValueError('NASA file size mismatch')
        partial.replace(target)
    checksum = sha256(target)
    if expected_sha256 and checksum != expected_sha256:
        raise ValueError(f'NASA content differs from pinned source: {target.name}')
    return {'path': str(target), 'sha256': checksum, 'bytes': target.stat().st_size,
            'study_id': 'PSI-98', 'study_version': 4, 'file_id': entry['id'],
            'file_version': entry['version'], 'key': entry['key']}
