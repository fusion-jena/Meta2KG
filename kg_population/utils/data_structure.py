class MyLiteral:
    def __init__(self, name, datatype, value=None):
        self.name = name
        self.datatype = datatype
        self.value = value


class MyNode:
    def __init__(self, name, members=None, is_a=None, literals=None, exactMatch=None, closeMatch=None):
        self.name = name
        self.members = members  # list of nodes
        self.is_a = is_a # should be something supported by rdflib e.g., schema.person,
        self.literals = literals  # a literal is a key-value pair (literal name, value)
        self.exactMatch = exactMatch
        self.closeMatch = closeMatch
