"""Compare an offline pytest JUnit report without hiding known test failures."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def compare(baseline, report):
    known = {row['id'] for row in baseline['failures']}
    expected = set(baseline['test_ids'])
    cases = list(ET.parse(report).getroot().iter('testcase'))
    present, failed, skipped, errors = set(), set(), set(), []
    for case in cases:
        name = case.get('classname', '') + '::' + case.get('name', '')
        present.add(name)
        if case.find('failure') is not None:
            failed.add(name)
        if case.find('skipped') is not None:
            skipped.add(name)
        if case.find('error') is not None:
            errors.append(name)
    result = {
        'baseline': baseline['recorded_at'],
        'current_test_count': len(cases),
        'known_failures_still_failing': sorted(known & failed),
        'new_failures': sorted(failed - known),
        'previously_failing_now_passed': sorted((known & present) - failed - skipped - set(errors)),
        'baseline_tests_missing': sorted(expected - present),
        'baseline_tests_skipped': sorted(expected & skipped),
        'errors': sorted(errors),
    }
    incomplete = not cases or errors or result['baseline_tests_missing'] or result['baseline_tests_skipped']
    result['comparison'] = 'incomplete' if incomplete else 'new_failures' if result['new_failures'] else 'no_new_failures'
    return result, 2 if incomplete else 1 if result['new_failures'] else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path, help='pytest --junitxml output')
    default = Path(__file__).resolve().parents[4]/'data/test-baselines/dispatch-green-20261029.json'
    parser.add_argument('--baseline', type=Path, default=default)
    args = parser.parse_args()
    result, code = compare(json.loads(args.baseline.read_text()), args.report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
