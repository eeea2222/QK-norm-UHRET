import json,struct
from qk_norm_blindspot import paths
from fastapi.testclient import TestClient
from qk_norm_blindspot.api import app

def test_three_models_have_valid_meshes_and_glb_headers():
    for key in ('cabin_transport','optical_detector','aging_chamber'):
        d=paths.DASHBOARD_DIR/'assets/3d'
        mesh=json.loads((d/(key+'.json')).read_text())
        assert mesh['conceptual'] is True
        assert mesh['vertices'] and mesh['faces']
        assert all(0<=i<len(mesh['vertices']) for f in mesh['faces'] for i in f[:3])
        blob=(d/(key+'.glb')).read_bytes()
        assert blob[:4]==b'glTF'
        assert struct.unpack('<I',blob[8:12])[0]==len(blob)

def test_3d_download_and_dashboard_integration():
    c=TestClient(app)
    assert c.get('/assets/3d/cabin_transport.glb').status_code==200
    d=json.loads((paths.DASHBOARD_DIR/'dashboard_data.json').read_text())
    assert len(d['models_3d'])==3
    assert 'models3d' in c.get('/').text
