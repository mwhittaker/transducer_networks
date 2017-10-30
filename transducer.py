from schema import database_satisfies_schema, state_satisfies_schema

class Transducer(object):
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
