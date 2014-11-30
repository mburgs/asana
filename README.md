## Asana API

Provides a fluid interface for interacting with the Asana API.
Some code borrowed from https://github.com/pandemicsyn/asana and then heavily modified

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

	from asana import *
	
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
    - ~~update~~
    - ~~create~~
- implement Section
    - ~~subtasks~~
    - naming (append colon)
- Task
    - ~~addProject, removeProject~~
    - functions for positioning? (addAfter, moveAfter?)
- unit testing
- docs
- ~~caching~~
- ~~__init__.py~~
- regex matching for field types:
    - ~~handle array values~~
