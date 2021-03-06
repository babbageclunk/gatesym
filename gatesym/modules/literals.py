from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Tie, block


@block
def low_literal(clock, write, address, data_in, size):
    data_out = []
    data_out.extend(address[:size])
    for i in range(len(data_in) - size):
        data_out.append(Tie(clock.network, False))
    return data_out


@block
def high_literal(clock, write, address, data_in, size):
    data_out = []
    for i in range(len(data_in) - size):
        data_out.append(Tie(clock.network, False))
    data_out.extend(address[:size])
    return data_out
