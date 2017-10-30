from collections import Counter
import random
import json

from schema import TransducerState, database_satisfies_schema

class Dict:
    @staticmethod
    def map(d, f):
        return {k: f(v) for (k, v) in d.iteritems()}

    @staticmethod
    def map2(d1, d2, f):
        assert d1.keys() == d2.keys()
        return {k: f(d1[k], d2[k]) for k in d1}

def _union_database(ds, schema):
    f = lambda d1, d2: Dict.map2(d1, d2, lambda s1, s2: s1 | s2)
    d0 = {r: set() for r in schema}
    return reduce(f, ds, d0)

def _random_subset(ms):
    xs = list(ms.elements())
    xs = random.sample(xs, random.randint(0, len(xs)))
    return Counter(xs)

class TransuducerNetwork(object):
    def __init__(self, network, transducer, in_0):
        self._network = network
        self._transducer = transducer
        self._schema = transducer.schema()
        self._in_0 = in_0

        # Initialize the state and message buffers for each node.
        nodes = set(network.keys())
        self._states = dict()
        self._bufs = dict()
        for node in nodes:
            self._states[node] = TransducerState(
                in_0[node],
                {r: set() for r in self._schema.out},
                {r: set() for r in self._schema.msg},
                {r: set() for r in self._schema.mem},
                {"Id": {node}, "All": nodes},
            )
            self._bufs[node] = {r: Counter() for r in self._schema.msg}

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        data = {}
        for (node, state) in self._states.items():
            data[node] = {
                "in": Dict.map(state.in_, list),
                "out": Dict.map(state.out, list),
                "mem": Dict.map(state.mem, list),
                "buf": Dict.map(self._bufs[node], lambda c: list(c.elements()))
            }
        return data

    def configuration(self):
        return (self._states, self._bufs)

    def out(self):
        schema = self._schema.out
        outs = [s.out for s in self._states.values()]
        return _union_database(outs, schema)

    def step(self, node, msgs):
        # Sanity check msgs.
        buf = self._bufs[node]
        assert all(0 <= msgs[r] <= buf[r] for r in self._schema.msg)

        # Step transducer and update state.
        state = self._states[node]
        msgs_sets = {r: set(d) for (r, d) in msgs.items()}
        new_state, snd = self._transducer.step(state, msgs_sets)
        self._states[node] = new_state

        # Update message buffers.
        for (r, d) in msgs.items():
            buf[r].subtract(d)

        for neighbor in self._network[node]:
            for (r, d) in snd.items():
                self._bufs[neighbor][r].update(Counter(d))

    def random_step(self):
        node = random.choice(self._network.keys())
        buf = self._bufs[node]
        msgs = {r: _random_subset(buf[r]) for r in buf}
        self.step(node, msgs)
        return (node, msgs)

    def sync_mem_relation(self, r):
        schema = self._schema.mem
        mems = [s.mem for s in self._states.values()]
        unioned = _union_database(mems, schema)
        for state in self._states.values():
            state.mem[r] = unioned[r]

