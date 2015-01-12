from entity import Entity

class Project(Entity):
	_matchon = 'project'

	_fields = ['name', 'notes', 'workspace', 'team']

	_children = {
		'tasks': None
	}

	def add_task(self, task):
		"""Adds a new task to this project, if the task is already created
		then proxies to Task.add_project

		:param task: task to add to project
		"""

		if task.id:
			task.add_project(self)
		else:
			task.projects = [self.id]
			task.workspace = self.workspace.id

			task.save()
