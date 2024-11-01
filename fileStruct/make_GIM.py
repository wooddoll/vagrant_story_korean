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

def packImage4b(image: Image.Image):
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

class read_gimBase:
    blocks = []
    blkPoss = []
    
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytearray()
        self.Canvas = Image.Image()
        self.Image = Image.Image()
        self.startPtr = 0x0

        if input_path:
            self.unpackData(input_path)
    
    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            self.buffer = bytearray(file.read())

            len_buffer = len(self.buffer)
            len_buffer_256_15 = (len_buffer // 128) // 15
            self.startPtr = len_buffer - (len_buffer_256_15*15*128)

            image = makeImage4b_(self.buffer[self.startPtr:])
            
            cavas_w = 256*len_buffer_256_15
            self.Image = Image.new("RGBA", (cavas_w, 15), (0, 0, 0, 0))
            
            wc = 0
            hc = 0
            for rect, pos in zip(self.blocks, self.blkPoss):
                wc = max(wc, pos[0] + rect[2])
                hc = max(hc, pos[1] + rect[3])

            self.Canvas = Image.new("RGBA", (wc, hc), (0, 0, 0, 0))
            
            for i in range(len_buffer_256_15):
                blkcrop = image.crop((0, 15*i, 256, 15*i + 15))
                self.Image.paste(blkcrop, (256*i, 0)) 
            
            for rect, pos in zip(self.blocks, self.blkPoss):
                blkcrop = self.Image.crop((rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3]))
                self.Canvas.paste(blkcrop, pos) 
            
    def packData(self, output_path: str):
        if not self.buffer:
            return
        
        canvas_w = self.Image.size[0]
        canvas_w_256 = canvas_w // 256
        image = Image.new("RGBA", (256, canvas_w_256*15), (0, 0, 0, 0))
        
        for i in range(canvas_w_256):
            blkcrop = self.Image.crop((256*i, 0, 256*i+256, 15))
            image.paste(blkcrop, (0, 15*i))
        
        for rect, pos in zip(self.blocks, self.blkPoss):
            blkcrop = self.Canvas.crop((pos[0], pos[1], pos[0]+rect[2], pos[1]+rect[3]))
            self.Image.paste(blkcrop, (rect[0], rect[1])) 
            
        with open(output_path, 'wb') as file:
            file.write(self.buffer)
            file.seek(self.startPtr)
            file.write( packImage4b(image) )

    def exportBase(self, output_path: str):
        self.Image.save(output_path)
    
    def exportCanvas(self, output_path: str):
        if self.Canvas.size[0] > 0 and self.Canvas.size[1] > 0:
            self.Canvas.save(output_path)

class gimDADDY(read_gimBase):
    blocks = [(0,0,128,7), (0,8,128,7)]
    blkPoss = [(128,7), (192,0)]

class gimDEMO_001(read_gimBase):
    blocks = [(1048, 0, 192, 15), (1240, 0, 320, 15), (1560, 0, 320, 15)]
    blkPoss = [(0,0), (0,15), (0,30)]

class gimDEMO_002(read_gimBase):
    blocks = [(1280, 0, 256, 15), (1536, 0, 256, 15), (1792, 0, 320, 15), (2112, 0, 320, 15) ]
    blkPoss = [(0,0),(0,15),(0,30),(0,45)]
        
class gimDEMO_003(read_gimBase):
    blocks = [(768, 0, 320, 15), (1088, 0, 320, 15)]
    blkPoss = [(0,0),(0,15)]
        
class gimDEMO_004(read_gimBase):
    blocks = [(1024, 0, 256, 15), (1280, 0, 320, 15), (1600, 0, 320, 15)]
    blkPoss = [(0,0),(0,15),(0,30)]

class gimDEMO_005(read_gimBase):
    blocks = [(768, 0, 256, 15), (1024, 0, 320, 15), (1344, 0, 320, 15)]
    blkPoss = [(0,0),(0,15),(0,30)]
        
class gimDEMO_006(read_gimBase):
    blocks = [(1024, 0, 320, 15), (1344, 0, 320, 15), (1664, 0, 192, 15), (1856, 0, 192, 15)]
    blkPoss = [(0,0),(0,15),(0,30),(0,45)]

class gimDEMO_007(read_gimBase):
    blocks = [(768, 0, 320, 15), (1088, 0, 320, 15), (1408, 0, 320, 15)]
    blkPoss = [(0,0),(0,15),(0,30)]
        
