"""
Test module for get_comments.py
"""
import unittest

import httpx

target = __import__("get_comments.py", "23423423")
"""
returns error

✗ python test.py
usage: Download HackerNews comments [-h] story_id
Download HackerNews comments: error: the following arguments are required: story_id
"""
parse_args = target.parse_args
get_bio = target.get_bio

class TestGetComments(unittest.TestCase):
    """Example unittest test methods for get_comments"""

    def test_get_bio(self):
        """Should return a string after hitting the internet"""
        username = "morenoh149"
        client = httpx.AsyncClient()
        bio = get_bio(username, client)
        self.assertIsInstance(bio, str)
    # def test_invalid_args(self):
    #     """Test that the tool complains if a invalid thread id is passed"""
    #     self.assertEqual(sum((1, 2, 2)), 5, "Should be 6")

    # def test_csv_length(self):
    #     """ Test that the csv file has the correct number of rows """
    #     usernames = ["morenoh149", "patio11", "abtinf", "TheCoelacanth"]
    #     self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()
