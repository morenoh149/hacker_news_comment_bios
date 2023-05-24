"""
Test module for get_comments.py
"""
import argparse
from collections.abc import Coroutine
import unittest

import httpx

from get_comments import parser, get_bio   # pylint: disable=import-error


class TestGetComments(unittest.TestCase):
    """Example unittest test methods for get_comments"""

    def test_get_bio(self):
        """Should return a coroutine after hitting the internet"""
        username = "morenoh149"
        client = httpx.AsyncClient()
        bio = get_bio(username, client)
        self.assertIsInstance(bio, Coroutine)

    def test_valid_args(self):
        """Test that the tool accepts valid story_id"""
        cmd_args = "35759449 ".split()
        args = parser().parse_args(cmd_args)
        assert isinstance(args, argparse.Namespace)

    def test_invalid_args(self):
        """Test that the tool complains about invalid story_id"""
        cmd_args = "abc ".split()
        try:
            parser().parse_args(cmd_args)
            return True
        except SystemExit:
            return False


if __name__ == '__main__':
    unittest.main()
