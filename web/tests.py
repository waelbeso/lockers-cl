"""Test module placeholder for Django's test discovery."""

import unittest

try:
    from django.test import TestCase  # type: ignore
except ImportError:  # pragma: no cover - Django not installed in CI image
    TestCase = unittest.TestCase


class PlaceholderTest(TestCase):
    """Minimal test case to ensure the module imports cleanly."""

    def test_placeholder(self):
        self.assertTrue(True)
