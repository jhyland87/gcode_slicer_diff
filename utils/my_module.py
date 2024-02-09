
import sys, importlib
from pathlib import Path # if you haven't already done so

#print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())


def foo(name):
    print("Foo name: " + name)


class Bar(object):
    def __init__(self, name):
        print("Created a new Bar with name "+ name)

#if __name__ == '__main__' and __package__ is None:


"""

def import_parents(level=1):
    global __package__
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[level]
    
    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # already removed
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__) # won't be needed after that


if __name__ == '__main__' and __package__ is None:
    import_parents(level=...)


# ====

if __name__ == '__main__' and __package__ is None:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[3]

    print("__name__: " + __name__)
    print("__package__: " + __package__)

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

    import utils.my_module
    __package__ = 'utils.my_module'

"""

"""

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))


print("__package__: " + __package__)
print("__name__: " + __name__)
# Additionally remove the current file's directory from sys.path
try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass

def say_hello(name):
    print("Hello {name}".format(name=name))


"""