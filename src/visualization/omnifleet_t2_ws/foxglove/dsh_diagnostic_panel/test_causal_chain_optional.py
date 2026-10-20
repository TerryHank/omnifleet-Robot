import unittest

from causal_evidence import validate_chain


class CausalChainOptionalTest(unittest.TestCase):
    def test_unrelated_historical_events_do_not_force_a_chain(self):
        snapshot = {"causal_evidence": {"events": [{"id": "E001"}]}}
        self.assertEqual(validate_chain({"causal_chain": []}, snapshot), [])

    def test_nonempty_chain_still_requires_evidence_for_confirmed_cause(self):
        snapshot = {"causal_evidence": {"events": [{"id": "E001"}]}}
        with self.assertRaisesRegex(ValueError, "confirmed cause needs evidence"):
            validate_chain(
                {
                    "causal_chain": [
                        {
                            "cause": "原因",
                            "effect": "结果",
                            "evidence_ids": [],
                            "confidence": "confirmed",
                        }
                    ]
                },
                snapshot,
            )

    def test_referenced_event_must_exist(self):
        snapshot = {"causal_evidence": {"events": [{"id": "E001"}]}}
        with self.assertRaisesRegex(ValueError, "unsupported evidence reference"):
            validate_chain(
                {
                    "causal_chain": [
                        {
                            "cause": "原因",
                            "effect": "结果",
                            "evidence_ids": ["E999"],
                            "confidence": "hypothesis",
                        }
                    ]
                },
                snapshot,
            )


if __name__ == "__main__":
    unittest.main()
