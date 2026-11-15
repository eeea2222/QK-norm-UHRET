"""Local API and dashboard: python -m uvicorn qk_norm_blindspot.api:app --port 8005."""
from __future__ import annotations
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from .agent import analyze_blindspots
from .schema import REQUEST_JSON_SCHEMA, RESPONSE_JSON_SCHEMA
from . import paths

app = FastAPI(title='QK norm BlindSpot — structured catalog', version='0.2.0')
_model_lock = threading.Lock()

class BlindspotRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    question: str = Field(min_length=1, max_length=4000)
    filters: dict | None = None
    use_llm: bool = False

class WT4Request(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prompt: str = Field(min_length=1, max_length=6000)
    max_new_tokens: int = Field(default=128, ge=1, le=512)

@app.post('/blindspots')
def blindspots(req: BlindspotRequest) -> dict:
    try:
        return analyze_blindspots(req.question, req.filters, use_llm=req.use_llm)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(503, detail=f'Catalog unavailable: {exc}') from exc

@app.get('/health')
def health():
    return {'status': 'ok', 'engine': 'STRUCTURED_CATALOG', 'rag_enabled': False,
            'scientific_validation_status': 'DEFERRED_BY_REQUEST'}

@app.get('/schema')
def schema():
    return {'request': REQUEST_JSON_SCHEMA, 'response': RESPONSE_JSON_SCHEMA}

@app.get('/catalog')
def catalog():
    from .store import get_store
    s = get_store()
    return {'records': s.records, 'gaps': s.gaps, 'priorities': s.priorities, 'profiles': s.profiles,
            'scientific_validation_status': 'DEFERRED_BY_REQUEST'}

@app.post('/models/a')
def model_a(request: dict):
    from .side_panels import model_a_panel
    try:
        return model_a_panel(request)
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, detail=str(exc)) from exc

@app.get('/models/b/sample')
def model_b():
    from .side_panels import model_b_panel
    try:
        result = model_b_panel(timeout=60)
        if result.get('status') == 'FAILED':
            raise RuntimeError(result.get('stderr', 'Model B failed'))
        return result
    except Exception as exc:
        raise HTTPException(503, detail=str(exc)) from exc

@app.post('/models/c')
def model_c(request: dict):
    from .model_c import predict
    try:
        return predict(request)
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, detail=str(exc)) from exc

@app.post('/models/wt4/generate')
def wt4(req: WT4Request):
    from .wt4 import get_wt4
    try:
        with _model_lock:
            model = get_wt4()
            result = model.generate('Respond concisely. Do not invent scientific claims or numbers.',
                                    req.prompt, max_new_tokens=req.max_new_tokens)
        return {'model': 'WeightSeek-WT4', 'value_kind': 'predicted', 'use_as_evidence': False,
                'rag_enabled': False, 'generation': result, 'model_report': model.report}
    except Exception as exc:
        raise HTTPException(503, detail=f'WT4 unavailable: {exc}') from exc

@app.get('/')
def dashboard():
    p = paths.DASHBOARD_DIR / 'index.html'
    if not p.exists():
        raise HTTPException(503, detail='Run python -m qk_norm_blindspot dashboard')
    return FileResponse(p, headers={"Cache-Control": "no-store, max-age=0", "Pragma": "no-cache"})

@app.get('/dashboard_data.json')
def dashboard_data():
    return FileResponse(paths.DASHBOARD_DIR / 'dashboard_data.json', headers={'Cache-Control':'no-store'})

app.mount("/assets", StaticFiles(directory=str(paths.DASHBOARD_DIR / "assets"), check_dir=False), name="assets")
