import unittest
from register_manager import register_manager

class TestRegisterConversion(unittest.TestCase):
    def test_u16(self):
        # 12345 -> [12345]
        res = register_manager._convert_to_registers(12345, 'U16', 'big')
        self.assertEqual(res, [12345])

    def test_s16_positive(self):
        # 123 -> [123]
        res = register_manager._convert_to_registers(123, 'S16', 'big')
        self.assertEqual(res, [123])

    def test_s16_negative(self):
        # -1 -> [65535] (0xFFFF)
        res = register_manager._convert_to_registers(-1, 'S16', 'big')
        self.assertEqual(res, [65535])

    def test_u32(self):
        # 0x12345678 -> [0x1234, 0x5678] (Big Endian)
        # 0x1234 = 4660, 0x5678 = 22136
        val = 0x12345678
        res = register_manager._convert_to_registers(val, 'U32', 'big')
        self.assertEqual(res, [0x1234, 0x5678])

    def test_float(self):
        # 123.45 in IEEE 754 float
        # Hex: 0x42f6e666
        # High word: 0x42f6 = 17142
        # Low word: 0xe666 = 58982
        val = 123.45
        res = register_manager._convert_to_registers(val, 'FLOAT', 'big')
        self.assertEqual(res, [17142, 58982])

    def test_float_little_endian(self):
        # 123.45 in IEEE 754 float Little Endian byte order for words?
        # Usually Modbus Float is Big Endian words, or Swapped words.
        # Our implementation of 'little' passed to struct.pack('<f')
        # <f = little endian bytes. 0x66 0xe6 0xf6 0x42
        # Then unpack('<HH') -> 0xe666, 0x42f6
        val = 123.45
        res = register_manager._convert_to_registers(val, 'FLOAT', 'little')
        # Should be swapped words of big endian?
        # 0xe666 = 58982, 0x42f6 = 17142
        self.assertEqual(res, [58982, 17142])

if __name__ == '__main__':
    unittest.main()
