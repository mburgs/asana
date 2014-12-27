import sys, unittest

sys.path.insert(0, "../")
asana =  __import__('asana')

from asana import *

class GeneralTest(unittest.TestCase):
	"""Tests that affect multiple classes"""
	def test_section_definition(self):
		section = {'name': 'Foo:'}
		task = {'name': 'Foo'}

		self.assertFalse(Task._is_section(task))
		self.assertFalse(Section._is_section(task))

		self.assertTrue(Task._is_section(section))
		self.assertTrue(Section._is_section(section))

class EntityTest(unittest.TestCase):

	def setUp(self):
		pass

	def test_entity_data_getter(self):
		"""Ensure data saved in is accessible"""
		test_entity = Entity({'foo': 'bar'})

		self.assertEqual(test_entity.foo, 'bar')

class ProjectTest(unittest.TestCase):
	def test_endpoint_correct(self):
		self.assertEqual(Project._get_api_endpoint(), 'projects')

if __name__ == "__main__":
	unittest.main()