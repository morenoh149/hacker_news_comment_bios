import unittest


class TestGetComments(unittest.TestCase):
    """Example unittest test methods for get_comments"""

    def test_invalid_args(self):
        """Test that the tool complains if a invalid thread id is passed"""
        self.assertEqual(sum((1, 2, 2)), 5, "Should be 6")

    def test_csv_length(self):
        """ Test that the csv file has the correct number of rows """
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()
