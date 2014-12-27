from entities import *
from asana import *

import inspect

__version__ = ".".join(map(str, (0, 1, 1)))

clsmembers = inspect.getmembers(entities, inspect.isclass)

#build map for matchon
matches = {}

for cls in clsmembers:
	if issubclass(cls[1], Entity) and hasattr(cls[1], '_matchon') and getattr(cls[1], '_matchon'):
		matches[cls[1]._matchon] = cls[1]

Entity._matchons = matches