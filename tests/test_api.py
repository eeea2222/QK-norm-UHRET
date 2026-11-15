"""Software integration tests; scientific validity is explicitly deferred."""
from fastapi.testclient import TestClient
import pytest
from qk_norm_blindspot.api import app
from qk_norm_blindspot import analyze_blindspots
client = TestClient(app)


def test_health_reports_catalog_and_deferred_validation():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['rag_enabled'] is False
    assert r.json()['scientific_validation_status'] == 'DEFERRED_BY_REQUEST'


def test_catalog_request_has_no_rag_even_with_legacy_flag():
    r = client.post('/blindspots', json={'question':'What is documented?', 'use_llm':True})
    assert r.status_code == 200
    assert r.json()['rag_enabled'] is False
    assert r.json()['generation_status'] == 'FALLBACK_TEMPLATE'
    assert r.json()['validation']['attempts'] == []


def test_explicit_filter_is_respected():
    r = client.post('/blindspots', json={'question':'Show catalog', 'filters':{'material':'Teflon'}})
    assert r.status_code == 200
    assert r.json()['catalog_records']
    assert all('Teflon' in (x.get('materials') or [x['material']]) for x in r.json()['catalog_records'])


def test_empty_selection_does_not_return_unrelated_priorities():
    r = analyze_blindspots('Show catalog', {'material':'UnlistedMaterial'})
    assert r['analysis_status'] == 'NO_EVIDENCE'
    assert not r['verified_findings'] and not r['research_priorities']


@pytest.mark.parametrize('body', [
    {'question':''}, {'question':'  '},
    {'question':'x','filters':{'year_range':[2025]}},
    {'question':'x','filters':{'year_range':[2025,2018]}},
    {'question':'x','filters':{'material':12}},
    {'question':'x','filters':{'unknown':'x'}},
])
def test_bad_input_returns_422(body):
    assert client.post('/blindspots',json=body).status_code == 422


def test_catalog_and_schema_available():
    assert client.get('/catalog').json()['records']
    assert client.get('/schema').json()['request']['properties']['use_llm']['default'] is False


def test_dashboard_served():
    r = client.get('/')
    assert r.status_code == 200
    assert 'ai-playground' in r.text
    assert client.get('/dashboard_data.json').status_code == 200


def test_model_a_endpoint_real_inference():
    from qk_norm_blindspot.side_panels import model_a_panel
    r = client.post('/models/a',json=model_a_panel()['request'])
    assert r.status_code == 200
    assert r.json()['value_kind'] == 'predicted'


def test_model_b_sample_real_inference():
    r = client.get('/models/b/sample')
    assert r.status_code == 200, r.text
    assert r.json()['response']['value'] == pytest.approx(220.28979111936016)


def test_model_c_rejects_invalid_input():
    assert client.post('/models/c',json={'material':'PMMA'}).status_code == 422


def test_wt4_request_bounded():
    assert client.post('/models/wt4/generate',json={'prompt':'Hi','max_new_tokens':99999}).status_code == 422


def test_dashboard_has_quick_presets_from_recorded_c_conditions():
    import json
    from qk_norm_blindspot import paths
    d=json.loads((paths.DASHBOARD_DIR/'dashboard_data.json').read_text())
    p=d['ai_presets']
    assert set(p)=={'a','b','c','wt4'}
    assert len(p['a'])==2 and len(p['c'])==6 and len(p['wt4'])==2
    assert p['c'][-1]['input']['material']=='Kapton'
    assert 'playground.js' not in client.get('/').text  # JS is inlined for portable dashboard
    assert 'Modeli çalıştır' in client.get('/').text
