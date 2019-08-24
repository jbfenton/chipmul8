import unittest
from chipmul8 import Processor


class TestOpCodes(unittest.TestCase):
    def setUp(self) -> None:
        Processor.initialize()
        self.cpu = Processor()

    def test_op_code_00e0(self):
        """
        00E0

        Clears the screen

        :return: None
        :rtype: None
        """

        op_code = 0x00E0
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

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

        op_code = 0x82F5
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

    def test_op_code_8006(self):
        """
        8XY6

        Stores the least significant bit of VX in VF and then shifts VX to the right by 1

        :return: None
        :rtype: None
        """

        op_code = 0x82F6
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

    def test_op_code_8007(self):
        """
        8XY7

        Sets VX to VY minus VX. VF is set to 0 when there is a borrow, and 1 when there isn't

        :return: None
        :rtype: None
        """

        op_code = 0x82F7
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

    def test_op_code_800e(self):
        """
        8XYE

        Stores the most significant bit of VX in VF and then shifts VX to the left by 1

        :return: None
        :rtype: None
        """

        op_code = 0x82FE
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

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
        self.cpu.execute_op_code()

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

    def test_op_code_f015(self):
        """
        FX15

        Sets the delay timer to VX

        :return: None
        :rtype: None
        """

        op_code = 0xF315
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

    def test_op_code_f018(self):
        """
        FX18

        Sets the sound timer to VX

        :return: None
        :rtype: None
        """

        op_code = 0xF418
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

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

        op_code = 0xF629
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

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
        self.cpu.execute_op_code()

    def test_op_code_f055(self):
        """
        FX55

        Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for
        each value written, but I itself is left unmodified

        :return: None
        :rtype: None
        """

        op_code = 0xF155
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()

    def test_op_code_f065(self):
        """
        FX65

        Fills V0 to VX (including VX) with values from memory starting at address I.
        The offset from I is increased by 1 for each value written, but I itself is left unmodified.

        :return: None
        :rtype: None
        """

        op_code = 0xF265
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()


if __name__ == '__main__':
    unittest.main()
