#!/usr/bin/env python3
from PIL import Image
import sys


class NewImage:
    def __init__(self, width, height, old_image):
        self.width = width
        self.height = height
        self.image = Image.new('RGB', (width, height))
        self.old = old_image

    def add_marker(self):
        """
        Поставим в пиксель (0,0) информацию, что есть сообщение:
        будем распознавать есть ли инфа по "111" в последних трех битах каждого цвета
        """
        rgb = []
        for color in self.old.getpixel((0, 0)):
            rgb.append(edit_last_n(color, [1, 1, 1], 3))
        self.image.putpixel((0, 0), (rgb[0], rgb[1], rgb[2]))

    def add_length_info(self, msg_length):
        """
        Используем 4 пикселя в изображении для того, чтоб занести туда
        длину кодируемого сообщения.
        """
        def edit_color(pixel, info):
            r, g, b = pixel
            r = edit_last_n(r, info[:2], 2)
            g = edit_last_n(g, info[2:5], 3)
            b = edit_last_n(b, info[5:], 3)
            return r, g, b
        # Раскладываем число
        temp = [msg_length // 255**3]
        temp.append((msg_length - temp[0] * 255**3) // 255**2)
        temp.append((msg_length - temp[0] * 255**3 - temp[1] * 255**2) // 255)
        temp.append(msg_length - temp[0] * 255**3 - temp[1] * 255**2 - temp[2] * 255)
        for k in range(1, 5):
            pixels = self.old.getpixel((k, 0))
            modified_pixels = edit_color(pixels, "{0:08b}".format(temp[k - 1]))
            self.image.putpixel((k, 0), modified_pixels)

    def edit_pixel(self, msg, i, j, n):
        """
        Если имеется сообщение msg, то кодирует его в n последних бит каждого цвета
        Иначе просто возвращает неизмененный бит
        :param msg:
        :param i:
        :param j:
        :param n:
        :return:
        """
        r, g, b = self.old.getpixel((i, j))
        if len(msg) > 0:
            r = edit_last_n(r, msg[0:n], n)
            g = edit_last_n(g, msg[n:2 * n], n)
            b = edit_last_n(b, msg[2 * n:3 * n], n)
        self.image.putpixel((i, j), (r, g, b))


def encode(image_name, message_name, output_name, n):
    """
    Кодирует в картинку image_name файл по битам из message_name
    Сохраняет в картинку под именем output_name
    n - сколько бит с конца заменять у каждого цвета в пиксиле
    """
    if not image_name.endswith(".bmp"):
        return "Расширение изображения должно быть .bmp"
    try:
        image = Image.open(image_name).convert('RGB')
    except FileNotFoundError:
        #print("Отсутствует данный bmp фаил")
        return "Отсутствует данный bmp фаил"
    width = image.width
    height = image.height
    try:
        byte_file = get_bytes_from_file(message_name)
    except FileNotFoundError:
       # print("Отсутствует фаил с сообщением")
        return "Отсутствует фаил с сообщением"
    bin_msg = bytes_to_bits(byte_file)
    msg_len = len(bin_msg)
    if msg_len <= n*3*width*height-5:
        pos = 0
        next_im = NewImage(width, height, image)
        next_im.add_marker()
        next_im.add_length_info(msg_len)
        for i in range(width):
            for j in range(height):
                if i < 5 and j == 0:
                    continue
                try:
                    bin_msg_array = bin_msg[pos:pos+n*3]
                except IndexError:
                    bin_msg_array = bin_msg[pos:]
                next_im.edit_pixel(bin_msg_array, i, j, n)
                pos += 3*n
        next_im.image.save(output_name)
        next_im.image.close()
    else:
        print("Too large incoming file")
    image.close()


def edit_last_n(color, msg, n):
    """Заменяет последние n бит в color на msg"""
    msg_len = len(msg)
    if msg_len == 0:
        return color
    bits = "{0:08b}".format(color)
    msg = ''.join(str(i) for i in msg)
    # Если кол-во бит, которые нужо зашифровать
    # меньше, чем длина по умолчанию, то пихаем их так, чтоб потом расшифровывать нормально
    if len(msg) != n:
        return int(bits[:8-n] + msg + bits[8-n+len(msg):], 2)
    return int(bits[:8-len(msg)] + msg, 2)


def get_bytes_from_file(filename, size=2048):
    """Возвращает байты из файла"""
    result = []
    with open(filename, "rb") as f:
        chunk = f.read(size)
        while chunk:
            for b in chunk:
                result.append(b)
            chunk = f.read(size)
    return result


def bytes_to_bits(bytes_iterable):
    """Переводит последовательность байт в биты"""
    result = []
    for b in bytes_iterable:
        b = "{0:08b}".format(b)
        result.append(list(map(int, b)))
    result = [val for sublist in result for val in sublist]
    return result


def bits_to_bytes(bits):
    """Переводит биты в байты"""
    result = []
    for i in range(0, len(bits) - 1, 8):
        n = int(bits[i:i+8], 2)
        result.append(bytes([n]))
    return result


def get_last_n_bits(color, n):
    """Вовзаращает последние n бит"""
    bits = "{0:08b}".format(color)
    return bits[-n:]


def get_length_from_image(image):
    """Возвращает длиу закодированного сообщение"""
    res = []
    for pos in range(1, 5):
        r, g, b = image.getpixel((pos, 0))
        end_r = get_last_n_bits(r, 2)
        end_g = get_last_n_bits(g, 3)
        end_b = get_last_n_bits(b, 3)
        res.append(int(end_r+end_g+end_b, 2))
    return res[0]*255**3 + res[1]*255**2 + res[2]*255+res[3]


def decode_bmp(image_name, n):
    """Пытается декодировать изображение по последним n битам"""
    image = Image.open(image_name)
    width = image.width
    height = image.height
    res = ""
    msg_len = get_length_from_image(image)
    wrong_bits_length = 0
    for color in image.getpixel((0, 0)):
        if get_last_n_bits(color, 3) != "111":
            print("Скорее всего в изображении нет нашего сообщения")
            print("Но мы попытаемся декодировать")
    for i in range(width):
        if len(res) >= msg_len:
            break
        for j in range(height):
            if len(res) >= msg_len:
                break
            if i >= 5 or j != 0:
                for color in image.getpixel((i, j)):
                    if len(res) >= msg_len:
                        break
                    if n > msg_len - len(res):
                        wrong_bits_length = n - (msg_len - len(res))
                    res += get_last_n_bits(color, n)
    image.close()
    if wrong_bits_length > 0:
        res = res[:-wrong_bits_length]
    result = bits_to_bytes(res)
    f = open('output.txt', 'wb')
    for byte in result:
        f.write(byte)
    f.close()

    str_res = ""
    for i in result:
        str_res += str(i)[2:-1]
    return str_res


def main():
    n = 8
    encode("test.bmp", "message.txt", "output.bmp", n)
    decode_bmp("output.bmp", n)
if __name__ == '__main__':
    main()