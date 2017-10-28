from collections import namedtuple

# DatabaseSchema: map relation name to arity
TransducerSchema = namedtuple("TransducerSchema", ["in_", "out", "msg", "mem"])
TransducerState = namedtuple("TransducerState", ["in_", "out", "msg", "mem", "sys"])

def database_satisfies_schema(d, schema):
    """
    >>> d = {"R": {(1, 2), (3, 4)}, "S": {(1,), (2,)}}
    >>> schema = {"R": 2, "S": 1}
    >>> database_satisfies_schema(d, schema)
    True
    >>> schema = {"R": 1, "S": 2}
    >>> database_satisfies_schema(d, schema)
    False
    """
    same_relations = d.keys() == schema.keys()
    if not same_relations:
        return False
    return all(len(t) == schema[r] for r in d for t in d[r])

def state_satisfies_schema(state, schema):
    return (database_satisfies_schema(state.in_, schema.in_) and
            database_satisfies_schema(state.out, schema.out) and
            database_satisfies_schema(state.msg, schema.msg) and
            database_satisfies_schema(state.mem, schema.mem))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

