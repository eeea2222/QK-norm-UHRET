from qk_norm_blindspot.benchmarks import build_benchmarks
import statistics
import json
from qk_norm_blindspot import paths

def test_a_median_uses_all_six_alternatives_and_winner_is_minimum():
    b=build_benchmarks()['groups'][0]
    actual=[r for r in b['rows'] if r['value_kind']=='source_reported']
    alternatives=[r['score'] for r in actual if not r['ours']]
    assert len(alternatives)==6
    assert b['rows'][-1]['score']==statistics.median(alternatives)
    assert [r['score'] for r in actual if r['winner']]==[min(r['score'] for r in actual)]

def test_b_keeps_loss_c_keeps_tie_wt4_unranked():
    b=build_benchmarks()['groups']
    assert not next(r for r in b[1]['rows'] if r['ours'])['winner']
    assert len([r for r in b[2]['rows'] if r['winner']])==2
    assert all(r['score'] is None and not r['winner'] for r in b[3]['rows'])
