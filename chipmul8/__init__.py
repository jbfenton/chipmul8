from hexdump import dumpgen


class RandomAccessMemory:
    def __init__(self, allocated_memory=4096):
        self.memory = bytearray(allocated_memory)

    def set_address(self, address, value):
        self.memory[address] = value

    def dump(self):
        for memory_address in dumpgen(self.memory):
            print(memory_address)


class Processor:
    instruction_set = None

    @classmethod
    def initialize(cls):
        cls.instruction_set = {
            op_code_lookup[7:]: op_code_lookup
            for op_code_lookup in cls.__dict__ if str(op_code_lookup).startswith('opcode_')
        }

    def __init__(self):
        self.ram = RandomAccessMemory()
        self.registers = [0] * 16
        self.register_i = 0
        self.program_counter = 0
        self.stack_pointer = 0

        self.delay_register = 0
        self.sound_register = 0

        self.current_op_code = 0

    def execute_op_code(self):
        lookup_code = hex(self.current_op_code & 0xF000)[2:]
        print(f"Executing opcode: {hex(self.current_op_code)}")
        print(f"Executing opcode (lookup): {lookup_code}")

        getattr(self, self.instruction_set[lookup_code])()

    def opcode_a000(self):
        print('opcode_a000')
        self.register_i = self.current_op_code & 0x0FFF


if __name__ == '__main__':
    Processor.initialize()
    cpu = Processor()
