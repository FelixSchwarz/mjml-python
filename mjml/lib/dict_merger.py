# -*- coding: UTF-8 -*-
# Copyright 2015 Felix Schwarz
# The source code in this file is licensed under the MIT license.

from typing import Any


__all__ = ["merge_dicts"]

def merge_dicts(*sources: dict[str, Any]) -> dict[str, Any]:
    # initial code from
    #    Robin Bryce, Tue, 19 Dec 2006
    #    PSF license
    #    http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/
    result: dict[str, Any] = {}
    for source in sources:
        stack = [(source, result)]
        while stack:
            current_src, current_dst = stack.pop()
            for key in (current_src or ()):
                src_item = current_src.get(key)
                dst_item = current_dst.get(key)
                if isinstance(src_item, dict) and isinstance(dst_item, dict):
                    stack.append((src_item, dst_item))
                else:
                    current_dst[key] = src_item
    return result
