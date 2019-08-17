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

    def __init__(self, start_address=0x200):
        self.ram = RandomAccessMemory()
        self.registers = [0] * 16
        self.register_i = 0
        self.program_counter = start_address
        self.stack_pointer = 0

        self.delay_register = 0
        self.sound_register = 0

        self.current_op_code = 0

    def execute_op_code(self):
        lookup_code = hex(self.current_op_code & 0xF000)[2:]
        print(f"Executing opcode: {hex(self.current_op_code)}")
        print(f"Executing opcode (lookup): {lookup_code}")

        getattr(self, self.instruction_set[lookup_code])()

    def opcode_0000(self):
        pass

    def opcode_1000(self):
        """
        1NNN

        goto NNN;

        :return: None
        :rtype: None
        """

        self.program_counter = self.current_op_code & 0x0FFF

    def opcode_2000(self):
        pass

    def opcode_3000(self):
        """
        3XNN

        Skips the next instruction if VX equals NN

        :return: None
        :rtype: None
        """

        if self.registers[(self.current_op_code & 0x0F00) >> 8] == self.current_op_code & 0x00FF:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def opcode_4000(self):
        """
        4XNN

        Skips the next instruction if VX does not equal NN

        :return: None
        :rtype: None
        """

        if self.registers[(self.current_op_code & 0x0F00) >> 8] != self.current_op_code & 0x00FF:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def opcode_5000(self):
        """
        5XY0

        Skips the next instruction if VX equals VY

        :return: None
        :rtype: None
        """

        if self.registers[(self.current_op_code & 0x0F00) >> 8] == self.registers[(self.current_op_code & 0x00F0) >> 4]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def opcode_6000(self):
        """
        6XNN

        Sets VX to NN

        :return: None
        :rtype: None
        """

        self.registers[(self.current_op_code & 0x0F00) >> 8] = self.current_op_code & 0x00FF
        self.program_counter += 2

    def opcode_7000(self):
        """
        7XNN

        Adds NN to VX. (Carry flag is not changed)

        :return: None
        :rtype: None
        """

        self.registers[(self.current_op_code & 0x0F00) >> 8] += self.current_op_code & 0x00FF
        self.program_counter += 2

    def opcode_8000(self):
        pass

    def opcode_9000(self):
        pass

    def opcode_a000(self):
        """
        ANNN

        Sets I to the address NNN.

        :return: None
        :rtype: None
        """

        self.register_i = self.current_op_code & 0x0FFF
        self.program_counter += 2

    def opcode_b000(self):
        pass

    def opcode_c000(self):
        pass

    def opcode_d000(self):
        pass

    def opcode_e000(self):
        pass

    def opcode_f000(self):
        pass


if __name__ == '__main__':
    Processor.initialize()
    cpu = Processor()
