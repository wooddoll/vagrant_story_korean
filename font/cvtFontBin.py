from typing import Union, List
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import logging
from pathlib import Path
import os
import io
from utils import *

def makeCLUT2b():
    clut2b = [(0, 0, 0, 0), ]
    for i in range(3):
        c = 255 - 127*i
        clut2b.append( (c, c, c, 255) )
    return clut2b
clut2b = makeCLUT2b()

def makeCLUT4b():
    clut4b = [(0, 0, 0, 0), ]
    for i in range(16):
        c = max(255 - 16*i, 0)
        clut4b.append( (c, c, c, 255) )
    return clut4b
clut4b = makeCLUT4b()

def readFont2b(font_data: bytes):
    width = 256
    width_byte = width//4

    byte_stream = io.BytesIO(font_data)
    size = len(font_data)
    height = size // width_byte

    buffer = bytearray()

    for y in range(height):
        for x in range(width_byte):
            next_byte = int.from_bytes(byte_stream.read(1), "little")
            
            v1 = next_byte&0b11
            v2 = (next_byte&0b1100)>>2
            v3 = (next_byte&0b110000)>>4
            v4 = (next_byte&0b11000000)>>6

            buffer.append(v1)
            buffer.append(v2)
            buffer.append(v3)
            buffer.append(v4)
    
    return buffer

def readFont4b(font_data: bytes):
    byte_stream = io.BytesIO(font_data)
    size = len(font_data)

    buffer = bytearray()
    for _ in range(size):
        next_byte = int.from_bytes(byte_stream.read(1), "little")
        
        v1 = next_byte&0b1111
        v2 = (next_byte&0b11110000)>>4
        buffer.append(v1)
        buffer.append(v2)
    
    return buffer


def readFile2b(image_file, width: int):
    return readFont2b(image_file.read())


def makeImage2b(buffer: bytearray, height: int, width: int):
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

def makeImage2b_(font_data: bytearray, width: int = 256):
    buffer = readFont2b(font_data)
    height = len(buffer) // width
    
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


def makeImage4b(buffer: bytearray, height: int, width: int):
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            v = buffer[y*width + x]
            pixel =  clut4b[v]
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




def makeImage4b_(font_data: bytearray, width: int = 256):
    buffer = readFont4b(font_data)
    height = len(buffer) // width
    
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            v = buffer[y*width + x]
            pixel =  clut4b[v]
            im.putpixel((x,y), pixel)
    
    return im

def makeImage2b__(buffer: bytearray, width: int = 256):
    height = len(buffer) // width
    
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            v = buffer[y*width + x]
            pixel = clut2b[v]
            im.putpixel((x,y), pixel)
    
    return im


def unpackSYSTEM_DAT(input_path: str, output_path: str = ''):
    image_file = open(input_path, "rb")
    system_dat = image_file.read()
    width = 256
    width_byte = width//2
    
    ptrA = 40
    ptrA_ = ptrA + 128*224
    im = makeImage4b_(system_dat[ptrA:ptrA_])
    im.save(f"work/system_dat_unpack_A.png")
    
    ptrB = 48 + 128*224
    ptrB_ = ptrB + 128*240
    im = makeImage4b_(system_dat[ptrB:ptrB_])
    im.save(f"work/system_dat_unpack_B.png")
    
    return

    ptrC = 112 + 128*852
    ptrC_ = ptrC + 128*220
    buffer = readFont4b(system_dat[ptrC:ptrC_])
    buffer2 = []
    for v in buffer:
        buffer2.append(v & 0b00000011)
    for v in buffer:
        buffer2.append((v & 0b00001100) >> 2)
    im = makeImage2b__(buffer2)
    im.save(f"work/system_dat_unpack_C.png")
    
    ptrD = 112 + 128*1076
    ptrD_ = ptrD + 128*220
    buffer = readFont4b(system_dat[ptrD:ptrD_])
    buffer2 = []
    for v in buffer:
        buffer2.append(v & 0b00000011)
    for v in buffer:
        buffer2.append((v & 0b00001100) >> 2)
    im = makeImage2b__(buffer2)
    im.save(f"work/system_dat_unpack_D.png")
    
    ptrE = 112 + 128*1300
    ptrE_ = ptrE + 128*110
    buffer = readFont4b(system_dat[ptrE:ptrE_])
    buffer2 = []
    for v in buffer:
        buffer2.append(v & 0b00000011)
    for v in buffer:
        buffer2.append((v & 0b00001100) >> 2)
    im = makeImage2b__(buffer2)
    im.save(f"work/system_dat_unpack_E.png")
    
    ptrF = 112 + 128*1410
    ptrF_ = ptrF + 128*44
    im = makeImage4b_(system_dat[ptrF:ptrF_])
    im.save(f"work/system_dat_unpack_F.png")
    
    #if output_path:
    #    im.save(output_path)
    return im
