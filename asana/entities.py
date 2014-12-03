#!/usr/bin/env python

import json
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
		"""Initializes this entity, either with entirely new data or with an
		update to be merged with the current data

		:param data: the data to use for the entity
		:param merge: if true only set keys from data that aren't already set
			internally
		"""
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

	def __hash__(self):
		return hash(self.id if hasattr(self, 'id') else frozenset(self._data.items()))

	def __eq__(self, other):
		return self.id == other.id if hasattr(self, 'id') else cmp(self._data, other._data)

class Project(Entity):
	_matchon = 'project'

	_fields = ['name', 'workspace', 'team']

	def add_task(self, task):
		"""Adds a new task to this project, if the task is already created
		then proxies to Task.add_project

		:param task: task to add to project
		"""

		if task.id:
			task.add_project(self)
		else:
			task.projects = [self.id]
			task.workspace = self.workspace['id']

			task.save()

class User(Entity):
	_matchon = 'assignee^|followers|_by'

class Tag(Entity):
	pass

class Task(Entity):
	_matchon = 'task'

	_filter_keys = [
		'project', 'assignee', 'workspace', 'completed_since', 'modified_since'
	]

	_fields = [
		'assignee','created_by','created_at','completed','completed_at',
		'followers','modified_at','name','notes','projects','parent',
		'workspace'
	]

	@classmethod
	def _filter_result_item(cls, entity, query):
		if Section._is_section(entity):
			return False

		return super(Task, cls)._filter_result_item(entity, query)

	def add_project(self, projectOrId):
		"""Adds this task to a project

		:param projectOrId Either the project object or a project ID
		"""
		return self._edit_project('addProject', projectOrId)

	def remove_project(self, projectOrId):
		"""Removes this task from a project

		:param projectOrId Either the project object or a project ID
		"""
		return self._edit_project('removeProject', projectOrId)

	def _edit_project(self, operation, projectOrId):
		pId = projectOrId.id if isinstance(projectOrId, Project) else projectOrId

		return self._get_api().post(
			'/'.join([self._get_item_url(), operation]),
			data={'project':pId}
		)

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
		"""We need custom result building for sections to figure out which in
		the reuslt set are sections and which are tasks - the results are
		returned in order so every task after a section until the next section
		is considered a subtask
		"""
		current = None
		filling = False
		ret = []

		for ent in data:
			if cls._is_section(ent):
				if current:
					ret.append(cls(current))
					current = None

				if cls._filter_result_item(ent, query):
					current = ent
					current['subtasks'] = []
			elif current:
				current['subtasks'].append(ent)

		if current:
			ret.append(cls(current))

		return ret

	@staticmethod
	def _is_section(ent):
		"""Checks whether a dict from the API is a section Task

		:param ent: The dict to check
		"""
		return ent['name'] and ent['name'][-1] == ':'

	def get_subitem(self, subclass, query):
		raise EntityException('This function does not apply to sections, try the subtasks property')