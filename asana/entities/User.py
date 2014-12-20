from Entity import Entity

class User(Entity):
	_matchon = 'assignee$|followers|_by'

	_fields = [
		'name', 'email'
	]