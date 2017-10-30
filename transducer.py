from schema import database_satisfies_schema, state_satisfies_schema

class Transducer(object):
    """
    A relational transducer. See "Relational Transducers for Declarative
    Networking" for a description of what a relation transducer is. Here's an
    example of how to define the Example 4.3 transducer from the Ameloot paper:

        class Ameloot1(Transducer):
            def schema(self):
                return TransducerSchema({"R": 2}, {"T": 2}, dict(), dict())

            def out(self, r, state):
                assert r == "T"
                return {(x, y) for (x, y) in state.in_["R"] if x == y}
    """
    def schema(self):
        raise NotImplementedError()

    def out(self, r, state):
        raise NotImplementedError()

    def snd(self, r, state):
        raise NotImplementedError()

    def add(self, r, state):
        raise NotImplementedError()

    def rem(self, r, state):
        raise NotImplementedError()

    def step(self, state, msgs):
        """
        Computes I, I_rcv -> J, J_snd from the Ameloot paper where I = state,
        I_rcv = msgs, and (J, J_snd) is returned.
        """
        schema = self.schema()
        state_p = state._replace(msg=msgs)

        out = {r: state.out[r] | self.out(r, state_p) for r in schema.out}
        add = {r: self.add(r, state_p) - self.rem(r, state_p) for r in schema.mem}
        rem = {r: self.rem(r, state_p) - self.add(r, state_p) for r in schema.mem}
        mem = {r: (state.mem[r] | add[r]) - rem[r] for r in schema.mem}
        snd = {r: self.snd(r, state_p) for r in schema.msg}
        new_state = state._replace(out=out, mem=mem)

        assert state_satisfies_schema(new_state, schema), (new_state, schema)
        assert database_satisfies_schema(snd, schema.msg)
        return (new_state, snd)
