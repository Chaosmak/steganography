#!/usr/bin/env python3
from PIL import Image
import sys


def encode(image_name, input_name, output_name, n):
    """
    Засовывает в картинку image_name файл по битам из input_name
    Сохраняет в картинку под именем output_name
    n - сколько бит с конца заменять у каждого цвета в пиксиле
    """
    image = Image.open(image_name).convert('RGB')
    width = image.width
    height = image.height
    byte_file = get_bytes_from_file(input_name)
    bin_msg = bytes_to_bits(byte_file)
    pos = 0
    if len(bin_msg) <= n*3*width*height-1:
        new_image = Image.new('RGB', (width, height))
        # поставим в пиксель (0,0) информацию, что есть сообщение
        for i in range(width):
            for j in range(height):
                #if i != 0 and j != 0:
                r, g, b = image.getpixel((i, j))
                try:
                    bin_msg_array = bin_msg[pos:pos+n*3]
                except IndexError:
                    bin_msg_array = bin_msg[pos:]
                if pos < len(bin_msg):
                    r = edit_last_n(r, bin_msg_array[0:n], n)
                    g = edit_last_n(g, bin_msg_array[n:2*n], n)
                    b = edit_last_n(b, bin_msg_array[2*n:3*n], n)
                    pos += 3*n
                new_image.putpixel((i, j), (r, g, b))
        new_image.save(output_name)
        new_image.close()
    else:
        print("Too large incoming file")
    image.close()


def edit_last_n(color, paste, n=1):
    b = "{0:08b}".format(color)
    i = 0
    for num in paste:
        #bit = int(paste[i])
        if num == 0:
            b = b[:8-n + i] + "0" + b[8-n +i+ 1:]
        else:
            b = b[:8-n + i] + "1" + b[8-n +i+ 1:]
        i += 1
    print("b", b)
    b = int(b, 2)
    print(b)
    return b


def get_bytes_from_file(filename, size=2048):
    result = []
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(size)
            if chunk:
                for b in chunk:
                    result.append(b)
            else:
                break
    return result


def bytes_to_bits(bytes_iterable):
    result = []
    for b in bytes_iterable:
        b = "{0:08b}".format(b)
        result.append(list(map(int, b)))
    result = [val for sublist in result for val in sublist]
    return result


def bits_to_bytes(bits_string):
    result = []
    for i in range(0, len(bits_string) - 1, 8):
        n = int(bits_string[i:i+8], 2)
        result.append(bytes([n]))
    return result


def get_last_n_bits_from_color(color, n):
    bits = "{0:08b}".format(color)
    return bits[-n:]


def decode_bmp(image_name, n):
    image = Image.open(image_name)
    width = image.width
    height = image.height
    res = ""
    for i in range(width):
        for j in range(height):
            for color in image.getpixel((i, j)):
                # Добавляем последние n бит из цветов картинки в результат
                res += get_last_n_bits_from_color(color, n)
    image.close()
    result = bits_to_bytes(res)
    f = open('output.txt', 'wb')
    for byte in result:
        f.write(byte)
    f.close()


def main():
    encode("test.bmp", "message.txt", "output.bmp", 8)
    decode_bmp("output.bmp", 8)
if __name__ == '__main__':
    main()
