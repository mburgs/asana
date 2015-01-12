#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Child(object):
	def __init__(self, cls):
		self.cls = cls

	def get_value(self, parent):
		return parent.get_subitem(self.cls)
