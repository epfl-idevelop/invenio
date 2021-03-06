# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for WebJournal."""

__revision__ = \
    "$Id$"

# pylint invenio/modules/webjournal/lib/webjournal_tests.py

import unittest

from invenio.webjournal_utils import compare_issues
from invenio.webjournal import issue_is_later_than

#from invenio import webjournal_utils
from invenio.testutils import make_test_suite, run_test_suite
#from invenio.config import CFG_SITE_URL

class TestCompareIssues(unittest.TestCase):
    """Tests for comparing issues."""

    def test_compare_issues(self):
        """webjournal - tests comparing issues"""

        issue1 = '06/2009'
        issue2 = '07/2009'
        self.assertEqual(compare_issues(issue1, issue2), -1)

        issue1 = '07/2009'
        issue2 = '06/2009'
        self.assertEqual(compare_issues(issue1, issue2), 1)

        issue1 = '07/2009'
        issue2 = '07/2009'
        self.assertEqual(compare_issues(issue1, issue2), 0)

        issue1 = '07/2009'
        issue2 = '07/2008'
        self.assertEqual(compare_issues(issue1, issue2), 1)

        issue1 = '07/2008'
        issue2 = '07/2009'
        self.assertEqual(compare_issues(issue1, issue2), -1)

    def test_issue1_is_later_than(self):
        """webjournal - tests comparing issue1 is later than issue2 """
        issue1 = '07/2009'
        issue2 = '07/2008'
        self.assertEqual(issue_is_later_than(issue1, issue2), True)

        issue1 = '07/2008'
        issue2 = '07/2009'
        self.assertEqual(issue_is_later_than(issue1, issue2), False)

        issue1 = '07/2009'
        issue2 = '06/2009'
        self.assertEqual(issue_is_later_than(issue1, issue2), True)

        issue1 = '06/2009'
        issue2 = '07/2009'
        self.assertEqual(issue_is_later_than(issue1, issue2), False)

        issue1 = '07/2009'
        issue2 = '07/2009'
        self.assertEqual(issue_is_later_than(issue1, issue2), False)

TEST_SUITE = make_test_suite(TestCompareIssues)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
