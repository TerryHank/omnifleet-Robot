import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import skill_context


class SkillContextTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        for relative in skill_context.AIRY_FILES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("content:" + relative, encoding="utf-8")
        self.env = patch.dict(os.environ, {"OMNIFLEET_AIRY_SKILL_ROOT": str(root)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def test_airy_question_loads_complete_read_only_skill(self):
        context, names, errors = skill_context.diagnostic_skill_context(
            "Airy 有 UDP 包但 ROS 没有点云，怎么排查？"
        )
        self.assertEqual(names, ["airy"])
        self.assertEqual(errors, [])
        self.assertIn("不得据此自动写设备", context)
        for relative in skill_context.AIRY_FILES:
            self.assertIn("airy/" + relative, context)

    def test_unrelated_navigation_question_does_not_load_skill(self):
        self.assertEqual(
            skill_context.diagnostic_skill_context("为什么多点导航目标失败？"),
            ("", [], []),
        )

    def test_incomplete_skill_is_not_partially_injected(self):
        (Path(os.environ["OMNIFLEET_AIRY_SKILL_ROOT"]) / "patterns.md").unlink()
        context, names, errors = skill_context.diagnostic_skill_context("雷达飞点")
        self.assertEqual((context, names), ("", []))
        self.assertIn("airy: missing patterns.md", errors)


if __name__ == "__main__":
    unittest.main()
