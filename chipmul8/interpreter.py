"""
CHIP-8 Interpreter.
"""

from random import Random

import numpy as np
from hexdump import dumpgen

random = Random()

font_list = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,
    0x20, 0x60, 0x20, 0x20, 0x70,
    0xF0, 0x10, 0xF0, 0x80, 0xF0,
    0xF0, 0x10, 0xF0, 0x10, 0xF0,
    0x90, 0x90, 0xF0, 0x10, 0x10,
    0xF0, 0x80, 0xF0, 0x10, 0xF0,
    0xF0, 0x80, 0xF0, 0x90, 0xF0,
    0xF0, 0x10, 0x20, 0x40, 0x40,
    0xF0, 0x90, 0xF0, 0x90, 0xF0,
    0xF0, 0x90, 0xF0, 0x10, 0xF0,
    0xF0, 0x90, 0xF0, 0x90, 0x90,
    0xE0, 0x90, 0xE0, 0x90, 0xE0,
    0xF0, 0x80, 0x80, 0x80, 0xF0,
    0xE0, 0x90, 0x90, 0x90, 0xE0,
    0xF0, 0x80, 0xF0, 0x80, 0xF0,
    0xF0, 0x80, 0xF0, 0x80, 0x80
]


class MemoryBase:
    """
    Generic memory object.
    """

    def __init__(self, allocated_memory):
        """
        :param allocated_memory: Number o bytes of memory to allocate.
        :type allocated_memory: int
        """

        self.memory = bytearray(allocated_memory)

    def dump(self):
        """
        Display a memory hexdump.

        :return: None
        :rtype: None
        """

        for memory_address in dumpgen(self.memory):
            print(memory_address)

    @staticmethod
    def wrap_integer(number):
        """
        C-style integer wrapping to fit into integers into an unsigned char.

        :param number: Integer to wrap.
        :type number: int
        :return: Wrapped integer.
        :rtype: int
        """

        return number % 256

    def set_address(self, address, value):
        """
        Sets the memory address to the provided value.

        :param address: Address to set.
        :type address: int
        :param value: Value to assign.
        :type value: int
        :return: None
        :rtype: None
        """

        self.memory[address] = self.wrap_integer(value)

    def __setitem__(self, key, value):
        """
        Sets the memory address to the provided value.

        :param key: Address to set.
        :type key: int
        :param value: Value to assign.
        :type value: int
        :return: None
        :rtype: None
        """

        self.memory[key] = self.wrap_integer(value)

    def __getitem__(self, item):
        """
        Retrieve the value of memory at the provided address.

        :param item: Memory address.
        :type item: int
        :return: Memory value for provided address.
        :rtype: int
        """

        return self.memory[item]


