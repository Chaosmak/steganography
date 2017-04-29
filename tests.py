#!/usr/bin/env python3
import unittest
import datetime
import version2 as solve


class SteganographyTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filename(self):
        for i in range(8):
            self.assertEqual("Отсутствует данный bmp фаил",
                             solve.encrypt_in("WrongName.bmp", "message.txt", "output.txt", i))

    def test_extension(self):
        for i in range(8):
            self.assertEqual("Расширение изображения должно быть .bmp",
                             solve.encrypt_in("WrongName.jpg", "message.txt", "output.txt", i))

    def test_msg_file(self):
        for i in range(8):
            self.assertEqual("Расширение изображения должно быть .bmp",
                             solve.encrypt_in("WrongName.jpg", "message.txt", "output.txt", i))

    def test_bytes_to_bits(self):
        bits = [int(i) for i in "01110100011001010111001101110100"]
        self.assertEqual(solve.bytes_to_bits(bytes("test", "utf8")), bits)

    def test_bits_to_bytes(self):
        result_bytes = solve.bits_to_bytes("01110100011001010111001101110100")
        result = ''
        for i in result_bytes:
            result += i.decode("utf-8")
        self.assertEqual(result, "test")

    def test_many_converts(self):
        s = "string"
        for i in range(20):
            bits = solve.bytes_to_bits(bytes(s, "utf8"))
            bits_res = ''
            for k in bits:
                bits_res += str(k)
            bytes_res = solve.bits_to_bytes(bits_res)
            result = ''
            for k in bytes_res:
                result += k.decode("utf-8")
            self.assertEqual(s, result)
            s += chr(100+i)

    @staticmethod
    def all_with_n(n):
        solve.encrypt_in("test28.bmp", "message.txt", "output.bmp", n)
        solve.decode_bmp("output.bmp", n)
        input_file = solve.get_bytes_from_file("message.txt")
        output_file = solve.get_bytes_from_file("output.txt")
        return input_file, output_file

    def test_1(self):
        res = SteganographyTest.all_with_n(1)
        self.assertEqual(res[0], res[1])

    def test_2(self):
        res = SteganographyTest.all_with_n(2)
        self.assertEqual(res[0], res[1])

    def test_3(self):
        res = SteganographyTest.all_with_n(3)
        self.assertEqual(res[0], res[1])

    def test_4(self):
        res = SteganographyTest.all_with_n(4)
        self.assertEqual(res[0], res[1])

    def test_5(self):
        res = SteganographyTest.all_with_n(5)
        self.assertEqual(res[0], res[1])

    def test_6(self):
        res = SteganographyTest.all_with_n(6)
        self.assertEqual(res[0], res[1])

    def test_7(self):
        res = SteganographyTest.all_with_n(7)
        self.assertEqual(res[0], res[1])

    def test_8(self):
        res = SteganographyTest.all_with_n(8)
        self.assertEqual(res[0], res[1])

if __name__ == '__main__':
    unittest.main()







