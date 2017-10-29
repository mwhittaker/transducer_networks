from collections import Counter

from schema import TransducerSchema
from transducer import Transducer
from transducer_network import TransuducerNetwork

class Ameloot1(Transducer):
    def schema(self):
        return TransducerSchema({"R": 2}, {"T": 2}, dict(), dict())

    def out(self, r, state):
        assert r == "T"
        return {(x, y) for (x, y) in state.in_["R"] if x == y}

    @staticmethod
    def example():
        A, B, C = "A", "B", "C"
        net = {A: {B, C}, B: {A, C}, C: {A, B}}
        in_0 = {
            A: {"R": {(1, 1), (1, 2), (2, 1), (2, 2)}},
            B: {"R": {(3, 3), (3, 4), (4, 3), (4, 4)}},
            C: {"R": {(5, 5), (5, 6), (6, 5), (6, 6)}},
        }
        return TransuducerNetwork(net, Ameloot1(), in_0)

class MonotoneButNotConsistent(Transducer):
    """
    This transducer shows that not all monotone transducers are consistent.
    This transducer is defined over a schema with an I input relation, an O
    output relation, an A and R message relations, and an M memory relation.
    All relations have arity 1. We can express each query as a non-recursive
    Datalog query:

        # Send input to everyone else.
        A(a) :- I(a)
        R(a) :- I(a)

        # Update memory.
        M_ins(a) :- A(a)
        M_del(a) :- R(a)

        # Output everything in M.
        O(a) :- M(a)

    Clearly, every rule is monotone. However, we can construct two runs with
    different quiescent outputs; see the proof method below.
    """
    def schema(self):
        return TransducerSchema(
            in_={"I": 1},
            out={"O": 1},
            msg={"A": 1, "R": 1},
            mem={"M": 1},
        )

    def snd(self, r, state):
        assert r in ["A", "R"]
        return state.in_["I"]

    def add(self, r, state):
        assert r == "M"
        return state.msg["A"]

    def rem(self, r, state):
        assert r == "M"
        return state.msg["R"]

    def out(self, r, state):
        assert r == "O"
        return state.mem["M"]

    @staticmethod
    def example():
        X, Y = "X", "Y"
        net = {A: {Y}, Y: {A}}
        in_0 = {A: {"I": {(1,)}}, Y: {"I": {(2,)}}}
        return TransuducerNetwork(net, MonotoneButNotConsistent(), in_0)

    @staticmethod
    def proof():
        # It's easy to construct a run in which the output quiesces at {1, 2}.
        tn = MonotoneButNotConsistent.example()
        tn.step("X", {"A": dict(), "R": dict()})
        tn.step("Y", {"A": dict(), "R": dict()})
        tn.step("X", {"A": Counter([(2,)]), "R": dict()})
        tn.step("X", {"A": dict(), "R": dict()})
        tn.step("Y", {"A": Counter([(1,)]), "R": dict()})
        tn.step("Y", {"A": dict(), "R": dict()})
        print tn.out()

        # We can also construct an infinite run in which nothing is output. We
        # just have to make sure to always deliver the A and R facts together.
        tn = MonotoneButNotConsistent.example()
        tn.step("X", {"A": dict(), "R": dict()})
        # Imagine this ran forever!
        for _ in range(100):
            tn.step("Y", {"A": Counter([(1,)]), "R": Counter([(1,)])})
            tn.step("X", {"A": Counter([(2,)]), "R": Counter([(2,)])})
        print tn.out()
