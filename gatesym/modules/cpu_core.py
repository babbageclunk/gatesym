from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Or
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_incr
from gatesym.blocks.mux import address_decode, word_switch, word_mux
from gatesym.utils import PlaceholderWord


@block
def cpu_core(clock, data_in, pc_in, write_pc, debug=False):
    network = clock.network
    word_size = len(data_in)

    # step through the 4 states in order
    state = PlaceholderWord(network, 2)
    incr, c = ripple_incr(state)
    state.replace(register(incr, clock))
    s0, s1, s2, s3 = address_decode(state)

    # pc increments in s1 and s3, incoming pc writes are taken in s3
    pc = PlaceholderWord(network, word_size)
    incr, c = ripple_incr(pc)
    jumping = And(write_pc, s3)
    new_pc = word_mux([jumping], incr, pc_in)
    clock_pc = And(clock, Or(s1, s3))
    pc.replace(register(new_pc, clock_pc))

    # clock in address in s0 and s2
    addr = register(data_in, And(clock, Or(s0, s2)))

    # send address as pc in s0 and s2 and addr in s1 and s3
    addr_out = word_switch([Or(s0, s2), Or(s1, s3)], pc, addr)

    # write out data in stage3
    write_out = s3
    data_out = register(data_in, And(clock, s1))

    if debug:
        clock.watch("clock")
        s0.watch("s0")
        s1.watch("s1")
        s2.watch("s2")
        s3.watch("s3")
        jumping.watch("jumping")
        clock_pc.watch("clock pc")
        write_out.watch("write out")

    return addr_out, data_out, write_out
