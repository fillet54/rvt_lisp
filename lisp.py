'''Implements a lisp used to execute verification tests'''
import shlex 

############
#   Types
############
class Symbol(str):
    '''A symbol.
    A symbol when evaluated will be looked up in its current environment otherwise 
    the symbol will remain unbounded. Unbounded symbols can also be resolved though
    a plugable system.
    '''
    pass

class String(str):
    '''A string. 
    RVT yaml will allow embedded strings to be interpreted using the shell_reader. 
    This String class will allow for quoted (double or single) strings to not get
    interpreted through the shell_reader.
    '''
    pass

class Procedure(object):
    "A user-defined procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))

List = list

def yaml_reader(stream):
    '''A yaml reader'''
    pass

def shlex_reader(s):
    'read tokens by '
    parts = shlex.split(s, posix=False)
    def convert_scalar(s):
        if len(s) > 0 and s.startswith('"') and s.endswith('"'):
            return String(s[1:-1])
        elif len(s) > 0 and s.startswith("'") and s.endswith("'"):
            return String(s[1:-1])
        else:
            try:
                return int(s)
            except:
                try:
                    return float(s)
                except:
                    return Symbol(s)
    return [convert_scalar(part) for part in parts] 

class Env(dict):
    '''An environment: a dict of {'var': val} pairs, with an outer Env.'''
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

def standard_env():
    env = Env()
    return


def eval(x, env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):    # variable reference
        # return symbol if not found in env
        return env.find(x).get(x, x)
    elif not isinstance(x, list):# constant 
        return x   
    op, args = x[0], x[1:]       
    if op == 'quote':            # quotation
        return args[0]
    elif op == 'if':             # conditional
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'define':         # definition
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':           # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'fn':             # procedure
        (parms, body) = args
        return Procedure(parms, body, env)
    else:                        # procedure call
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)