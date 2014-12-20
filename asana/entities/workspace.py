from entity import Entity

class Workspace(Entity):

	_matchon = 'workspace'

	_fields = ['name', 'is_organization']