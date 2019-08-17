import unittest
from chipmul8 import Processor


class TestOpCodes(unittest.TestCase):
    def setUp(self) -> None:
        Processor.initialize()
        self.cpu = Processor()

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


if __name__ == '__main__':
    unittest.main()