#unpackSYSTEM_DAT('C:/TEMP/Vagrant Story (USA)/BATTLE/SYSTEM.DAT', 'work/system_dat_unpack.png')

def unpackTITLE_PRG(input_path: str):
    image_file = open(input_path, "rb")
    system_dat = image_file.read()
    width = 256
    width_byte = width//2

    ptrA = 0x44d08
    ptrA_ = ptrA + 128*224
    
    buffer4b = readFont4b(system_dat[ptrA:])
    buffer2b = []
    for v in buffer4b:
        buffer2b.append(v & 0b00000011)
    for v in buffer4b:
        buffer2b.append((v & 0b00001100) >> 2)
    imA = makeImage2b__(buffer2b)
    imA.save(f"work/title_prg_unpack_A.png")
    
    imB = makeImage4b_(system_dat[ptrA:])
    imB.save(f"work/title_prg_unpack_B.png")
    
    imC = makeImage2b_(system_dat[ptrA:])
    imC.save(f"work/title_prg_unpack_C.png")


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
#testFont14Bin()

def packImage2b(image: Image):
    width, height = image.size
    
    buffer2b = []
    for y in range(height):
        for x in range(width):
            pxl = image.getpixel((x, y))
            
            if 0 == pxl[3]:
                buffer2b.append(0)
            elif 192 < pxl[1]:
                buffer2b.append(1)
            elif 64 < pxl[1]:
                buffer2b.append(2)
            else:
                buffer2b.append(3)
    
    height_half = height // 2
    size_half = width * height_half
    buffer4b = []
    for idx in range(size_half):
        buffer4b.append( buffer2b[idx] | (buffer2b[size_half + idx] << 2) )

    buffer8b = []
    for idx in range(0, size_half, 2):
        buffer8b.append( buffer4b[idx] | (buffer4b[idx+1] << 4) )

    return bytes(buffer8b)

class FontImage2b:
    ptr = [0, 128*224, 128*448, 128*558]
    size = [128*220, 128*220, 128*110, 128*44]
    
    def __init__(self, buffer: Union[bytes, None] = None):
        self.buffer = bytearray()
        self.buffers: List[bytes] = []
        self.images = []
        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        self.buffer = bytearray(buffer)
        
        self.buffers.clear()
        for idx in range(4):
            self.buffers.append(buffer[self.ptr[idx] : self.ptr[idx] + self.size[idx]])

        self.images.clear()
        for idx in range(3):
            buffer4b = readFont4b(self.buffers[idx])
            buffer2b = []
            for v in buffer4b:
                buffer2b.append(v & 0b00000011)
            for v in buffer4b:
                buffer2b.append((v & 0b00001100) >> 2)
            self.images.append( makeImage2b__(buffer2b) )
    
        #self.images.append( makeImage4b_(self.buffers[3]) )
    
        #for idx in range(4):
        #    self.images[idx].save(f"work/system_dat_font_{idx}.png")
    
    def getImage(self):
        width = 256
        sumHeight = 0
        for img in self.images:
            width, height = img.size
            sumHeight += height
        
        sumImg = Image.new('RGBA', (width, sumHeight), (0, 0, 0, 0))
        y = 0
        for img in self.images:
            sumImg.paste(img, (0, y))
            
            width, height = img.size
            y += height
        
        return sumImg
    
    def setImage(self, sumImg: Image):
        width, height = sumImg.size
        
        y = 0
        for img in self.images:
            width, height = img.size
            
            subImg = sumImg.crop((0, y, width, y + height))
            img.paste(subImg, (0, 0))
            
            y += height
        
    def packData(self):
        for idx in range(3):
            self.buffers[idx] = packImage2b( self.images[idx] )
        
        byte_stream = io.BytesIO(self.buffer)
        for idx in range(4):
            byte_stream.seek(self.ptr[idx])
            byte_stream.write(self.buffers[idx])
        
        return byte_stream.getvalue()


