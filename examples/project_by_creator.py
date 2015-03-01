#! /usr/bin/python

from asana import Entity, AsanaAPI, Project, Section

import re, argparse

#argument parsing
parser = argparse.ArgumentParser(
	description='Create a view of all tasks by createor',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('name', help='Name of the project that will contain the view')
parser.add_argument('--project-regex', '-p', help='Regex of which projects to generate report for')
parser.add_argument('--api-key', '-a', help='API key to use')

options = parser.parse_args()

Entity.set_api(AsanaAPI(options.api_key, debug=True, cache=True))

print 'Loading projects and tasks...'

projects = Project.find({
	'name': lambda n: re.search(options.project_regex, n)
})

tasks = []

for project in projects:
	tasks.extend(project.tasks)

print 'Creating view project...'

view_project = Project({
	'name': 'Creator View',
	'workspace': projects[0].workspace.id,
	'team': projects[0].team.id
})

view_project.save()


#initialize each creator to an empty array
tasks_by_creator = {t.created_by: [] for t in tasks}

print 'Adding tasks to meeting...'

for task in tasks:
	tasks_by_creator[task.created_by].append(task)

for creator in tasks_by_creator.keys():

	for task in tasks_by_creator[creator]:
		view_project.add_task(task)

	# need to add section after tasks to correct order
	section = Section({'name':creator.name + ':'})

	view_project.add_task(section)

print 'Done!'