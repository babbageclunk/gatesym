from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Tie
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_adder
from gatesym.blocks.mux import word_switch, address_decode


@block
def add(clock, write, address, data_in):
    assert len(address) == 2

    control_lines = address_decode(address)

    write_a = And(clock, write, control_lines[0])
    a = register(data_in, write_a)

    write_b = And(clock, write, control_lines[1])
    b = register(data_in, write_b)

    res, carry = ripple_adder(a, b)
    carry = [carry] + [Tie(address[0].network) for i in range(len(data_in)-1)]

    return word_switch(control_lines, a, b, res, carry)
