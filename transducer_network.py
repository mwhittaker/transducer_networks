from collections import Counter
import random

from schema import TransducerState, database_satisfies_schema

class TransuducerNetwork(object):
    def __init__(self, network, transducer, in_0):
        self._network = network
        self._transducer = transducer
        self._schema = transducer.schema()
        self._in_0 = in_0

        nodes = set(network.keys())
        s0 = TransuducerNetwork._state_0
        self._states = {node: s0(node, nodes, self._schema, in_0[node])
                        for node in nodes}
        self._bufs = {node: {r: Counter() for r in self._schema.msg}
                      for node in nodes}

    def __str__(self):
        ss = []
        for (node, state) in self._states.items():
            buf = self._bufs[node]

            ss.append("Node '{}'".format(node))
            named_databases = [
                ("in", state.in_),
                ("out", state.out),
                ("mem", state.mem),
                ("buf", buf),
            ]
            for (name, database) in named_databases:
                ss.append("  {}".format(name))
                for (r, d) in database.items():
                    ss.append("    '{}': {}".format(r, d))

        return "\n".join(ss)

    def configuration(self):
        return (self._states, self._bufs)

    def out(self):
        out_0 = {r: set() for r in self._schema.out}
        outs = [s.out for s in self._states.values()]
        return reduce(TransuducerNetwork.union_dicts, outs, out_0)

    def step(self):
        node = random.choice(self._network.keys())
        buf = self._bufs[node]
        msgs = {r: TransuducerNetwork.random_subset(buf[r]) for r in buf}
        self._step(node, msgs)
        return (node, msgs)

    def run(self):
        last_out = None
        out = self.out()
        while last_out != out:
            last_out = out
            self.step()
            out = self.out()

    def _step(self, node, msgs):
        # Sanity check msgs.
        buf = self._bufs[node]
        assert all(0 <= msgs[r] <= buf[r] for r in self._schema.msg)

        # Step transducer and update state.
        state = self._states[node]
        msgs_sets = {r: set(d) for (r, d) in msgs.items()}
        new_state, snd = self._transducer.step(state, msgs_sets)
        self._states[node] = new_state

        # Update message buffers.
        for (r, d) in msgs:
            buf[r].subtract(d)

        for neighbor in self._network[node]:
            for (r, d) in snd:
                self._bufs[neighbor][r].update(Counter(d))

    @staticmethod
    def _state_0(node, nodes, schema, in_0):
        assert database_satisfies_schema(in_0, schema.in_)
        out = {r: set() for r in schema.out}
        msg = {r: set() for r in schema.msg}
        mem = {r: set() for r in schema.mem}
        sys = {"Id": {node}, "All": nodes}
        return TransducerState(in_0, out, msg, mem, sys)

    @staticmethod
    def union_dicts(d1, d2):
        assert d1.keys() == d2.keys()
        return {k: d1[k] | d2[k] for k in d1}

    @staticmethod
    def random_subset(ms):
        xs = ms.elements()
        xs = random.sample(xs, random.randint(0, len(xs) - 1))
        return Counter(xs)
