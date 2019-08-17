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

    def opcode_0(self):
        """
        00EN

        :return: None
        :rtype: None
        """

        def sub_op_code_00e0():
            """
            00E0

            Clear the screen

            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_00ee():
            """
            00EE

            Return from subroutine

            :return: None
            :rtype: None
            """

            pass

        sub_op_code_lookup = {
            0x00E0: sub_op_code_00e0,
            0x00EE: sub_op_code_00ee
        }

        sub_op_code = sub_op_code_lookup[(self.current_op_code & 0x00FF)]
        print(f"Executing: {sub_op_code.__name__}")

        sub_op_code()

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
        """
        8XYN

        :return: None
        :rtype: None
        """

        def sub_op_code_8000(x, y):
            """
            8XY0

            Sets VX to the value of VY

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[y]
            self.program_counter += 2

        def sub_op_code_8001(x, y):
            """
            8XY1

            Sets VX to VX or VY

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[x] | self.registers[y]
            self.program_counter += 2

        def sub_op_code_8002(x, y):
            """
            8XY2

            Sets VX to VX and VY

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[x] & self.registers[y]
            self.program_counter += 2

        def sub_op_code_8003(x, y):
            """
            8XY3

            Sets VX to VX xor VY

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[x] ^ self.registers[y]
            self.program_counter += 2

        def sub_op_code_8004(x, y):
            """
            8XY4

            Adds VY to VX. VF is set to 1 when there is a carry, and to 0 when there isn't

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_8005(x, y):
            """
            8XY5

            VY is subtracted from VX. VF is set to 0 when there is a borrow, and to 0 where there isn't

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_8006(x, y):
            """
            8XY6

            Stores the least significant bit of VX in VF and then shifts VX to the right by 1

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_8007(x, y):
            """
            8XY7

            Sets VX to VY minus VX. VF is set to 0 when there is a borrow, and 1 when there isn't

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_800e(x, y):
            """
            8XYE

            Stores the most significant bit of VX in VF and then shifts VX to the left by 1

            :param x: Value of X in in current opcode (8XYN)
            :type x: int
            :param y: Value of Y in current opcode (8XYN)
            :type y: int
            :return: None
            :rtype: None
            """

            pass

        sub_op_code_lookup = {
            0x8000: sub_op_code_8000,
            0x8001: sub_op_code_8001,
            0x8002: sub_op_code_8002,
            0x8003: sub_op_code_8003,
            0x8004: sub_op_code_8004,
            0x8005: sub_op_code_8005,
            0x8006: sub_op_code_8006,
            0x8007: sub_op_code_8007,
            0x800e: sub_op_code_800e
        }

        x_value = (self.current_op_code & 0x0F00) >> 8
        y_value = (self.current_op_code & 0x00F0) >> 4

        sub_op_code = sub_op_code_lookup[(self.current_op_code & 0xF00F)]
        print(f"Executing: {sub_op_code.__name__}")

        sub_op_code(x_value, y_value)

    def opcode_9000(self):
        """
        9XY0

        Skips the next instruction if VX doesn't equal VY
        :return: None
        :rtype: None
        """

        if self.registers[(self.current_op_code & 0x0F00) >> 8] != self.registers[(self.current_op_code & 0x00F0) >> 4]:
            self.program_counter += 4
        else:
            self.program_counter += 2

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
        """
        EXNN

        :return: None
        :rtype: None
        """

        def sub_op_code_ex9e(x):
            """
            EX9E

            Skips the next instruction if the key stored in VX is pressed

            :param x: Value of X from opcode (EX9E)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_exa1(x):
            """
            EXA1

            Skips the next instruction if the key stored in VX isn't pressed

            :param x: Value if X from opcode (EXA1)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        sub_op_code_lookup = {
            0xe09E: sub_op_code_ex9e,
            0xe0A1: sub_op_code_exa1
        }

        sub_op_code = sub_op_code_lookup[(self.current_op_code & 0xF0FF)]
        x_value = (self.current_op_code & 0x0F00) >> 8

        print(f"Executing: {sub_op_code.__name__}")

        sub_op_code(x_value)

    def opcode_f000(self):
        """
        FXNN

        :return: None
        :rtype: None
        """

        def sub_op_code_fx07(x):
            """
            FX07

            Sets VX to the value of the delay timer

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx0a(x):
            """
            FX0A

            A key press is awaited, and then stored in VX (Blocking operation)

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx15(x):
            """
            FX15

            Sets the delay timer to VX

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx18(x):
            """
            FX18

            Sets the sound timer to VX

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx1e(x):
            """
            FX1E

            Adds VX to I

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx29(x):
            """
            FX29

            Sets I to the location of the sprite for the character in VX
            Characters 0-F (in hexadecimal) are represented by a 4x5 font

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx33(x):
            """
            FX33

            Stores the binary-coded decimal representation of VX, with the most significant of three digits at the
            address in I, the middle digit at I plus 1, and the least significant digit at I plus 2.

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx55(x):
            """
            FX55

            Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for
            each value written, but I itself is left unmodified

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        def sub_op_code_fx65(x):
            """
            FX65

            Fills V0 to VX (including VX) with values from memory starting at address I.
            The offset from I is increased by 1 for each value written, but I itself is left unmodified.

            :param x: X value from current opcode (FXNN)
            :type x: int
            :return: None
            :rtype: None
            """

            pass

        sub_op_code_lookup = {
            0xF007: sub_op_code_fx07,
            0xF00a: sub_op_code_fx0a,
            0xF015: sub_op_code_fx15,
            0xF018: sub_op_code_fx18,
            0xF01E: sub_op_code_fx1e,
            0xF029: sub_op_code_fx29,
            0xF033: sub_op_code_fx33,
            0xF055: sub_op_code_fx55,
            0xF065: sub_op_code_fx65
        }

        sub_op_code = sub_op_code_lookup[(self.current_op_code & 0xF0FF)]
        x_value = (self.current_op_code & 0x0F00) >> 8

        print(f"Executing: {sub_op_code.__name__}")

        sub_op_code(x_value)


if __name__ == '__main__':
    Processor.initialize()
    cpu = Processor()
