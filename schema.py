from collections import namedtuple

# A transducer schema defines a database schema for each of the in_, out, msg,
# and mem databases. Every database schema is a dictionary mapping a relation's
# name to its arity. For example, the database schema {"R": 1, "S": 2}
# represents a database with an arity 1 relation R and an arity 2 relation S.
#
#   in_ = {"I": 2}
#   out = {"O": 2}
#   msg = {"A": 2, "B": 1}
#   mem = {"X": 2}
#   schema = TransducerSchema(in_=in_, out=out, msg=msg, mem=mem)
TransducerSchema = namedtuple("TransducerSchema", ["in_", "out", "msg", "mem"])

# A transducer state defines a database instance for each of the in_, out, msg,
# mem, and sys databases. Every database instance is a dictionary mapping a
# relation's name to a set of tuples. For example, here's a transducer sate
# that satisfies the schema above:

#   in_ = {"I": set()}
#   out = {"O": {(1, 2), (3, 4)}}
#   msg = {"A": set(), "B": {(1,), (2,)}}
#   mem = {"X": set()}
#   state = TransducerState(in_=in_, out=out, msg=msg, mem=mem)
TransducerState = namedtuple("TransducerState", ["in_", "out", "msg", "mem", "sys"])

def database_satisfies_schema(d, schema):
    """
    Returns whether a database instance d satisfies a database schema schema. A
    database instance satisfies a schema if the arity of every tuple in a
    relation matches the arity of the relation as prescribed by the schema.

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
    """Returns whether a transducer state satisfies a transducer schema."""
    sys = {"Id": 1, "All": 1}
    return (database_satisfies_schema(state.in_, schema.in_) and
            database_satisfies_schema(state.out, schema.out) and
            database_satisfies_schema(state.msg, schema.msg) and
            database_satisfies_schema(state.mem, schema.mem) and
            database_satisfies_schema(state.sys, sys))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
