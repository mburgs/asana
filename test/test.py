#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, unittest, re

asanadir = os.path.dirname(os.path.realpath(__file__))+"/../"
sys.path.insert(0, asanadir)
asana =  __import__('asana')

from asana import *

from mocks import ApiMock

class BaseTest(unittest.TestCase):
	def setUp(self):
		self.api = ApiMock()
		Entity.set_api(self.api)

	def slugify(self, name):
	    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class GeneralTest(BaseTest):
	"""Tests that affect multiple classes"""
	def test_section_definition(self):
		"""Ensure section definition is correct in
		both Task and Section"""
		tests = {
			True:{'name': 'Foo:'},
			False:{'name': 'Foo'}
		}

		for truth, ent in tests.items():
			for cls in [Task, Section]:
				self.assertEqual(cls._is_section(ent), truth)

	def test_empty_name_section_check(self):
		for cls in [Task, Section]:
			self.assertEqual(bool(cls._is_section({'name':''})), False) 

class EntityTest(BaseTest):
	def test_entity_data_getter(self):
		"""Ensure data saved in is accessible"""
		test_entity = Entity({'foo': 'bar'})

		self.assertEqual(test_entity.foo, 'bar')

	def test_new_id_overwrites(self):
		"""Tests that a new ID from the API will replace a placeholder ID"""
		user = User({'id':'me'})

		user._init({'id':'new'})

		self.assertEqual(user.id, 'new')

	def test_equality(self):
		taskname1 = Task({'name': 'a'})
		taskname2 = Task({'name': 'b'})
		taskid1 = Task({'id': 1})
		taskid2 = Task({'id': 2})

		self.assertTrue(taskname1.__eq__(taskname1))
		self.assertTrue(taskid1.__eq__(taskid1))

		self.assertFalse(taskname1.__eq__(taskname2))
		self.assertFalse(taskid1.__eq__(taskid2))

	def test_from_link(self):
		task = Task.from_link('https://example.com/0/23/1')

		task.load()

		self.assertIn(
			('get', 'tasks/1', {}),
			self.api.requests
		)

		self.assertEqual(Task.from_link(None), None)

class ProjectTest(BaseTest):
	def test_endpoint_correct(self):
		self.assertEqual(Project._get_api_endpoint(), 'projects')

	def test_tasks_as_children(self):
		project = Project({'id':1})

		self.assertEqual(project.tasks, [])

		self.assertIn(
			('get', 'projects/1/tasks', {'params': {'opt_fields': ','.join(Task._fields)}}),
			self.api.requests
		)

	def test_add_task(self):
		"""Tests adding an existing and new task to this project"""

		existing = Task({'id': 1})
		new = Task({'name': 'new'})

		project = Project({'id': 2, 'workspace': {'id': 3}})

		project.add_task(existing)

		self.assertIn(
			('post', 'tasks/1/addProject', {'data': {'project': 2}}),
			self.api.requests
		)

		project.add_task(new)

		self.assertIn(
			('post', 'tasks', {'data': {'projects': [2], 'name': 'new', 'workspace': 3}}),
			self.api.requests
		)

class SectionTest(BaseTest):
	def test_endpoint_correct(self):
		"""Test section endpoint uses tasks"""
		self.assertEqual(Section._get_api_endpoint(), 'tasks')

	def test_custom_build_result(self):
		"""Test that the custom result handling works"""

		taskinsection = {'name': 'a task in section', 'id': 2}
		notinsection = {'name': 'a task not in section', 'id': 3}

		testdata = [
			{'name': 'a test task'},
			{'name': 'Not the section:'},
			notinsection,
			{'name': 'test section:', 'id': 1},
			taskinsection,
			{'name': 'Not the section:'},
			notinsection
		]

		result = Section._build_result({
			'name': lambda n: 'test' in n
		}, testdata)

		self.assertEqual(len(result), 1)

		self.assertEqual(result[0].id, 1)

		self.assertIn(Task(taskinsection), result[0].subtasks)

		self.assertNotIn(Task(notinsection), result[0].subtasks)

class TaskTest(BaseTest):
	def test_addremove_project(self):
		"""Tests adding and removing project
		with a plain id and with an object"""

		task = Task({'id':1})

		projects = {
			2: Project({'id':2}),
			3: 3
		}

		operations = ['addProject', 'removeProject']

		for op in operations:
			for id, obj in projects.items():
				getattr(task, self.slugify(op))(obj)

				self.assertIn(
					('post', 'tasks/1/' + op, {'data': {'project': id}}),
					self.api.requests
				)

	def test_tags_as_children(self):
		task = Task({'id':1})

		self.assertEqual(task.tags, [])

		self.assertIn(
			('get', 'tasks/1/tags', {'params': {'opt_fields': ','.join(Tag._fields)}}),
			self.api.requests
		)

	def test_add_to_section(self):
		task = Task({
			'id':1,
			'projects': [{'id':3}, {'id':4}]
		})

		section = Section({
			'id':2,
			'projects': [{'id':4}, {'id':5}]
		})

		task.add_to_section(section)

		self.assertIn(
			('post', 'tasks/1/addProject', {'data': {'project': 4, 'insert_after': 2}}),
			self.api.requests
		)


if __name__ == "__main__":
	unittest.main()