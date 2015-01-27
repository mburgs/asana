from entity import Entity

class User(Entity):
	_matchon = 'assignee$|followers|_by'

	_fields = ['name', 'email', 'workspaces']

	@classmethod
	def from_link(cls, link):
		raise Exception('This method does not work for the User type')