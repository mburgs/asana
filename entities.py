class EntityException(Exception):
    """Wrap entity specific errors"""
    pass

class Entity(object):
	"""Base implementation for an Asana entity containing
	common funcitonality"""

	_filter_keys = []

	def __init__(self, apiOrData):
		self._data = apiOrData

		self._dirty = set()

		self._ready = True

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

	@classmethod
	def find(cls, query={}):
		params = {} #params that are part of the request

		if cls._filter_keys:
			for key in query.keys():
				if key in cls._filter_keys:
					params[key] = query[key]
					del query[key]

		data = cls._get_api().get(cls._get_api_endpoint(), params=params)

		return cls._build_result(query, data)

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

	def save(self):
		"""Handles both creating and updating content
		The assumption is if there is no ID set this is
		a creation request"""

		pass

	def delete(self):
		"""Deletes the specified resource. The ID must be set"""

		if not self.id:
			raise EntityException('Cannot delete without an ID set')

		self.get_api().delete('/'.join([self._get_api_endpoint(), self.id]))

	def __getattr__(self, attr):

		if attr in self.__dict__:
			return self.__dict__[attr]

		if attr in self.__dict__['_data']:
			return self.__dict__['_data'][attr]

	def __setattr__(self, attr, value):
		if attr in ['_data', '_dirty', '_ready']:
			self.__dict__[attr] = value
		elif self._ready:
			self._data[attr] = value
			self._dirty.add(attr)

	def __str__(self):
		return vars(self).__repr__()

	def __repr__(self):
		return self.__str__()

class Project(Entity):
	pass

class Task(Entity):
	_filter_keys = ['project', 'assignee']
	pass

class Section(Entity):
	_filter_keys = Task._filter_keys

	@classmethod
	def _get_api_endpoint(cls):
		return Task._get_api_endpoint()