from collections import namedtuple


TIE, AND, OR = range(3)


class Gate(object):
    # handles to gate objects
    def __init__(self, network, index, inputs):
        self.network = network
        self.index = index
        for input_ in inputs:
            network.add_link(input_, self)

    def __repr__(self):
        return "{self.index}".format(self=self)

    def read(self):
        return self.network.read(self)


class _Gate(namedtuple("Gate", "type_, inputs, neg_inputs, outputs")):
    # internal gate format
    def __new__(cls, type_):
        return super(_Gate, cls).__new__(cls, type_, set(), set(), set())


class GateNetwork(object):
    def __init__(self):
        self._gates = [None]
        self._values = [None]
        self._queue = set()

    def add_gate(self, type_):
        assert type_ in [TIE, AND, OR]
        index = len(self._gates)
        self._gates.append(_Gate(type_))
        self._values.append(False)
        return index

    def add_link(self, source, destination):
        assert source.network is self
        assert destination.network is self
        assert destination.index > 0
        dest_gate = self._gates[destination.index]
        assert dest_gate.type_ != TIE
        self._gates[abs(source.index)].outputs.add(destination.index)
        if source.index < 0:
            dest_gate.neg_inputs.add(abs(source.index))
        else:
            dest_gate.inputs.add(source.index)
        self._queue.add(destination.index)

    def read(self, gate):
        assert gate.network is self
        if gate.index < 0:
            return not self._values[-gate.index]
        else:
            return self._values[gate.index]

    def write(self, gate, value):
        assert gate.network is self
        assert gate.index > 0
        r_gate = self._gates[gate.index]
        assert r_gate.type_ == TIE
        self._values[gate.index] = value
        self._queue.update(r_gate.outputs)

    def step(self):
        queue = self._queue
        self._queue = set()

        for index in queue:
            gate = self._gates[index]

            if gate.type_ == AND:
                a = [self._values[i] for i in gate.inputs]
                b = [not self._values[i] for i in gate.neg_inputs]
                res = all(a + b)
            elif gate.type_ == OR:
                a = [self._values[i] for i in gate.inputs]
                b = [not self._values[i] for i in gate.neg_inputs]
                res = any(a + b)
            else:
                assert False, gate.type_

            if self._values[index] != res:
                self._values[index] = res
                self._queue.update(gate.outputs)

        return bool(self._queue)

    def drain(self):
        print ".",
        while self.step():
            print ".",
            pass
        print


class Tie(Gate):
    def __init__(self, network, value=False):
        index = network.add_gate(TIE)
        super(Tie, self).__init__(network, index, [])
        self.write(value)

    def write(self, value):
        self.network.write(self, value)


def Not(gate):
    return Gate(gate.network, -gate.index, [])


class And(Gate):
    def __init__(self, *inputs):
        network = inputs[0].network
        index = network.add_gate(AND)
        super(And, self).__init__(network, index, inputs)


class Or(Gate):
    def __init__(self, *inputs):
        network = inputs[0].network
        index = network.add_gate(OR)
        super(Or, self).__init__(network, index, inputs)



def half_adder(a, b):
    carry = And(a, b)
    result = Or(And(a, Not(b)), And(Not(a), b))
    return result, carry


def full_adder(a, b, c):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, c)
    return s2, Or(c1, c2)


def test_half_adder():
    network = GateNetwork()
    a = Tie(network)
    b = Tie(network)
    r, c = half_adder(a, b)
    network.drain()

    a.write(False)
    b.write(False)
    network.drain()
    assert not r.read()
    assert not c.read()

    a.write(True)
    b.write(False)
    network.drain()
    assert r.read()
    assert not c.read()

    a.write(False)
    b.write(True)
    network.drain()
    assert r.read()
    assert not c.read()

    a.write(True)
    b.write(True)
    network.drain()
    assert not r.read()
    assert c.read()


def test_full_adder():
    network = GateNetwork()
    a = Tie(network)
    b = Tie(network)
    c = Tie(network)
    r, co = full_adder(a, b, c)
    network.drain()

    a.write(False)
    b.write(False)
    c.write(False)
    network.drain()
    assert not r.read()
    assert not co.read()

    a.write(True)
    b.write(False)
    c.write(False)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(False)
    b.write(True)
    c.write(False)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(True)
    b.write(True)
    c.write(False)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(False)
    b.write(False)
    c.write(True)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(True)
    b.write(False)
    c.write(True)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(False)
    b.write(True)
    c.write(True)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(True)
    b.write(True)
    c.write(True)
    network.drain()
    assert r.read()
    assert co.read()


if __name__ == "__main__":
    test_half_adder()
    test_full_adder()