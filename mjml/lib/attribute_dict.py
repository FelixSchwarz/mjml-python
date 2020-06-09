# -*- coding: UTF-8 -*-

# License: Public Domain
# Authors: Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Version 1.2
#
# 1.2 (2018-02-16)
#   - split tests into separate file
#   - add ".copy()" method
#
# 1.1 (08.09.2015)
#   - set items via attributes
#
# 1.0 (06.02.2010)
#   - initial release


__all__ = ['AttrDict']

class AttrDict(dict):
    def copy(self):
        return AttrDict(self)

    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        return self[name]

    def __setattr__(self, name, value):
        if name not in self:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        self[name] = value
