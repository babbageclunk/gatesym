from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, gates, utils
from gatesym.modules import memory


def test_memory():
    network = core.Network()
    clock = gates.Tie(network)
    write_flag = gates.Tie(network)
    address = utils.BinaryIn(network, 4)
    data_in = utils.BinaryIn(network, 8)
    mem = memory.memory(clock, write_flag, address, data_in)
    data_out = utils.BinaryOut(mem)
    network.drain()

    def write(value, addr):
        data_in.write(value)
        address.write(addr)
        write_flag.write(1)
        clock.write(1)
        network.drain()
        clock.write(0)
        network.drain()
        write_flag.write(0)

    def read(addr):
        address.write(addr)
        write_flag.write(0)
        network.drain()
        return data_out.read()

    data = [0] * 16
    for i in range(100):
        v = random.randrange(256)
        a = random.randrange(16)
        write(v, a)
        data[a] = v

        a = random.randrange(16)
        assert read(a) == data[a]
