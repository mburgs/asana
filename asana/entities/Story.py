from Entity import Entity

class Story(Entity):

	@classmethod
	def _get_api_endpoint(cls):
		return 'stories'