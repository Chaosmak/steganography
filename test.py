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
    msg_len = len(bin_msg)
    if msg_len <= n*3*width*height-5:
        new_image = Image.new('RGB', (width, height))
        # поставим в пиксель (0,0) информацию, что есть сообщение
        r, g, b = image.getpixel((0, 0))
        # пусть будем распознавать есть ли инфа по "111" в последних трех битах
        r = edit_last_n(r, [1, 1, 1], 3)
        g = edit_last_n(g, [1, 1, 1], 3)
        b = edit_last_n(b, [1, 1, 1], 3)
        new_image.putpixel((0, 0), (r, g, b))
        # Отводим 4 пикселя:(1 - 5, 0) на служебную инфу, т.е. в каком пикселе будет заканчиваться текст
        # В первом - сколько раз взять по 255
        # Во втором - сколько прибавить после этих взятий по 255
        # Так два раза, чтоб когда будем расшифровывать - узнать до какого надо расшифровывать
        service_i = service_j = 0
        for i in range(width):
            for j in range(height):
                if i < 5 and j == 0:
                    continue
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
                    service_i = i
                    service_j = j
                new_image.putpixel((i, j), (r, g, b))
        new_image = add_info(image, new_image, service_i, service_j)
        new_image.save(output_name)
        new_image.close()
    else:
        print("Too large incoming file")
    image.close()


def add_info(old_image, new_image, i, j):
    temp = ["{0:08b}".format(i // 255),
            "{0:08b}".format(i - ((i // 255) * 255)),
            "{0:08b}".format(j // 255),
            "{0:08b}".format(j - ((j // 255) * 255))]
    for pos in range(1, 5):
        pixels = old_image.getpixel((pos, 0))
        modified_pixels = edit_c(pixels, temp[pos-1])
        new_image.putpixel((pos, 0), modified_pixels)
    return new_image


def edit_c(pixel, info):
    r, g, b = pixel
    r = edit_last_n(r, info[:2], 2)
    g = edit_last_n(g, info[2:5], 3)
    b = edit_last_n(b, info[5:], 3)
    return r, g, b


def edit_last_n(color, msg, n):
    """color - int, msg - list, n - int"""
    msg_len = len(msg)
    # Если длина сообщения 0, то возвращаем неизмененный цвет
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
    result = []
    with open(filename, "rb") as f:
        chunk = f.read(size)
        while chunk:
            for b in chunk:
                result.append(b)
            chunk = f.read(size)
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


def get_stop_pixels(image):
    res = []
    for pos in range(1, 5):
        temp = ''
        r, g, b = image.getpixel((pos, 0))
        temp += get_last_n_bits_from_color(r, 2)
        temp += get_last_n_bits_from_color(g, 3)
        temp += get_last_n_bits_from_color(b, 3)
        res.append(int(temp, 2))
    return res[0]*255 + res[1], res[2]*255 + res[3]


def decode_bmp(image_name, n):
    image = Image.open(image_name)
    width = image.width
    height = image.height
    res = ""
    stop_i, stop_j = get_stop_pixels(image)
    for color in image.getpixel((0, 0)):
        temp = get_last_n_bits_from_color(color, 3)
        if temp != "111":
            print("Скорее всего в изображении нет нашего сообщения")
    stop = False
    for i in range(width):
        if stop:
            break
        for j in range(height):
            if i == stop_i and j == stop_j + 1:
                stop = True
                break
            if i >= 5 or j != 0:
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
    n = 3
    encode("test.bmp", "message.txt", "output.bmp", n)
    decode_bmp("output.bmp", n)
if __name__ == '__main__':
    main()