class gimDEMO_008(read_gimBase):
    blocks = [(512, 0, 64, 15), (576, 0, 64, 15)]
    blkPoss = [(0,0),(0,15)]
        
class gimEPI_INF(read_gimBase):
    blocks = []
    blkPoss = []
    def __init__(self, input_path: str = '') -> None:
        for x in range(16):
            self.blocks.append((768+64*x, 0, 64, 15))
            self.blkPoss.append((0, 15*x))

        super().__init__(input_path)

class gimEPILOGUE(read_gimBase):
    blocks = [(1024, 0, 192, 15), (1216, 0, 192, 15)]
    blkPoss = [(0, 0), (0, 15)]

class gimJO(read_gimBase):
    blocks = []
    blkPoss = []
    def __init__(self, input_path: str = '') -> None:
        blkSizes = [128, 192, 192, 320, 128, 192, 192, 128, 320, 320]
        pos = 0
        self.blocks.clear()
        self.blkPoss.clear()
        for i, x in enumerate(blkSizes):
            self.blocks.append((pos, 0, x, 15))
            pos += x
            self.blkPoss.append((0, 15*i))

        super().__init__(input_path)

class gimN_LEA(read_gimBase):
    blocks = [(2048, 0, 320, 15), (2368, 0, 320, 15)]
    blkPoss = [(0, 0), (0, 15)]

class gimVKP_0(read_gimBase):
    blocks = [(0, 0, 300, 15), (300, 0, 210, 15), (510, 0, 220, 15), (758, 0, 192, 15), 
              (960, 0, 320, 15), (1280, 0, 320, 15), (1600, 0, 192, 15), (1792, 0, 320, 15), 
              (2112, 0, 320, 15), (2432, 0, 256, 15), (2688, 0, 320, 15), (3008, 0, 128, 15), 
              (3136, 0, 192, 15), (3328, 0, 192, 15)]
    blkPoss = [(0,0),(0,15),(18,30),(10,45),(0,60),(0,75),(0,90),(0,105),(0,120),(0,135),(0,150),(0,165),(0,180),(0,195)]
    
class gimVKP_1(read_gimBase):
    blocks = [(0, 0, 192, 15), (192, 0, 192, 15), (384, 0, 192, 15), (576, 0, 192, 15), (768, 0, 320, 15),
              (1088, 0, 256, 15), (1344, 0, 320, 15), (1664, 0, 320, 15), (1984, 0, 256, 15)]
    blkPoss = [(0,0),(0,15),(0,30),(0,45),(0,60),(0,75),(0,90),(0,105),(0,120)]
    
class gimVKP_2(read_gimBase):
    blocks = [(0, 0, 320, 15), (320, 0, 192, 15), (512, 0, 192, 15), (704, 0, 320, 15), (1024, 0, 320, 15),
              (1344, 0, 320, 15), (1664, 0, 320, 15), (1984, 0, 320, 15), (2304, 0, 192, 15), (2496, 0, 320, 15),
              (2816, 0, 320, 15), (3136, 0, 256, 15)]
    blkPoss = [(0,0),(0,15),(0,30),(0,45),(0,60),(0,75),(0,90),(0,105),(0,120),(0,135),(0,150),(0,165)]

class read_GIM:
    def __init__(self, input_path: str = '') -> None:
        self.GIMs = {}
        
        if input_path:
            self.unpack(input_path)
            
    def unpack(self, input_path: str):
        folder_path = Path(input_path) / Path('GIM')
        file_list = [file for file in folder_path.rglob('*.GIM') if file.is_file()]
        file_list = sorted(file_list)
        for filepath in file_list:
            class_name = f"gim{filepath.stem}"
            if class_name in globals():
                cls = globals()[class_name]
                self.GIMs.update({ filepath.stem: cls(str(filepath)) })
    
    def pack(self, output_path: str):
        folder_path = Path(output_path) / Path('GIM')
        for k, v in self.GIMs.items():
            outpath = folder_path / Path(f"{k}.GIM")
            v.packData(str(outpath))
        
    def debug(self):
        for k, v in self.GIMs.items():
            v.exportBase(f"work/test/{k}.base.png")
            v.packData(f'work/test/{k}.GIM')
            v.exportBase(f"work/test/{k}.recover.png")
            v.exportCanvas(f"work/test/{k}.canvas.png")

gims = read_GIM('/home/wooddoll/Workspace/personal/Vagrant Story (J)')
gims.debug()