import yaml

import pprint
pp = pprint.PrettyPrinter(indent=3)

class quoted(str):
    def __repr__(self):
        return '"' + str(self) + '"'

def quoted_constructor(loader, node):
    value = loader.construct_scalar(node)
    return quoted(value)

with open('example.yml', 'r') as f:
    doc = f.read()

from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.composer import *
from yaml.constructor import *
from yaml.resolver import *
from yaml.error import *
from yaml.nodes import *

class RvtYamlResolver(Resolver):
    '''Changes the default tag for Non-plain/Non-tagged scalars from str to quotedstr'''
    def resolve(self, kind, value, implicit):
        if kind is ScalarNode and implicit[0]:
            if value == '':
                resolvers = self.yaml_implicit_resolvers.get('', [])
            else:
                resolvers = self.yaml_implicit_resolvers.get(value[0], [])
            wildcard_resolvers = self.yaml_implicit_resolvers.get(None, [])
            for tag, regexp in resolvers + wildcard_resolvers:
                if regexp.match(value):
                    return tag
        if self.yaml_path_resolvers:
            exact_paths = self.resolver_exact_paths[-1]
            if kind in exact_paths:
                return exact_paths[kind]
            if None in exact_paths:
                return exact_paths[None]
        if kind is ScalarNode and not implicit[0] and implicit[1]:
            # Non-plain and Non-tagged scalars are quoted strings
            return '!quoted'
        elif kind is ScalarNode:
            return self.DEFAULT_SCALAR_TAG
        elif kind is SequenceNode:
            return self.DEFAULT_SEQUENCE_TAG
        elif kind is MappingNode:
            return self.DEFAULT_MAPPING_TAG

class RvtYamlSafeLoader(Reader, Scanner, Parser, Composer, SafeConstructor, RvtYamlResolver):
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        RvtYamlResolver.__init__(self)


RvtYamlSafeLoader.add_constructor('!quoted', quoted_constructor)


x = yaml.load(doc, Loader=RvtYamlSafeLoader)
pp.pprint(x)