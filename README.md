## Asana API

Provides a fluid interface for interacting with the Asana API.
Some code borrowed from https://github.com/pandemicsyn/asana

### Features
 - Easily retrieve items and filter by any field - automatically handle which
 fields are request filters and which ar filtered out manually
 - `get_subitem` - unified interface for retrieving items in Parent-Child
 relations
 - Section support - special properties for getting sections and their subtasks

### Requirements
  - `requests` module - http://docs.python-requests.org/en/latest/user/install/

### Usage

Example of basic usage (getting all incomplete tasks in certain project):

	import asana
	from entities import *
	
	api_key = '<api_key>'
	Entities.set_api(AsanaAPI(api_key))
	
	myproject = Project.find({
		'name': 'My project'
	})[0]
	
	tasks = myproject.get_subitem(Task, {'completed_since': 'now'})

### Todo
- finish README
- finish todo
- implement save()
- implement Section
    - ~~subtasks~~
    - naming (append colon)
- unit testing
- docs
- ~~caching~~
- Task:
	- ~~get_created_by~~
	- get_assignee (?)
- setup.py, modularize
- leverage Input/Output options to pull more fields? (http://developer.asana.com/documentation/#Options)