class Interpreter:
    """
    Chip8 Interpreter.
    """

    instruction_set = None

    @classmethod
    def initialize(cls):
        """
        Loads op codes.

        :return: None
        :rtype: None
        """

        cls.instruction_set = {
            op_code_lookup[7:]: op_code_lookup
            for op_code_lookup in cls.__dict__ if str(op_code_lookup).startswith('opcode_')
        }

    def __init__(self, start_address=0x200):
        """
        :param start_address: Interpreter memory start location.
        :type start_address: int
        """

        self.ram = MemoryBase(4096)
        self.registers = MemoryBase(16)

        self.stack = [0] * 16
        self.register_i = 0
        self.program_counter = start_address
        self.stack_pointer = 0

        self.delay_register = 0
        self.sound_register = 0

        self.current_op_code = 0

        self.display_memory = np.zeros(shape=(32, 64), dtype=np.int8)

        self.keyboard = [False] * 16
        self.frame_ready = False

        for index, font_item in enumerate(font_list):
            self.ram.set_address(index, font_item)

    def load_rom(self, rom_path):
        """
        Loads a rom into memory.

        :param rom_path: Path to rom file.
        :type rom_path: str | Path
        :return: None
        :rtype: None
        """

        with open(rom_path, 'rb') as rom_file:
            for index, line in enumerate(rom_file.read()):
                self.ram.set_address(0x200 + index, line)

    def emulate(self):
        """
        Executes one emulation cycle of the interpreter.

        :return: None
        :rtype: None
        """

        self.current_op_code = self.ram[self.program_counter] << 8 | self.ram[self.program_counter + 1]
        self.execute_op_code()

        if self.delay_register > 0:
            self.delay_register -= 1

        if self.sound_register > 0:
            self.sound_register -= 1

    def execute_op_code(self):
        """
        Executes the current opcode.

        :return: None
        :rtype: None
        """

        lookup_code = hex(self.current_op_code & 0xF000)[2:]

        try:
            getattr(self, self.instruction_set[lookup_code])()
        except Exception as e:
            print(f"Executing opcode: {hex(self.current_op_code)}")
            print(e)

    def opcode_0(self):
        """
        00EN

        :return: None
        :rtype: None
        """

        def sub_op_code_00e0():
            """
            00E0

            Clear the screen.

            :return: None
            :rtype: None
            """

            self.display_memory = np.zeros(shape=(32, 64), dtype=np.int8)
            self.program_counter += 2

        def sub_op_code_00ee():
            """
            00EE

            Return from subroutine.

            :return: None
            :rtype: None
            """

            self.program_counter = self.stack[self.stack_pointer - 1]
            self.stack_pointer -= 1
            self.program_counter += 2

        sub_op_code_lookup = {
            0x00E0: sub_op_code_00e0,
            0x00EE: sub_op_code_00ee
        }

        sub_op_code = sub_op_code_lookup[(self.current_op_code & 0x00FF)]
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
        """
        2NNN

        Calls subroutine at NNN.

        :return: None
        :rtype: None
        """

        self.stack[self.stack_pointer] = self.program_counter
        self.stack_pointer += 1
        self.program_counter = self.current_op_code & 0x0FFF

    def opcode_3000(self):
        """
        3XNN

        Skips the next instruction if VX equals NN.

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

        Skips the next instruction if VX does not equal NN.

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

        Skips the next instruction if VX equals VY.

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

        Sets VX to NN.

        :return: None
        :rtype: None
        """

        self.registers[(self.current_op_code & 0x0F00) >> 8] = self.current_op_code & 0x00FF

        self.program_counter += 2

    def opcode_7000(self):
        """
        7XNN

        Adds NN to VX. (Carry flag is not changed).

        :return: None
        :rtype: None
        """

        register_address = (self.current_op_code & 0x0F00) >> 8

        self.registers[register_address] = self.registers[register_address] + self.current_op_code & 0x00FF

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

            Sets VX to the value of VY.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[y]
            self.program_counter += 2

        def sub_op_code_8001(x, y):
            """
            8XY1

            Sets VX to VX or VY.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[x] | self.registers[y]
            self.program_counter += 2

        def sub_op_code_8002(x, y):
            """
            8XY2

            Sets VX to VX and VY.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[x] & self.registers[y]
            self.program_counter += 2

        def sub_op_code_8003(x, y):
            """
            8XY3

            Sets VX to VX xor VY.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.registers[x] ^ self.registers[y]
            self.program_counter += 2

        def sub_op_code_8004(x, y):
            """
            8XY4

            Adds VY to VX. VF is set to 1 when there is a carry, and to 0 when there isn't.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            if self.registers[y] > (0xFF - self.registers[x]):
                self.registers[0xF] = 1
            else:
                self.registers[0xF] = 0

            self.registers[x] = self.registers[x] + self.registers[y]

            self.program_counter += 2

        def sub_op_code_8005(x, y):
            """
            8XY5

            VY is subtracted from VX. VF is set to 0 when there is a borrow, and to 0 where there isn't.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            if self.registers[y] > self.registers[x]:
                self.registers[0xF] = 0
            else:
                self.registers[0xF] = 1

            self.registers[x] = self.registers[x] - self.registers[y]

            self.program_counter += 2

        def sub_op_code_8006(x, y):
            """
            8XY6

            Stores the least significant bit of VX in VF and then shifts VX to the right by 1.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            _ = y
            self.registers[0xF] = self.registers[x] & 0x1
            self.registers[x] >>= 0x1

            self.program_counter += 2

        def sub_op_code_8007(x, y):
            """
            8XY7

            Sets VX to VY minus VX. VF is set to 0 when there is a borrow, and 1 when there isn't.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            if self.registers[x] > self.registers[y]:
                self.registers[0xF] = 0
            else:
                self.registers[0xF] = 1

            self.registers[x] = self.registers[y] - self.registers[x]

            self.program_counter += 2

        def sub_op_code_800e(x, y):
            """
            8XYE

            Stores the most significant bit of VX in VF and then shifts VX to the left by 1.

            :param x: Value of X in in current opcode (8XYN).
            :type x: int
            :param y: Value of Y in current opcode (8XYN).
            :type y: int
            :return: None
            :rtype: None
            """

            _ = y
            self.registers[0xF] = self.registers[x] >> 7
            self.registers[x] <<= 1

            self.program_counter += 2

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

        sub_op_code(x_value, y_value)

    def opcode_9000(self):
        """
        9XY0

        Skips the next instruction if VX doesn't equal VY.

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
        """
        BNNN

        Jumps to the address NNN plus V0.

        :return: None
        :rtype: None
        """

        self.program_counter = (self.current_op_code & 0x0FFF) + self.registers[0x0]

    def opcode_c000(self):
        """
        CXNN

        Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.

        :return: None
        :rtype: None
        """

        self.registers[(self.current_op_code & 0x0F00) >> 8] = (self.current_op_code & 0x00FF) & random.randint(0, 255)
        self.program_counter += 2

    def opcode_d000(self):
        """
        DXYN

        Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
        Each row of 8 pixels is read as bit-coded starting from memory location I;
        I value does not change after the execution of this instruction.
        As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn,
        and to 0 if that does not happen.

        :return: None
        :rtype: None
        """

        x_coordinate = self.registers[(self.current_op_code & 0x0F00) >> 8]
        y_coordinate = self.registers[(self.current_op_code & 0x00F0) >> 4]
        height = self.current_op_code & 0x000F

        self.registers[0xF] = 0x0

        for y_sprite_coordinate in range(0, height):
            sprite_row = self.ram[self.register_i + y_sprite_coordinate]

            for x_sprite_coordinate, bit in enumerate("{0:08b}".format(sprite_row)):
                if int(bit) == 0x1:
                    x = x_sprite_coordinate + x_coordinate
                    y = y_sprite_coordinate + y_coordinate

                    try:
                        if self.display_memory[y, -x - 1] == 0:
                            self.registers[0xF] = 1

                        self.display_memory[y, -x - 1] ^= 1
                    except Exception:
                        print(self.registers)
                        exit()

        self.frame_ready = True
        self.program_counter += 2

    def opcode_e000(self):
        """
        EXNN

        :return: None
        :rtype: None
        """

        def sub_op_code_ex9e(x):
            """
            EX9E

            Skips the next instruction if the key stored in VX is pressed.

            :param x: Value of X from opcode (EX9E).
            :type x: int
            :return: None
            :rtype: None
            """

            if self.keyboard[self.registers[x]] is True:
                self.program_counter += 4
            else:
                self.program_counter += 2

        def sub_op_code_exa1(x):
            """
            EXA1

            Skips the next instruction if the key stored in VX isn't pressed.

            :param x: Value if X from opcode (EXA1).
            :type x: int
            :return: None
            :rtype: None
            """

            if self.keyboard[self.registers[x]] is False:
                self.program_counter += 4
            else:
                self.program_counter += 2

        sub_op_code_lookup = {
            0xe09E: sub_op_code_ex9e,
            0xe0A1: sub_op_code_exa1
        }

        sub_op_code = sub_op_code_lookup[(self.current_op_code & 0xF0FF)]
        x_value = (self.current_op_code & 0x0F00) >> 8

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

            Sets VX to the value of the delay timer.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            self.registers[x] = self.delay_register
            self.program_counter += 2

        def sub_op_code_fx0a(x):
            """
            FX0A

            A key press is awaited, and then stored in VX (Blocking operation).

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            current_program_counter = self.program_counter

            for index, key in enumerate(self.keyboard):
                if key:
                    self.registers[x] = index
                    self.program_counter += 2
                    break

            if self.program_counter <= current_program_counter:
                return

        def sub_op_code_fx15(x):
            """
            FX15

            Sets the delay timer to VX.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            self.delay_register = self.registers[x]

            self.program_counter += 2

        def sub_op_code_fx18(x):
            """
            FX18

            Sets the sound timer to VX.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            self.sound_register = self.registers[x]

            self.program_counter += 2

        def sub_op_code_fx1e(x):
            """
            FX1E

            Adds VX to I.

            VF is set to 1 when there is a range overflow (I+VX>0xFFF), and to 0 when there isn't.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            self.register_i += self.registers[x]

            if self.register_i + self.registers[x] > 0xFFF:
                self.registers[0xF] = 1
            else:
                self.registers[0xF] = 0

            self.program_counter += 2

        def sub_op_code_fx29(x):
            """
            FX29

            Sets I to the location of the sprite for the character in VX.
            Characters 0-F (in hexadecimal) are represented by a 4x5 font.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            # Each sprite is 5 bytes long (each sprite will use up 5 memory addresses)
            self.register_i = self.registers[x] * 0x5

            self.program_counter += 2

        def sub_op_code_fx33(x):
            """
            FX33

            Stores the binary-coded decimal representation of VX, with the most significant of three digits at the
            address in I, the middle digit at I plus 1, and the least significant digit at I plus 2.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            int_string = "{0:03}".format(self.registers[x])

            for index, character in enumerate(int_string):
                self.ram.set_address(self.register_i + index, int(character))

            self.program_counter += 2

        def sub_op_code_fx55(x):
            """
            FX55

            Stores V0 to VX (including VX) in memory starting at address I.
            The offset from I is increased by 1 for each value written, but I itself is left unmodified.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            temp_i = self.register_i

            for index in range(0x0, x + 0x1):
                self.ram.set_address(temp_i, self.registers[index])
                temp_i += 1

            self.program_counter += 2

        def sub_op_code_fx65(x):
            """
            FX65

            Fills V0 to VX (including VX) with values from memory starting at address I.
            The offset from I is increased by 1 for each value written, but I itself is left unmodified.

            :param x: X value from current opcode (FXNN).
            :type x: int
            :return: None
            :rtype: None
            """

            temp_i = self.register_i

            for index in range(0x0, x + 0x1):
                self.registers[index] = self.ram[temp_i]
                temp_i += 1

            self.program_counter += 2

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

        sub_op_code(x_value)
