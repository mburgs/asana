#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import *

class Child(object):
	def __init__(self, key, *pargs, **kwargs):

		self.value = None
		self.loaded = False

		if 'class' in kwargs:
			self.cls = kwargs['class']
		else:
			self.cls = key[:-1].title()

	def is_loaded(self):
		return self.loaded

	def load_value(self, parent):
		self.value = parent.get_subitem(globals()[self.cls])
		self.loaded = True