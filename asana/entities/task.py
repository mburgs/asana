from entity import Entity

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
		if entity['name'][-1] == ':':
			#this is a section
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
