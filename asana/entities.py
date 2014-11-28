#!/usr/bin/env python

import re

class EntityException(Exception):
    """Wrap entity specific errors"""
    pass

class Entity(object):
	"""Base implementation for an Asana entity containing
	common funcitonality"""

	_filter_keys = []
	_fields = []
	_matchons = []

	def __init__(self, data):
		self._init(data)
		self._ready = True

	def _init(self, data, merge=False):
		if merge:
			for key, value in data.items():
				if key not in self._data:
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
							self._data[key][idx] = cls(val)
					else:
						self._data[key] = cls(self._data[key])

					break

	@classmethod
	def set_api(cls, api):
		cls.api = api

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
		return cls._run_find(cls._get_api_endpoint(), query)

	@classmethod
	def _run_find(cls, target, query):
		params = cls._get_default_params() #params that are part of the request

		if cls._filter_keys:
			for key in query.keys():
				if key in cls._filter_keys:
					params[key] = query[key]
					del query[key]

		data = cls._get_api().get(target, params=params)

		return cls._build_result(query, data)

	@classmethod
	def _get_default_params(cls):
		if cls._fields:
			return {
				'opt_fields': ','.join(cls._fields)
			}

		return {}

	@classmethod
	def _build_result(cls, query, data):
		"""Filters the result set based on a query returning the resulting
		objects as instances of the current class"""
		
		return [cls(ent) for ent in data if cls._filter(ent, query)]

	@classmethod
	def _filter(cls, entity, query):
		"""Filters a single entity dict against a dict of allowed values
		returning true if it passes"""

		for key, value in query.items():
			if key not in entity:
				raise EntityException('The key {} is not a valid query for {}'.format(key, cls.__name__))

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
		a creation request"""

		if self.id:
			#performing update - put
			pass
		else:
			#performing create - post
			pass

	def delete(self):
		"""Deletes the specified resource. The ID must be set"""

		self.get_api().delete(self._get_item_url())

	def __getattr__(self, attr):

		if attr in self.__dict__:
			return self.__dict__[attr]

		if attr in self.__dict__['_data']:
			return self.__dict__['_data'][attr]

	def __setattr__(self, attr, value):
		if attr[0] == '_':
			self.__dict__[attr] = value
		elif self._ready:
			self._data[attr] = value
			self._dirty.add(attr)

	def __str__(self):
		return vars(self).__repr__()

	def __repr__(self):
		return self.__str__()

class Project(Entity):
	_matchon = 'project'

class User(Entity):
	_matchon = 'assignee|followers|_by'

class Tag(Entity):
	pass

class Task(Entity):
	_filter_keys = [
		'project', 'assignee', 'workspace', 'completed_since', 'modified_since'
	]

	_fields = [
		'assignee','created_by','created_at','completed','completed_at',
		'followers','modified_at','name','notes','projects','parent',
		'workspace','tags'
	]

class Story(Entity):

	@classmethod
	def _get_api_endpoint(cls):
		return 'stories'

class Section(Entity):
	_filter_keys = Task._filter_keys

	@classmethod
	def _get_api_endpoint(cls):
		return Task._get_api_endpoint()

	@classmethod
	def _build_result(cls, query, data):
		current = None
		filling = False
		ret = []

		for ent in data:
			if cls._is_section(ent):
				if current:
					ret.append(cls(current))
					current = None

				if cls._filter(ent, query):
					current = ent
					current['subtasks'] = []
			elif current:
				current['subtasks'].append(Task(ent))

		if current:
			ret.append(cls(current))

		return ret

	@staticmethod
	def _is_section(ent):
		"""Checks whether a dict from the API is a section Task

		:param ent: The dict to check
		"""
		return ent['name'][-1] == ':'

	def get_subitem(self, subclass, query):
		raise EntityException('This function does not apply to sections, try the subtasks property')