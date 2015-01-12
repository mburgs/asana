import os
import glob, importlib

#expose classes as part of the base module
modules = glob.glob(os.path.dirname(__file__)+"/*.py")

for name in [ os.path.basename(f)[:-3] for f in modules if '__init__' not in f]:
	module = __import__(name, globals(), locals())

	locals()[name.title()] = getattr(module, name.title())
