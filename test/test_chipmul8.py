import unittest
from chipmul8 import Processor


class TestOpCodes(unittest.TestCase):
    def setUp(self) -> None:
        Processor.initialize()
        self.cpu = Processor()

    def test_op_code_a000(self):
        op_code = 0xA2F0
        self.cpu.current_op_code = op_code
        self.cpu.execute_op_code()
        print(hex(self.cpu.register_i))

        self.assertEqual(op_code & 0x0FFF, self.cpu.register_i)


if __name__ == '__main__':
    unittest.main()
