# -*- coding: UTF-8 -*-
# Copyright 2015 Felix Schwarz
# The source code in this file is licensed under the MIT license.


__all__ = ['merge_dicts']

def merge_dicts(*sources):
    # initial code from
    #    Robin Bryce, Tue, 19 Dec 2006
    #    PSF license
    #    http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/
    result = {}
    for source in sources:
        stack = [(source, result)]
        while stack:
            current_src, current_dst = stack.pop()
            for key in (current_src or ()):
                src_item_is_dict = isinstance(current_src.get(key), dict)
                dst_item_is_dict = isinstance(current_dst.get(key), dict)
                if src_item_is_dict and dst_item_is_dict:
                    stack.append((current_src[key], current_dst[key]))
                else:
                    current_dst[key] = current_src[key]
    return result

