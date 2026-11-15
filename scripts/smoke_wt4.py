"""Load real WT4, enforce checksums and tied weights, run one bounded generation."""
import json
from qk_norm_blindspot.wt4 import get_wt4
from qk_norm_blindspot.paths import OUTPUTS
try:
    model = get_wt4()
    result = model.generate('Reply briefly.', 'Say hello.', max_new_tokens=12)
    report = {'status': 'PASSED', 'report': model.report, 'generation': result}
except Exception as exc:
    report = {'status': 'FAILED', 'error': f'{type(exc).__name__}: {exc}'}
OUTPUTS.mkdir(exist_ok=True)
(OUTPUTS / 'wt4_smoke.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['status'] == 'PASSED' else 1)
