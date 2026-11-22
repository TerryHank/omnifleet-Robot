import unittest

try:
    from omnifleet_waypoint_ui.navigation_error_dictionary import NAVIGATION_ERROR_MAP, lookup_navigation_error
except ModuleNotFoundError:
    from navigation_error_dictionary import NAVIGATION_ERROR_MAP, lookup_navigation_error


class NavigationErrorDictionaryTest(unittest.TestCase):
    def test_known_errors(self):
        cases = {
            "deviated from ordered route; stopped without shortcut replanning": "ordered_route_deviation",
            "Goal failed": "goal_failed",
            "Goal faild": "goal_failed",
            "stale localization transform: age_ms=538": "stale_localization",
            "initial localization stability timeout": "initial_localization_timeout",
            "global costmap not fresh": "global_costmap_stale",
            "remaining route planning failed": "remaining_route_planning_failed",
            "planned path does not visit ordered goals": "ordered_goals_not_visited",
            "path ended before ordered waypoint verification": "path_ended_early",
            "Starting point in lethal space": "start_blocked",
            "Failed to make progress": "progress_timeout",
            "到点安全检查失败：车身覆盖真实障碍": "goal_safety_check_failed",
            "取消未确认，已停止发后续段": "cancel_unconfirmed",
            "navigation失败：action状态=6": "path_tracking_failed",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(lookup_navigation_error(raw)["code"], expected)

    def test_every_entry_has_user_facing_fields(self):
        for code, entry in NAVIGATION_ERROR_MAP.items():
            with self.subTest(code=code):
                self.assertTrue(entry["patterns"])
                self.assertTrue(entry["title"])
                self.assertTrue(entry["meaning"])
                self.assertTrue(entry["action"])

    def test_unknown_error_has_fallback_and_normal_status_is_ignored(self):
        self.assertEqual(
            lookup_navigation_error("某个新导航模块失败：尚未登记")["code"],
            "unclassified_navigation_error",
        )
        self.assertIsNone(lookup_navigation_error("系统已就绪，可以开始导航"))


if __name__ == "__main__":
    unittest.main()
