import importlib.util
from pathlib import Path

import pytest

path = Path(__file__).resolve().parents[1]/'scripts/compare_test_baseline.py'
spec = importlib.util.spec_from_file_location('compare_test_baseline', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('body,code,status,key', [
    ('<testcase classname="test.a" name="known"><failure/></testcase>', 0, 'no_new_failures', 'known_failures_still_failing'),
    ('<testcase classname="test.a" name="known"/><testcase classname="test.a" name="new"><failure/></testcase>', 1, 'new_failures', 'new_failures'),
    ('<testcase classname="test.a" name="known"/>', 0, 'no_new_failures', 'previously_failing_now_passed'),
    ('<testcase classname="test.a" name="other"/>', 2, 'incomplete', 'baseline_tests_missing'),
    ('<testcase classname="test.a" name="known"><skipped/></testcase>', 2, 'incomplete', 'baseline_tests_skipped'),
    ('<testcase classname="test.a" name="known"><error/></testcase>', 2, 'incomplete', 'errors'),
])
def test_baseline_comparison_preserves_failures_and_detects_incomplete_runs(tmp_path, body, code, status, key):
    report = tmp_path/'report.xml'
    report.write_text('<testsuites><testsuite>'+body+'</testsuite></testsuites>')
    result, actual = module.compare({'recorded_at':'2026-10-29', 'test_ids':['test.a::known'], 'failures':[{'id':'test.a::known'}]}, report)
    assert actual == code and result['comparison'] == status and result[key]


def test_running_only_known_failures_does_not_count_as_full_comparison(tmp_path):
    report = tmp_path/'partial.xml'
    report.write_text('<testsuite><testcase classname="test.a" name="known"><failure/></testcase></testsuite>')
    baseline = {'recorded_at':'2026-10-29', 'test_ids':['test.a::known','test.a::passed'],
                'failures':[{'id':'test.a::known'}]}
    result, code = module.compare(baseline, report)
    assert code == 2 and result['baseline_tests_missing'] == ['test.a::passed']
