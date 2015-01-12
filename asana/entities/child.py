#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Child(object):
	def __init__(self, cls):
		self.cls = cls

	def get_value(self, parent):
		#gotta find a better way to do this
		self.value = parent.get_subitem(self.cls)
