# -*- coding: UTF-8 -*-
# Copyright 2015 Felix Schwarz
# The source code in this file is licensed under the MIT license.

from pythonic_testcase import *

from ..dict_merger import merge_dicts

class DictMergerTest(PythonicTestCase):
    def test_returns_single_dict_unmodified(self):
        assert_equals({}, merge_dicts({}))
        assert_equals({'bar': 42}, merge_dicts({'bar': 42}))

    def test_can_merge_two_dicts_without_modifying_inputs(self):
        a = {'a': 1}
        b = {'b': 2}
        assert_equals({'a': 1, 'b': 2}, merge_dicts(a, b))

    def test_can_merge_three_dicts_without_modifying_inputs(self):
        a = {'a': 1}
        b = {'b': 2}
        c = {'c': 3}
        assert_equals({'a': 1, 'b': 2, 'c': 3}, merge_dicts(a, b, c))

