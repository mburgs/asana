## Asana API

Provides a fluid interface for interacting with the Asana API.
Some code borrowed from https://github.com/pandemicsyn/asana and then heavily modified

### Features
 - Easily retrieve items and filter by any field - automatically handle which
 fields are request filters and which ar filtered out manually. Filters can be strings which are matched or lambdas
 - Lazy loading ORM. Sub-objects are automatically wrapped with their corresponding objects and accessing any unloaded fields on them will cause a that object to load it's fields. Example:

        task = Task.find({'name': 'My task'})
        print task.assignee.name

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
		'name': lambda n: 'Test' in n
	})[0]
	
	tasks = myproject.get_subitem(Task, {'completed_since': 'now'})

See `examples/` for more

### Testing

There are tests under the `test` folder using `unittest`. Just run with `test.py`

For coverage reports run `coverage run --source=asana --omit=asana/asana.py ./test/test.py && coverage report`

For coverage reports (from base of repo):
`coverage run --source=asana --omit=asana/asana.py ./test/test.py`

### Todo
- implement Section
    - ~~subtasks~~
    - naming (append colon on save)
- Task
    - use expand= options for project.section (see http://stackoverflow.com/questions/26937179/how-to-retrieve-tasks-by-section-using-asana-api)
- docs
- examples
- relationships
    - child/parent, instead of get_subitem implement magic methods
    - for adding project, tag, follower to task implement magic methods
- subtasks?
- issue with passing in items for filters. If they're request filters needs to be id but if not needs to be id (ie for project) - need to filter on value