def insertTITLE_font(input_path: str, insert_image: str, output_path: str):
    with open(input_path, "rb") as file:
        title_prg = file.read()

        ptrA = 0x44cc8
        fontImg = FontImage2b(title_prg[ptrA:])
        imgJpKr = Image.open(insert_image)
        fontImg.setImage(imgJpKr)

        buffer = fontImg.packData()
        
    with open(output_path, "wb") as file:
        file.seek(ptrA)
        file.write(buffer)
    
    
#testTITLE_font('C:/TEMP/Vagrant Story (J)/TITLE/TITLE.PRG', 'font/font12kr.png', 'C:/TEMP/Vagrant Story (Kor)/TITLE/TITLE.PRG')
#exit()


def packImage4b(image: Image):
    width, height = image.size
    
    buffer4b = []
    for y in range(height):
        for x in range(width):
            pxl = image.getpixel((x, y))
            
            if 0 == pxl[3]:
                buffer4b.append(0)
            else:
                b4 = 16 - (pxl[1] // 16)
                if b4 < 0 or 15 < b4:
                    print(b4)
                buffer4b.append(b4)
    
    size_buffer4b = len(buffer4b)
    buffer8b = []
    for idx in range(0, size_buffer4b, 2):
        buffer8b.append( buffer4b[idx] | (buffer4b[idx+1] << 4) )

    return bytes(buffer8b)

class Texture4b:
    def __init__(self, buffer: Union[bytes, None] = None):
        self.buffer = bytearray()
        self.image = None
        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        self.buffer = bytearray(buffer)
        self.image = makeImage4b_(self.buffer[8:])
        #self.image.save('work/texture/test0.png')

    def setImage(self, newImg: Image):
        width, height = newImg.size
        assert width == self.image.size[0]
        self.image.paste(newImg, (0, 0))
        #self.image.save('work/texture/test1.png')
        
    def packData(self):
        byte_stream = io.BytesIO(self.buffer)
        byte_stream.seek(8)
        byte_stream.write( packImage4b(self.image) )
        
        self.buffer = byte_stream.getvalue()
        #image = makeImage4b_(self.buffer[8:])
        #image.save('work/texture/test2.png')
        
        return self.buffer

class SYSTEM_DAT:
    def __init__(self, input_path: str):
        
        self.data: List[bytes] = []
        self.fontData = FontImage2b()
        self.texture_ui = Texture4b()
        
        if os.path.isfile(input_path):
            self.unpackData(input_path)
        elif os.path.isdir(input_path):
            filepath = Path(input_path) / Path('BATTLE/SYSTEM.DAT')
            if os.path.isfile(str(filepath)):
                self.unpackData(str(filepath))
            else:
                logging.warning(f'{input_path} is not valid path.')
        else:
            logging.warning(f'{input_path} is not valid path.')
    
    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            buffer = file.read()
            byte_stream = io.BytesIO(buffer)
            
            itemNums = int2(byte_stream.read(4)) // 4
            byte_stream.seek(0)
            
            ptrs = []
            for idx in range(itemNums):
                pos = int4(byte_stream.read(4))
                ptrs.append(pos)
            ptrs.append(len(buffer))

            for idx in range(itemNums):
                self.data.append(buffer[ptrs[idx]:ptrs[idx+1]])

            self.texture_ui.unpackData( self.data[1] )
            self.fontData.unpackData( self.data[7] )
            
    def packData(self, output_path: str):
        self.data[1] = self.texture_ui.packData()
        self.data[7] = self.fontData.packData()
        
        bufpos = [ len(self.data) * 4 ]
        for data in self.data:
            size = len(data)
            bufpos.append( bufpos[-1] + size )
        
        len_data = len(self.data)
        with open(output_path, 'wb') as file:
            for idx in range(len_data):
                file.write( bytes4(bufpos[idx]) )
            
            for data in self.data:
                file.write( data )