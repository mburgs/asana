import os
import glob

#expose classes as part of the base module
modules = glob.glob(os.path.dirname(__file__)+"/*.py")

for name in [ os.path.basename(f)[:-3] for f in modules if f is not '__init__.py']:
	locals()[name] = getattr(__import__(name, globals(), locals()), name)
