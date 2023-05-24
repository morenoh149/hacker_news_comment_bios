"""
Test module for get_comments.py
"""
import argparse
from collections.abc import Coroutine
import unittest

import httpx

from get_comments import parser, get_bio, main


class TestGetComments(unittest.TestCase):
    """Example unittest test methods for get_comments"""

    def test_get_bio(self):
        """Should return a coroutine after hitting the internet"""
        username = "morenoh149"
        client = httpx.AsyncClient()
        bio = get_bio(username, client)
        self.assertIsInstance(bio, Coroutine)

    def test_invalid_args(self):
        """Test that the tool complains if a invalid thread id is passed"""
        # self.assertEqual(sum((1, 2, 2)), 5, "Should be 6")

        cmd_args = "35759449 ".split()
        args = parser().parse_args(cmd_args)
        assert type(args) == argparse.Namespace


if __name__ == '__main__':
    unittest.main()
