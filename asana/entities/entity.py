#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re

class EntityException(Exception):
    """Wrap entity specific errors"""
    pass

class Entity(object):
	"""Base implementation for an Asana entity containing
	common funcitonality"""

	# Keys which are filtered as part of the HTTP request
	_filter_keys = []

	#fields this object has. This affects what is returned from the Asana API
	#as well as serving as a lookup for lazy-loading
	_fields = []

	#define regex to match field names that should be wrapped with an instance
	#of this object
	_matchons = []

	#items that are sub-items of the current one such that the API endpoint is
	#/api/parent/<id>/subitme
	_children = {}

	def __init__(self, data):
		self._childrenValues = {}
		self._init(data)
		self._ready = True

	def _init(self, data, merge=False):
		"""Initializes this entity, either with entirely new data or with an
		update to be merged with the current data

		:param data: the data to use for the entity
		:param merge: if true only set keys from data that aren't already set
			internally
		"""
		if merge:
			for key, value in data.items():
				if key not in self._data or key == 'id':
					self._data[key] = value
		else:
			self._data = data
			self._dirty = set()

		#todo it would probably be better to subclass
		# dict and implement this in there
		for key in self._data:
			if not self._data[key]:
				continue

			for regex, cls in self._matchons.items():
				if re.search(regex, key):
					if isinstance(self._data[key], list):
						for idx, val in enumerate(self._data[key]):
							if isinstance(val, dict):
								self._data[key][idx] = cls(val)
					else:
						if isinstance(self._data[key], dict):
							self._data[key] = cls(self._data[key])

					break

	@classmethod
	def set_api(cls, api):
		cls.api = api

	@classmethod
	def from_link(cls, link):
		"""Builds an object from a link to it
		This works by assuming the last section of the link is the ID"""
		
		if not link:
			return None

		return cls({'id': link.split('/')[-1]})

	@classmethod
	def _get_api(cls):
		if not cls.api:
			raise EntityException('The api must be set using Entity.set_api()')

		return cls.api

	@classmethod
	def _get_api_endpoint(cls):
		"""By default use name of class for endpoint"""
		return cls.__name__.lower() + 's'

	def _get_item_url(self):
		if not self.id:
			raise EntityException('Cannot get item URL without id set')

		return '/'.join([self._get_api_endpoint(), str(self.id)])

	@classmethod
	def find(cls, query={}):
		"""Find objects of this type that fit query

		:param query: dict of key/value pairs to match against. keys that the
			API natively handles are sent as part of the request if they have
			scalar values, other keys are filtered from the response.
			filter values can be either absolute values or lambdas. for lambdas
			the value of its key will be passed as the only argument and it
			will be considered passing if the lambda returns true
		"""
		return cls._run_find(cls._get_api_endpoint(), query)

	@classmethod
	def _run_find(cls, target, query):
		params = cls._get_default_params() #params that are part of the request

		#todo handle lambdas that are passed in for filter keys
		if cls._filter_keys:
			for key in query.keys():
				if key in cls._filter_keys:
					params[key] = query[key]
					del query[key]

		data = cls._get_api().get(target, params=params)

		return cls._build_result(query, data)

	@classmethod
	def _get_default_params(cls):
		"""Hook to add params that will always be part of a find request
		Default behavior checks for the 'fields' property and, if present,
		joins it with commas and passes it as the opt_fields param
		"""
		if cls._fields:
			return {
				'opt_fields': ','.join(cls._fields)
			}

		return {}

	@classmethod
	def _build_result(cls, query, data):
		"""Filters the result set based on a query returning the resulting
		objects as instances of the current class"""
		
		return [cls(ent) for ent in data if cls._filter_result_item(ent, query)]

	@classmethod
	def _filter_result_item(cls, entity, query):
		"""Filters a single entity dict against a dict of allowed values
		returning true if it passes
		"""

		for key, value in query.items():
			if key not in entity:
				raise EntityException('The key {0} is not a valid query for {1}'.format(key, cls.__name__))

			if (
				(callable(value) and not value(entity[key])) or
				(isinstance(value, basestring) and value != entity[key])
			):
				return False
		return True

	def load(self):
		"""Loads all of this items data using its ID"""

		#TODO check if sending in empty opt_fields will make us lose all fields
		self._init(self._get_api().get(self._get_item_url()), merge=True)

		return self

	def get_subitem(self, subitem_class, query={}):
		target = '/'.join([self._get_item_url(), subitem_class._get_api_endpoint()])

		return subitem_class._run_find(target, query)

	def save(self):
		"""Handles both creating and updating content
		The assumption is if there is no ID set this is
		a creation request
		"""

		if self.id:
			return self._do_update()
		else:
			#performing create - post
			return self._do_create()

	def _do_update(self):
		data = {}

		for key in self._dirty:
			data[key] = self._data[key]

		if not data:
			return

		return self._get_api().put(self._get_item_url(), data=data)

	def _do_create(self):
		return self._init(self._get_api().post(self._get_api_endpoint(), data=self._data))

	def delete(self):
		"""Deletes the specified resource. The ID must be set"""

		self._get_api().delete(self._get_item_url())

	def __getattr__(self, attr):

		if attr in self.__dict__:
			return self.__dict__[attr]

		if attr in self.__dict__['_data']:
			return self.__dict__['_data'][attr]

		if attr in self._fields:
			self.load()
			return self.__dict__['_data'][attr]


		if attr in self._children.keys():

			if not attr in self._childrenValues.keys():
				self._childrenValues[attr] = self.get_subitem(self._children[attr])

			return self._childrenValues[attr]

		if attr != 'id':
			#todo throw standard exception for no property
			raise Exception("Could not locate key " + attr)

	def __setattr__(self, attr, value):
		if attr[0] == '_':
			self.__dict__[attr] = value
		elif self._ready:

			if attr in self._fields:
				self._data[attr] = value
				self._dirty.add(attr)
			else:
				raise Exception("Cannot set attribute {0} - unknown name".foramt(attr))

	def __str__(self):
		return vars(self).__repr__()

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		return hash(self.id if hasattr(self, 'id') else frozenset(self._data.items()))

	def __eq__(self, other):
		if type(self) is not type(other):
			return False

		if self.id:
			return self.id == other.id
		else:
			return cmp(self._data, other._data) == 0
