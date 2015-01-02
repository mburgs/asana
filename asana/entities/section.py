from entity import Entity
import task

class Section(task.Task):
	_matchon = None

	def _filter_result_item(cls, entity, query):
		Entity._filter_result_item(entity, query)

	@classmethod
	def _get_api_endpoint(cls):
		"""Point to tasks"""
		return 'tasks'

	@classmethod
	def _build_result(cls, query, data):
		"""We need custom result building for sections to figure out which in
		the reuslt set are sections and which are tasks - the results are
		returned in order so every task after a section until the next section
		is considered a subtask
		"""
		current = None
		filling = False
		ret = []

		for ent in data:
			if cls._is_section(ent):
				if current:
					ret.append(cls(current))
					current = None

				if cls._filter_result_item(ent, query):
					current = ent
					current['subtasks'] = []
			elif current:
				current['subtasks'].append(ent)

		if current:
			ret.append(cls(current))

		return ret

	@staticmethod
	def _is_section(ent):
		"""Checks whether a dict from the API is a section Task

		:param ent: The dict to check
		"""
		return ent['name'] and ent['name'][-1] == ':'

	def get_subitem(self, subclass, query):
		raise EntityException('This function does not apply to sections, try the subtasks property')