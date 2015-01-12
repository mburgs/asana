from entities import *
from asana import *

import inspect

__version__ = ".".join(map(str, (0, 1, 1)))

clsmembers = inspect.getmembers(entities, inspect.isclass)

#build map for matchon
matches = {}

for cls in clsmembers:
	if issubclass(cls[1], Entity):
		#load matchon clauses
		if hasattr(cls[1], '_matchon') and getattr(cls[1], '_matchon'):
			matches[cls[1]._matchon] = cls[1]

		#put children into wrapper classes
		for key, subClass in cls[1]._children.items():

			if isinstance(subClass, Child):
				continue

			if not subClass:
				subClass = locals()[key[:-1].title()]

			cls[1]._children[key] = Child(subClass)


Entity._matchons = matches