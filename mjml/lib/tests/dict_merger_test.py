# -*- coding: UTF-8 -*-
# Copyright 2015 Felix Schwarz
# The source code in this file is licensed under the MIT license.

from ..dict_merger import merge_dicts


def test_returns_single_dict_unmodified():
    assert merge_dicts({}) == {}
    assert merge_dicts({'bar': 42}) == {'bar': 42}

def test_can_merge_two_dicts_without_modifying_inputs():
    a = {'a': 1}
    b = {'b': 2}
    assert merge_dicts(a, b) == {'a': 1, 'b': 2}

def test_can_merge_three_dicts_without_modifying_inputs():
    a = {'a': 1}
    b = {'b': 2}
    c = {'c': 3}
    assert merge_dicts(a, b, c) == {'a': 1, 'b': 2, 'c': 3}
