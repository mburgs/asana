from entities import *
from asana import *

import inspect

clsmembers = inspect.getmembers(entities, inspect.isclass)

matches = {}

for cls in clsmembers:
	if issubclass(cls[1], Entity) and hasattr(cls[1], '_matchon'):
		matches[cls[1]._matchon] = cls[1]

Entity._matchons = matches