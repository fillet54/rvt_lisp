import lisp
import shlex

class Test(object):
    def __init__(self, **kwargs):
        self.steps = kwargs.get('steps', [])
        self.description = []

class Step(object):
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.preconditions = kwargs.get('preconditions', [])
        self.blocks = kwargs.get('blocks', [])

class BuildingBlock(object):
    '''Base class to find it'''

    def getName(self):
        return self.__class__.__name__

    def checkSyntax(self, *args):
        return False

    def execute(self, *args):
        return True

class BlockExecutor(object):
    'Finds specific block and executes it'
    def __init__(self, name):
        self.name = name
    def __call__(self, *args):
        for block in BuildingBlock.__subclasses__():
            b = block()
            if b.getName() == self.name and b.checkSyntax(*args):
                return b.execute(*args)
        raise Exception('%s not found' % self.name)


def shlex_reader(s):
    'read using the backwards compatible way'
    parts = shlex.split(s)
    return [lisp.Symbol(parts[0])] + parts[1:]

def execute_test(test):
    # Construct global env
    # Add block executors to the global env 
    block_names = set([b().getName() for b in BuildingBlock.__subclasses__()])
    block_execs = [BlockExecutor(name) for name in block_names]
    global_env = lisp.Env(parms=block_names, args=block_execs, outer=lisp.standard_env())

    for step in test.steps:
        for block in step.blocks:
            if isinstance(block, str):
                block = shlex_reader(block)
            result = lisp.eval(block, env=global_env) 
            if not result:
                return False
    return True