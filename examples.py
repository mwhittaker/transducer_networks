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
    output relation, A and R message relations, and an M memory relation.
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
        net = {X: {Y}, Y: {X}}
        in_0 = {X: {"I": {(1,)}}, Y: {"I": {(2,)}}}
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

class SuperMonotoneButNotConsistent(Transducer):
    """
    This transducer shows that not all monotone transducers are consistent.
    This transducer is defined over a schema with an I input relation of arity
    1 and an O output relation of arity 2. The transducer performs no network
    communication and consists of a single rule:

        O(a, b) :- I(a), I(b), a != b

    This program is super montone in the sense that:

        (1) it never deletes from its channels,
        (2) it never deletes from its memory, and
        (3) all of its rules are monotone.

    Howoever, the transducer is still not consistent. See proof method below
    for details.
    """
    def schema(self):
        return TransducerSchema(
            in_={"I": 1},
            out={"O": 2},
            msg=dict(),
            mem=dict(),
        )

    def out(self, r, state):
        assert r == "O"
        I = state.in_["I"]
        return {(a, b) for (a,) in I for (b,) in I if a != b}

    @staticmethod
    def example(in_0):
        X, Y = "X", "Y"
        net = {X: {Y}, Y: {X}}
        return TransuducerNetwork(net, SuperMonotoneButNotConsistent(), in_0)

    @staticmethod
    def proof():
        # We can construct a run in which the output quiesces at {(1, 2), (2, 1)}.
        in_0 = {"X": {"I": {(1,), (2,)}}, "Y": {"I": set()}}
        tn = SuperMonotoneButNotConsistent.example(in_0)
        tn.step("X", dict())
        for _ in range(100):
            tn.random_step()
        print tn.out()

        # We can also construct a run in which the output quiesces at {}.
        in_0 = {"X": {"I": {(1,)}}, "Y": {"I": {(2,)}}}
        tn = SuperMonotoneButNotConsistent.example(in_0)
        tn.step("X", dict())
        tn.step("Y", dict())
        for _ in range(100):
            tn.random_step()
        print tn.out()

class SynchronizedNegationsButNotConsistent(Transducer):
    """
    This transducer shows that synchronizing negated relations is not
    sufficient to make a transducer consistent. This transducer is defined over
    a schema with an I input relation, an O output relation, A and R message
    relations, and A and R memory relation.  All relations have arity 1. We can
    express each query as a non-recursive Datalog query:

        # Replicate input.
        A(a) :- I(a)
        R(a) :- I(a)

        # Cache input.
        A_ins(a) :- A(a)
        R_ins(a) :- R(a)

        # Write to out.
        O(a) :- A(a), !R(a)

    The only negated relation is R, but synchronizing R before every timestep
    is not enough to guarantee that the transducer network is consistent. See
    the proof method below for details.
    """
    def schema(self):
        return TransducerSchema(
            in_={"I": 1},
            out={"O": 1},
            msg={"A": 1, "R": 1},
            mem={"A": 1, "R": 1},
        )

    def snd(self, r, state):
        assert r in ["A", "R"]
        return state.in_["I"]

    def add(self, r, state):
        return state.msg[r]

    def rem(self, r, state):
        return set()

    def out(self, r, state):
        assert r == "O"
        return state.mem["A"] - state.mem["R"]

    @staticmethod
    def example():
        X, Y = "X", "Y"
        net = {X: {Y}, Y: {X}}
        in_0 = {X: {"I": {(1,)}}, Y: {"I": {(2,)}}}
        t = SynchronizedNegationsButNotConsistent()
        return TransuducerNetwork(net, t, in_0)

    @staticmethod
    def proof():
        # It's easy to construct a run in which the output quiesces at {1, 2}.
        tn = SynchronizedNegationsButNotConsistent.example()
        tn.step("X", {"A": dict(), "R": dict()})
        tn.sync_mem_relation("R")
        tn.step("Y", {"A": Counter([(1,)]), "R": dict()})
        tn.sync_mem_relation("R")
        tn.step("Y", {"A": dict(), "R": dict()})
        tn.sync_mem_relation("R")
        tn.step("X", {"A": Counter([(2,)]), "R": dict()})
        tn.sync_mem_relation("R")
        tn.step("X", {"A": dict(), "R": dict()})
        tn.sync_mem_relation("R")
        for _ in range(100):
            tn.random_step()
        print tn.out()

        # We can also construct a run which quiesces at the empty set.
        tn = SynchronizedNegationsButNotConsistent.example()
        tn.step("X", {"A": dict(), "R": dict()})
        tn.sync_mem_relation("R")
        tn.step("Y", {"A": dict(), "R": Counter([(1,)])})
        tn.sync_mem_relation("R")
        tn.step("Y", {"A": dict(), "R": dict()})
        tn.sync_mem_relation("R")
        tn.step("X", {"A": dict(), "R": Counter([(2,)])})
        tn.sync_mem_relation("R")
        tn.step("X", {"A": dict(), "R": dict()})
        tn.sync_mem_relation("R")
        for _ in range(100):
            tn.random_step()
        print tn.out()



def main():
    MonotoneButNotConsistent.proof()
    SuperMonotoneButNotConsistent.proof()
    SynchronizedNegationsButNotConsistent.proof()

if __name__ == "__main__":
    main()
