from typing import Union, List
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import logging
from pathlib import Path
import os
import io

def makeCLUT4b():
    clut4b = [(0, 0, 0, 0), ]
    for i in range(16):
        c = max(255 - 16*i, 0)
        clut4b.append( (c, c, c, 255) )
    return clut4b
clut4b = makeCLUT4b()

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



class read_gimBase:
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytearray()
        self.Canvas = Image.new("RGBA", (256, 512), (0, 0, 0, 0))
        self.Image = None
        
        if input_path:
            self.unpackData(input_path)
    
    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            self.buffer = bytearray(file.read())

    def packData(self, output_path: str):
        with open(output_path, 'wb') as file:
            file.write(self.buffer)

    def exportBase(self, output_path: str):
        self.Image.save(output_path)
    
    def exportCanvas(self, output_path: str):
        self.Canvas.save(output_path)

class gimDADDY(read_gimBase):
    def unpackData(self, input_path: str):
        super().unpackData(input_path)
        # here
        self.Image = makeImage4b_(self.buffer[0x180:])
        
        blk1 = self.Image.crop((0, 7, 64, 14))
        self.Canvas.paste(blk1, (0, 0))
        blk2 = self.Image.crop((64, 0, 127, 7))
        self.Canvas.paste(blk1, (0, 7))

    def packData(self, output_path: str):
        # here
        super().packData(output_path)

class gimDEMO_001(read_gimBase):
    def unpackData(self, input_path: str):
        super().unpackData(input_path)
        # here
        self.Image = makeImage4b_(self.buffer[0x190:])

    def packData(self, output_path: str):
        # here
        super().packData(output_path)


class read_GIM:
    def __init__(self, input_path: str) -> None:
        folder_path = Path(input_path) / Path('GIM')
        file_list = [file for file in folder_path.rglob('*.GIM') if file.is_file()]
        file_list = sorted(file_list)
        
        self.GIMs = {}
        
        for filepath in file_list:
            class_name = f"gim{filepath.stem}"
            if class_name in globals():
                cls = globals()[class_name]
                self.GIMs.update({ filepath.stem: cls(str(filepath)) })

        for k, v in self.GIMs.items():
            v.exportBase(f"work/test/{k}.base.png")
            v.exportCanvas(f"work/test/{k}.canvas.png")

read_GIM('/home/wooddoll/Workspace/personal/Vagrant Story (J)')