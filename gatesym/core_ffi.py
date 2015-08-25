from cffi import FFI
import os

SO_PATH = os.path.expanduser('~/Dropbox/code/rust/gatesymcore/target/release/libgatesymcore.so')

ffi = FFI()

ffi.cdef("""
    void   *network_new();
    void    network_free(void *ptr);
    size_t  network_add_gate(void *ptr, uint8_t kind, uint32_t cookie);
    void    network_add_link(void *ptr, size_t source_index, size_t dest_index, uint8_t negate);
    uint8_t network_read(void *ptr, size_t gate_index);
    void    network_write(void *ptr, size_t gate_index, uint8_t value);
    size_t  network_drain(void *ptr);
""")

lib = ffi.dlopen(SO_PATH)

TIE, SWITCH, AND, OR = range(4)

class Network(object):

    def __init__(self):
        self._ptr = lib.network_new()
        self._cookies = []

    def __del__(self):
        lib.network_free(self._ptr)

    def add_gate(self, type_, cookie):
        self._cookies.append(cookie)
        return lib.network_add_gate(self._ptr, type_, len(self._cookies))

    def add_link(self, source_index, dest_index, negate=False):
        assert dest_index >= 0
        assert source_index >= 0
        lib.network_add_link(self._ptr, source_index, dest_index, negate)

    def read(self, gate_index):
        assert gate_index >= 0
        return bool(lib.network_read(self._ptr, gate_index))

    def write(self, gate_index, value):
        assert gate_index >= 0
        lib.network_write(self._ptr, gate_index, value)

    def drain(self):
        return lib.network_drain(self._ptr)
