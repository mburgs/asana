from entity import Entity

class Story(Entity):

	_fields = ['created_at', 'created_by', 'text', 'source', 'type']

	@classmethod
	def _get_api_endpoint(cls):
		return 'stories'