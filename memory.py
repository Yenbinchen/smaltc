class SystemMemory:
    def __init__(self, start_address=1000):
        self.start_address = start_address
        self.buffer = bytearray(65536)
        self.alloc_ptr = start_address

    def allocate(self, size):
        if self.alloc_ptr + size > len(self.buffer):
            raise RuntimeError("記憶體溢出")
        addr = self.alloc_ptr
        self.alloc_ptr += size
        return addr

    def read_char(self, address):
        if address == 0:
            raise RuntimeError("error: Null pointer dereference")
        return int.from_bytes(self.buffer[address:address+1], byteorder='little', signed=True)

    def read_int(self, address):
        if address == 0:
            raise RuntimeError("error: Null pointer dereference")
        return int.from_bytes(self.buffer[address:address+4], byteorder='little', signed=True)

    def write_char(self, address, value):
        if address == 0:
            raise RuntimeError("error: Null pointer dereference")
        self.buffer[address:address+1] = int(value).to_bytes(1, byteorder='little', signed=True)

    def write_int(self, address, value):
        if address == 0:
            raise RuntimeError("error: Null pointer dereference")
        self.buffer[address:address+4] = int(value).to_bytes(4, byteorder='little', signed=True)

    def reset(self):
        self.alloc_ptr = self.start_address
        self.buffer = bytearray(65536)
