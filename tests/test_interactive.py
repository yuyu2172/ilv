import unittest

import os

from ilv.collect_results.interactive import interactive


class TestInteractive(unittest.TestCase):

    def test_interactive(self):
        result_base = 'sample_result'

        obtained = interactive(result_base, 2)

        self.assertEqual(obtained, os.path.join(result_base, 'directory_1'))


