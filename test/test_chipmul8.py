import unittest
from random import Random
from unittest.mock import patch

from chipmul8 import Processor


class TestOpCodes(unittest.TestCase):
    def setUp(self) -> None:
        Processor.initialize()
        self.cpu = Processor()
        self.random = Random(10)

    def test_op_code_00e0(self):
        """
        00E0

        Clears the screen

        :return: None
        :rtype: None
        """

        op_code = 0x00E0
        self.cpu.current_op_code = op_code

        for y_index, row in enumerate(self.cpu.display_memory):
            for x_index, pixel in enumerate(row):
                self.cpu.display_memory[y_index][x_index] = 1

        self.cpu.execute_op_code()

        for y_index, row in enumerate(self.cpu.display_memory):
            for x_index, pixel in enumerate(row):
                self.assertEqual(0x0, self.cpu.display_memory[y_index][x_index])

    def test_op_code_00ee(self):
        """
        00EE

        Return from subroutine

        :return: None
        :rtype: None
        """

        # execute a subroutine
        self.test_op_code_2000()

        # return from the subroutine
        op_code = 0x00EE
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        self.assertEqual(0, self.cpu.stack_pointer)
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_1000(self):
        """
        1NNN

        goto NNN;

        :return: None
        :rtype: None
        """

        op_code = 0x12F0
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(op_code & 0x0FFF, self.cpu.program_counter)

    def test_op_code_2000(self):
        """
        2NNN

        Calls subroutine at NNN

        :return:
        :rtype:
        """

        op_code = 0x22F0
        self.cpu.current_op_code = op_code
        self.cpu.program_counter = 0x200
        self.cpu.execute_op_code()
        self.assertEqual(1, self.cpu.stack_pointer)
        self.assertEqual(0x200, self.cpu.stack[0])
        self.assertEqual(0x02F0, self.cpu.program_counter)

    def test_op_code_3000(self):
        """
        3XNN

        Skips the next instruction if VX equals NN

        :return: None
        :rtype: None
        """

        op_code = 0x32F0

        self.cpu.current_op_code = op_code
        self.cpu.registers[0x0200 >> 8] = 0x00F0
        self.cpu.execute_op_code()
        self.assertEqual(0x0204, self.cpu.program_counter)

        self.cpu.registers[0x0200 >> 8] = 0x00F1
        self.cpu.execute_op_code()
        self.assertEqual(0x0206, self.cpu.program_counter)

    def test_op_code_4000(self):
        """
        4XNN

        Skips the next instruction if VX does not equal NN

        :return: None
        :rtype: None
        """

        op_code = 0x42F0

        self.cpu.current_op_code = op_code
        self.cpu.registers[0x0200 >> 8] = 0x00F0
        self.cpu.execute_op_code()
        self.assertEqual(0x0202, self.cpu.program_counter)

        self.cpu.registers[0x0200 >> 8] = 0x00F1
        self.cpu.execute_op_code()
        self.assertEqual(0x0206, self.cpu.program_counter)

    def test_op_code_5000(self):
        """
        5XY0

        Skips the next instruction if VX equals VY

        :return: None
        :rtype: None
        """

        op_code = 0x5230

        self.cpu.current_op_code = op_code
        self.cpu.registers[2] = 0x00FF
        self.cpu.registers[3] = 0x00FF
        self.cpu.execute_op_code()
        self.assertEqual(0x204, self.cpu.program_counter)
        self.cpu.registers[2] = 0x00FF
        self.cpu.registers[3] = 0x00F1
        self.cpu.execute_op_code()
        self.assertEqual(0x206, self.cpu.program_counter)

    def test_op_code_6000(self):
        """
        6XNN

        Sets VX to NN

        :return: None
        :rtype: None
        """

        op_code = 0x62F0
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(op_code & 0x00FF, self.cpu.registers[2])
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_7000(self):
        """
        7XNN

        Adds NN to VX. (Carry flag is not changed)

        :return: None
        :rtype: None
        """

        op_code = 0x72F0
        self.cpu.current_op_code = op_code
        self.cpu.registers[2] = 0x00A2
        self.cpu.execute_op_code()
        self.assertEqual(402, self.cpu.registers[2])
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_8000(self):
        """
        8XY0

        Sets VX to the value of VY

        :return: None
        :rtype: None
        """

        op_code = 0x8230

        self.cpu.registers[2] = 0x11
        self.cpu.registers[3] = 0xF0
        self.cpu.program_counter = 0x200
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0xF0, self.cpu.registers[2])

        op_code = 0x82F0

        self.cpu.registers[0x2] = 0x11
        self.cpu.registers[0xF] = 0xF0

        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(0x204, self.cpu.program_counter)
        self.assertEqual(0xF0, self.cpu.registers[2])

    def test_op_code_8001(self):
        """
        8XY1

        Sets VX to VX or VY

        :return: None
        :rtype: None
        """

        op_code = 0x82F1
        self.cpu.registers[0x2] = 0x22
        self.cpu.registers[0xF] = 0x11
        self.cpu.program_counter = 0x200
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0x33, self.cpu.registers[0x2])

    def test_op_code_8002(self):
        """
        8XY2

        Sets VX to VX and VY

        :return: None
        :rtype: None
        """

        op_code = 0x85F2
        self.cpu.registers[0x5] = 0xF3
        self.cpu.registers[0xF] = 0x01
        self.cpu.program_counter = 0x200
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0x1, self.cpu.registers[0x5])

    def test_op_code_8003(self):
        """
        8XY3

        Sets VX to VX xor VY

        :return: None
        :rtype: None
        """

        op_code = 0x85F3
        self.cpu.registers[0x5] = 0xF3
        self.cpu.registers[0xF] = 0x01
        self.cpu.program_counter = 0x200
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0xF2, self.cpu.registers[0x5])

    def test_op_code_8004(self):
        """
        8XY4

        Adds VY to VX. VF is set to 1 when there is a carry, and to 0 when there isn't

        :return: None
        :rtype: None
        """

        op_code = 0x8234
        self.cpu.current_op_code = op_code

        self.cpu.registers[0x2] = 0x1
        self.cpu.registers[0x3] = 0x1

        self.cpu.execute_op_code()
        self.assertEqual(0x2, self.cpu.registers[0x2])
        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0x0, self.cpu.registers[0xF])

        self.cpu.registers[0x3] = 0xFF
        self.cpu.execute_op_code()
        self.assertEqual(0x1, self.cpu.registers[0xF])
        self.assertEqual(0x204, self.cpu.program_counter)

    def test_op_code_8005(self):
        """
        8XY5

        VY is subtracted from VX. VF is set to 0 when there is a borrow, and to 0 where there isn't

        :return: None
        :rtype: None
        """

        op_code = 0x8E25
        self.cpu.current_op_code = op_code
        self.cpu.registers[0xE] = 0xE
        self.cpu.registers[2] = 0x1
        self.cpu.execute_op_code()
        self.assertEqual(0xD, self.cpu.registers[0xE])
        self.assertEqual(0x1, self.cpu.registers[0xF])
        self.assertEqual(0x202, self.cpu.program_counter)

        self.cpu.registers[0xE] = 0x1
        self.cpu.registers[2] = 0x2
        self.cpu.execute_op_code()
        self.assertEqual(-0x1, self.cpu.registers[0xE])
        self.assertEqual(0x204, self.cpu.program_counter)
        self.assertEqual(0x0, self.cpu.registers[0xF])

    def test_op_code_8006(self):
        """
        8XY6

        Stores the least significant bit of VX in VF and then shifts VX to the right by 1

        :return: None
        :rtype: None
        """

        op_code = 0x82F6
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x2] = 0x3
        self.cpu.execute_op_code()
        self.assertEqual(0x1, self.cpu.registers[0xF])
        self.assertEqual(0x1, self.cpu.registers[0x2])
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_8007(self):
        """
        8XY7

        Sets VX to VY minus VX. VF is set to 0 when there is a borrow, and 1 when there isn't

        :return: None
        :rtype: None
        """

        op_code = 0x8237
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x2] = 0x4
        self.cpu.registers[0x3] = 0x8
        self.cpu.execute_op_code()
        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0x4, self.cpu.registers[0x2])
        self.assertEqual(0x1, self.cpu.registers[0xF])

        self.cpu.registers[0x2] = 0x8
        self.cpu.registers[0x3] = 0x4
        self.cpu.execute_op_code()
        self.assertEqual(-0x4, self.cpu.registers[0x2])
        self.assertEqual(0x204, self.cpu.program_counter)

    def test_op_code_800e(self):
        """
        8XYE

        Stores the most significant bit of VX in VF and then shifts VX to the left by 1

        :return: None
        :rtype: None
        """

        op_code = 0x823E
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x2] = 0x2
        self.cpu.execute_op_code()
        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0x0, self.cpu.registers[0xF])
        self.assertEqual(0x4, self.cpu.registers[0x2])

    def test_op_code_9000(self):
        """
        9XY0

        Skips the next instruction if VX doesn't equal VY

        :return:
        :rtype:
        """

        op_code = 0x9230

        self.cpu.current_op_code = op_code
        self.cpu.registers[2] = 0x00FF
        self.cpu.registers[3] = 0x00FF
        self.cpu.execute_op_code()
        self.assertEqual(0x202, self.cpu.program_counter)
        self.cpu.registers[2] = 0x00FF
        self.cpu.registers[3] = 0x00F1
        self.cpu.execute_op_code()
        self.assertEqual(0x206, self.cpu.program_counter)

    def test_op_code_a000(self):
        """
        ANNN

        Sets I to the address NNN.

        :return: None
        :rtype: None
        """

        op_code = 0xA2F0
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(op_code & 0x0FFF, self.cpu.register_i)
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_b000(self):
        """
        BNNN

        Jumps to the address NNN plus V0

        :return: None
        :rtype: None
        """

        op_code = 0xB111
        self.cpu.registers[0x0] = 0xF3
        self.cpu.program_counter = 0x200
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        self.assertEqual(0x204, self.cpu.program_counter)
        self.assertEqual(0xF3, self.cpu.registers[0x0])

    @patch('chipmul8.random')
    def test_op_code_c000(self, random):
        """
        CXNN

        Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN

        :return: None
        :rtype: None
        """

        random.randint._mock_side_effect = self.random.randint
        op_code = 0xC111

        self.cpu.registers[0x1] = 0xF3
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0x10, self.cpu.registers[0x1])

    def test_op_code_d000(self):
        """
        DXYN

        Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
        Each row of 8 pixels is read as bit-coded starting from memory location I;
        I value does not change after the execution of this instruction.
        As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn,
        and to 0 if that does not happen

        :return: None
        :rtype: None
        """

        op_code = 0xD004
        self.cpu.current_op_code = op_code
        self.cpu.register_i = 0x300
        self.cpu.ram.set_address(0x300, 0x10)
        self.cpu.ram.set_address(0x301, 0x28)
        self.cpu.ram.set_address(0x302, 0x44)
        self.cpu.ram.set_address(0x303, 0xFE)
        self.cpu.execute_op_code()

        sprite_coordinates = [
            (3, 0),
            (2, 1),
            (4, 1),
            (1, 2),
            (5, 2),
            (0, 3),
            (1, 3),
            (2, 3),
            (3, 3),
            (4, 3),
            (5, 3),
            (6, 3),
        ]

        for coordinate_x, coordinate_y in sprite_coordinates:
            print(coordinate_x, coordinate_y)
            self.assertEqual(0x1, self.cpu.display_memory[coordinate_y, coordinate_x])

        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_e09e(self):
        """
        EX9E

        Skips the next instruction if the key stored in VX is pressed

        :return: None
        :rtype: None
        """

        op_code = 0xE19E
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

        # key isn't pressed
        self.assertEqual(0x202, self.cpu.program_counter)

        # key is pressed
        self.cpu.registers[0x1] = 0x1
        self.cpu.keyboard[0x1] = True
        self.cpu.execute_op_code()
        self.assertEqual(0x206, self.cpu.program_counter)

    def test_op_code_e0a1(self):
        """
        EXA1

        Skips the next instruction if the key stored in VX isn't pressed

        :return: None
        :rtype: None
        """

        op_code = 0xE5A1
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x5] = 0x5
        self.cpu.keyboard[0x5] = True
        self.cpu.execute_op_code()

        # key is pressed
        self.assertEqual(0x202, self.cpu.program_counter)

        # key isn't pressed
        self.cpu.registers[0x5] = 0x5
        self.cpu.keyboard[0x5] = False
        self.cpu.execute_op_code()
        self.assertEqual(0x206, self.cpu.program_counter)

    def test_op_code_f007(self):
        """
        FX07

        Sets VX to the value of the delay timer

        :return: None
        :rtype: None
        """

        op_code = 0xF107
        self.cpu.current_op_code = op_code
        self.cpu.delay_register = 0xF
        self.cpu.execute_op_code()
        self.assertEqual(0xF, self.cpu.registers[0x1])
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_f00a(self):
        """
        FX0A

        A key press is awaited, and then stored in VX (Blocking operation)

        :return: None
        :rtype: None
        """

        op_code = 0xF20A
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(0x200, self.cpu.program_counter)

        # Simulate a key press
        self.cpu.keyboard[0xf] = True
        self.cpu.execute_op_code()
        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0xF, self.cpu.registers[0x2])

    def test_op_code_f015(self):
        """
        FX15

        Sets the delay timer to VX

        :return: None
        :rtype: None
        """

        op_code = 0xF315
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x3] = 0xF
        self.cpu.execute_op_code()
        self.assertEqual(0xF, self.cpu.delay_register)
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_f018(self):
        """
        FX18

        Sets the sound timer to VX

        :return: None
        :rtype: None
        """

        op_code = 0xF418
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x4] = 0xF
        self.cpu.execute_op_code()
        self.assertEqual(0xF, self.cpu.sound_register)
        self.assertEqual(0x202, self.cpu.program_counter)

    def test_op_code_f01e(self):
        """
        FX1E

        Adds VX to I

        VF is set to 1 when there is a range overflow (I + VX > 0xFFF), and to 0 when there isn't.

        :return: None
        :rtype: None
        """

        op_code = 0xF51E
        self.cpu.registers[0x5] = 0x1
        self.cpu.register_i = 0x1
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        self.assertEqual(0x2, self.cpu.register_i)
        self.assertEqual(0x0, self.cpu.registers[0xF])
        self.assertEqual(0x0202, self.cpu.program_counter)

        self.cpu.registers[0x5] = 0xFFF
        self.cpu.execute_op_code()
        self.assertEqual(0x1001, self.cpu.register_i)
        self.assertEqual(0x1, self.cpu.registers[0xF])
        self.assertEqual(0x0204, self.cpu.program_counter)

    def test_op_code_f029(self):
        """
        FX29

        Sets I to the location of the sprite for the character in VX
        Characters 0-F (in hexadecimal) are represented by a 4x5 font

        :return: None
        :rtype: None
        """

        op_code = 0xF229
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x2] = 0x2
        self.cpu.execute_op_code()
        self.assertEqual(0x202, self.cpu.program_counter)
        self.assertEqual(0xA, self.cpu.register_i)

    def test_op_code_f033(self):
        """
        FX33

        Stores the binary-coded decimal representation of VX, with the most significant of three digits at the
        address in I, the middle digit at I plus 1, and the least significant digit at I plus 2.

        :return: None
        :rtype: None
        """

        op_code = 0xF733
        self.cpu.current_op_code = op_code
        self.cpu.registers[0x7] = 0x2
        self.cpu.register_i = 0x300
        self.cpu.execute_op_code()
        self.assertEqual(0x0, self.cpu.ram[0x300])
        self.assertEqual(0x0, self.cpu.ram[0x301])
        self.assertEqual(0x2, self.cpu.ram[0x302])
        self.assertEqual(0x202, self.cpu.program_counter)

        self.cpu.registers[0x7] = 0x111
        self.cpu.execute_op_code()
        self.assertEqual(0x2, self.cpu.ram[0x300])
        self.assertEqual(0x7, self.cpu.ram[0x301])
        self.assertEqual(0x3, self.cpu.ram[0x302])
        self.assertEqual(0x204, self.cpu.program_counter)

    def test_op_code_f055(self):
        """
        FX55

        Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for
        each value written, but I itself is left unmodified

        :return: None
        :rtype: None
        """

        op_code = 0xFE55
        self.cpu.current_op_code = op_code
        self.cpu.register_i = 0x300
        self.cpu.registers[0x0] = 0xF
        self.cpu.registers[0x1] = 0xF
        self.cpu.execute_op_code()

        for index in range(0x300, 0x302):
            self.assertEqual(0xF, self.cpu.ram[index])

        self.assertEqual(0x202, self.cpu.program_counter)

        for index in range(0x0, 0xF):
            self.cpu.registers[index] = 0xFF

        self.cpu.execute_op_code()
        self.assertEqual(0x204, self.cpu.program_counter)

        for index in range(0x300, 0x30F):
            self.assertEqual(0xFF, self.cpu.ram[index])

    def test_op_code_f065(self):
        """
        FX65

        Fills V0 to VX (including VX) with values from memory starting at address I.
        The offset from I is increased by 1 for each value written, but I itself is left unmodified.

        :return: None
        :rtype: None
        """

        op_code = 0xFE65
        self.cpu.current_op_code = op_code
        self.cpu.register_i = 0x300

        for index in range(0x300, 0x30F):
            self.cpu.ram.set_address(index, 0xFF)

        self.cpu.execute_op_code()

        self.assertEqual(0x202, self.cpu.program_counter)

        for index in range(0x0, 0xF):
            self.assertEqual(0xFF, self.cpu.registers[index])


if __name__ == '__main__':
    unittest.main()
