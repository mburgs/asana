from functools import partial

class ApiMock():
	"""Mock an API by saving all calls in a dict"""

	def __init__(self):
		self.requests = []

	def __nonzero__(self):
		return True

	def __getattr__(self, attr):
		return partial(self._savecall, attr)

	def _savecall(self, method, target, **kwargs):
		self.requests.append((method, target, kwargs))

		return {}
