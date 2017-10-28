from schema import TransducerSchema
from transducer import Transducer
from transducer_network import TransuducerNetwork

class Ameloot1(Transducer):
    def schema(self):
        return TransducerSchema({"R": 2}, {"T": 2}, dict(), dict())

    def out(self, r, state):
        assert r == "T"
        return {(x, y) for (x, y) in state.in_["R"] if x == y}

def main():
    A, B, C = "ABC"
    net = {A: {B, C}, B: {A, C}, C: {A, B}}
    in_0 = {
        A: {"R": {(1, 1), (1, 2), (2, 1), (2, 2)}},
        B: {"R": {(3, 3), (3, 4), (4, 3), (4, 4)}},
        C: {"R": {(5, 5), (5, 6), (6, 5), (6, 6)}},
    }
    tn = TransuducerNetwork(net, Ameloot1(), in_0)

    print tn.out()
    tn.step(1)
    print tn.out()
    tn.step(1)
    print tn.out()
    tn.step(1)
    print tn.out()

if __name__ == "__main__":
    main()
