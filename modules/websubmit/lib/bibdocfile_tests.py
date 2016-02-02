# -*- coding: utf-8 -*-

"""Unit tests for BibDocFile."""

__revision__ = \
    "$Id$"

import unittest

from invenio import bibdocfile
from invenio.testutils import make_test_suite, run_test_suite


class TestFormatNormalization(unittest.TestCase):
    """Test for handling of & and unicode."""

    def test_base(self):
        self.assertEqual(".format", bibdocfile.normalize_format(".format"))

    def test_ampersand(self):
        self.assertEqual(".format", bibdocfile.normalize_format(".format&suffix"))

    def test_unicode(self):
        self.assertEqual(".\xca\xac", bibdocfile.normalize_format(u".ʬ"))

    def test_unicode_subformat(self):
        self.assertEqual(".format;\xca\xac", bibdocfile.normalize_format(u".format;ʬ"))

TEST_SUITE = make_test_suite(TestFormatNormalization)


if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
