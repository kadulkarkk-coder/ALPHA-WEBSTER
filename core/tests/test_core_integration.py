"""Integration tests for Webster's repaired command routing path."""
from __future__ import annotations

import unittest

from core.ai.router import IntentRouter, IntentType
from core.planning.analyzer import GoalAnalyzer
from core.planning.decomposer import TaskDecomposer
from core.planning.goal import Goal
from core.vision.analyzer import VisionAnalyzer
from core.vision.capture import VisionCapture
from core.vision.manager import VisionManager
from core.vision.types import VisionFrame, VisionSource


class FakeScreenProvider:
    def capture(self) -> VisionFrame:
        return VisionFrame(
            source=VisionSource.SCREEN,
            data=b"png-placeholder",
            width=1920,
            height=1080,
            format="png",
            metadata={"provider": "fake"},
        )


class CoreIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.router = IntentRouter()

    def test_plain_filename_delete_routes_to_delete_capability(self):
        intent = self.router.route("delete read.txt")
        self.assertEqual(intent.intent, IntentType.FILE)
        self.assertEqual(intent.action, "delete_file")

        goal = Goal(objective="delete read.txt")
        analysis = GoalAnalyzer().analyze(goal)
        self.assertEqual(analysis.required_capabilities, ("delete_file",))

        task = TaskDecomposer().create_task(goal, "delete_file")
        self.assertEqual(task.arguments["path"], "read.txt")

    def test_open_google_normalizes_to_google_domain(self):
        task = TaskDecomposer().create_task(Goal(objective="open google"), "open_url")
        self.assertEqual(task.arguments["url"], "https://google.com")

    def test_vision_commands_route_to_real_actions(self):
        self.assertEqual(self.router.route("activate vision").action, "vision_enable")
        self.assertEqual(self.router.route("vision status").action, "vision_status")
        self.assertEqual(self.router.route("can you see my screen").action, "vision_screen")

    def test_vision_manager_is_disabled_until_activated(self):
        manager = VisionManager(
            capture=VisionCapture(screen_provider=FakeScreenProvider()),
            analyzer=VisionAnalyzer(),
        )
        self.assertFalse(manager.enabled)
        with self.assertRaises(RuntimeError):
            manager.capture_and_analyze_screen()
        manager.enabled = True
        result = manager.capture_and_analyze_screen()
        self.assertEqual(result.source, VisionSource.SCREEN)
        self.assertEqual(result.metadata["width"], 1920)
        self.assertEqual(result.metadata["height"], 1080)


if __name__ == "__main__":
    unittest.main()
