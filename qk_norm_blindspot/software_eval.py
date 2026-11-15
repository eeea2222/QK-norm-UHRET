"""Execute software checks and retain real pass/fail output. Scientific evaluation is deferred."""
from __future__ import annotations
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from . import paths


def run_eval(**_compat):
    paths.OUTPUTS.mkdir(exist_ok=True)
    xml_path = paths.OUTPUTS / 'software_tests.xml'
    run = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--junitxml', str(xml_path)],
                         cwd=paths.ROOT, capture_output=True, text=True)
    cases = []
    if xml_path.exists():
        for case in ET.parse(xml_path).iter('testcase'):
            failure = case.find('failure')
            error = case.find('error')
            skipped = case.find('skipped')
            node = failure if failure is not None else error
            cases.append({'test':case.get('name'), 'suite':case.get('classname'),
                          'expected':'software assertions pass',
                          'actual':node.text if node is not None else 'assertions passed' if skipped is None else 'skipped',
                          'result':'FAILED' if node is not None else 'SKIPPED' if skipped is not None else 'PASSED'})
    n = sum(c['result'] != 'SKIPPED' for c in cases)
    passed = sum(c['result'] == 'PASSED' for c in cases)
    report = {'evaluation_type':'SOFTWARE_ONLY', 'scientific_validation_status':'DEFERRED_BY_REQUEST',
              'rag_enabled':False, 'exit_code':run.returncode, 'executed':n, 'passed':passed,
              'success_rate': passed/n if n else None, 'tests':cases, 'stdout':run.stdout, 'stderr':run.stderr,
              'scientific_tests_1_to_15':'NOT_RUN_BY_REQUEST'}
    (paths.OUTPUTS/'eval_results.json').write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k not in ('tests','stdout','stderr')}
