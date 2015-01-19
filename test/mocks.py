class ApiMock():
	"""Mock an API by saving all calls in a dict"""

	def __init__(self):
		self.requests = []

	def get(self, target, **kwargs):
		self._savecall('get', target, **kwargs)

		return {}

	def post(self, target, **kwargs):
		self._savecall('post', target, **kwargs)

		return {}

	def put(self, target, **kwargs):
		self._savecall('put', target, **kwargs)

	def delete(self, target, **kwargs):
		self._savecall('delete', target, **kwargs)

	def _savecall(self, method, target, **kwargs):
		self.requests.append((method, target, kwargs))
