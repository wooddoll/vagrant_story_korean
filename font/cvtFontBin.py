from PIL import Image
import os


def readFile2b(image_file, width: int):
    width_byte = width//4
    image_file.seek(0, os.SEEK_END)
    size = image_file.tell()
    height = size // width_byte

    image_file.seek(0, os.SEEK_SET)
    buffer = []

    for y in range(height):
        for x in range(width_byte):
            next_byte = int.from_bytes(image_file.read(1), "little")
            
            v1 = next_byte&0b11
            v2 = (next_byte&0b1100)>>2
            v3 = (next_byte&0b110000)>>4
            v4 = (next_byte&0b11000000)>>6

            buffer.append(v1)
            buffer.append(v2)
            buffer.append(v3)
            buffer.append(v4)
    
    return buffer

def makeImage2b(buffer, height: int, width: int):
    clut2b = [(0, 0, 0, 0), ]
    for i in range(3):
        c = 255 - 127*i
        clut2b.append( (c, c, c, 255) )

    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    width_half = width//2
    font_cols = width//14

    line0 = [0]*128
    line1 = [0]*128
    line = [0]*256
    for y in range(height):
        for x in range(width_half):
            v1 = buffer[y*width + 2*x]
            v2 = buffer[y*width + 2*x+1]
            line0[x] = v1
            line1[x] = v2
        for i in range(font_cols//2):
            for k in range(14):
                line[i*28+k] = line0[i*14+k]
                line[i*28+k+14] = line1[i*14+k]

        for x in range(width):
            pixel =  clut2b[line[x]]
            im.putpixel((x,y), pixel)
    
    return im

def unpackFont14Bin(input_path: str, output_path: str = ''):
    image_file = open(input_path, "rb")
    
    width = 256
    width_byte = width//4

    image_file.seek(0, os.SEEK_END)
    size = image_file.tell()
    height = size // width_byte

    image_file.seek(0, os.SEEK_SET)

    buffer = readFile2b(image_file, width)
    im = makeImage2b(buffer, height, width)
    
    if output_path:
        im.save(output_path)
    
    return im

def packFont14Bin(input_path: str, output_path: str):
    im = Image.open(input_path)

    if im.width != 256 or im.mode != 'RGBA':
        raise ValueError("Image size or format mis match")
    
    width = 256
    width_byte = width//4
    width_half = width//2
    font_cols = width//14
    height = im.height

    bin_file = open(output_path, "wb")

    buffer = [0]*width_byte
    line0 = [0]*128
    line1 = [0]*128
    line = [0]*256
    for y in range(height):
        for i in range(font_cols//2):
            for k in range(14):
                v = 0
                _v = im.getpixel((i*28+k, y))
                if _v[3] == 0:
                    v = 0
                else:
                    v = 3 - round((_v[0]+_v[1]+_v[2])/382)
                line0[i*14+k] = v

                _v = im.getpixel((i*28+k+14, y))
                if _v[3] == 0:
                    v = 0
                else:
                    v = 3 - round((_v[0]+_v[1]+_v[2])/382)
                line1[i*14+k] = v

        for x in range(width_half):
            line[2*x] = line0[x]
            line[2*x+1] = line1[x]

        for i in range(width_byte):
            v1 = line[4*i]
            v2 = line[4*i+1]
            v3 = line[4*i+2]
            v4 = line[4*i+3]
            cur_byte = (v1&0b11) | ((v2&0b11) << 2) | ((v3&0b11) << 4) | ((v4&0b11) << 6)
            buffer[i] = cur_byte

        bin_file.write(bytes(buffer))


PATHBASE_TEST = "C:/TEMP/Vagrant Story (J)/"

def testFont14Bin():
    #unpackFont14Bin(PATHBASE_TEST+"MENU/FONT14.BIN", "font14_2b_256.png")
    packFont14Bin("font14_2b_256.png", "_font14.bin")
    unpackFont14Bin("_font14.bin", "_font14_2b_256.png")
testFont14Bin()