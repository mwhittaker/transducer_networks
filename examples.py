import argparse
import json

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

def main():
    examples = {
        "Ameloot1": Ameloot1().example(),
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("example", choices=examples.keys())
    args = parser.parse_args()

    tn = examples[args.example]
    print(json.dumps(tn.run_json()))

if __name__ == "__main__":
    main()
