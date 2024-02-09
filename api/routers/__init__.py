#from pathlib import Path
#print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

#from os.path import dirname, basename, isfile, join

#import glob

#modules = glob.glob(join(dirname(__file__), "*.py"))

#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

from .gcode import router as gcode
from .utils import router as utils

