from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *




class ZND_MPD_data:
    def __init__(self, LBApos = 0, File_size = 0, File_name = '') -> None:
        self.LBApos: int = LBApos        # LBA pos
        self.File_size: int = File_size     # bytes !!! not lba, rounded up to multiple of 2048
        self.File_name: str = File_name

class ZND_MPD:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.MPD: List[ZND_MPD_data] = []

        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)

        self.MPD.clear()

        numMPD = header[1] // 8
        byte_stream.seek(header[0])
        for _ in range(numMPD):
            LBApos = int4(byte_stream.read(4))
            File_size = int4(byte_stream.read(4))
            self.MPD.append(ZND_MPD_data(LBApos, File_size))

    def packData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        if (header[1]//8) != len(self.MPD):
            logging.critical(f"check the number of MPD files, size different; privious({header[0]}) != current({len(self.MPD)})")
        self.MPD.clear()

        byte_stream.seek(header[0])
        for data in self.MPD:
            byte_stream.write(bytes4(data.LBApos))
            byte_stream.write(bytes4(data.File_size))
        
        return byte_stream.getvalue()

class ZND_Enemy:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.name_byte: List[bytearray] = []
        self.weapon_byte: List[bytearray] = []

        self.name_str: List[str] = []
        self.weapon_str: List[str] = []

        if buffer is not None:
            self.unpackData(buffer)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.name_str.clear()
        for text in self.name_byte:
            self.name_str.append(table.cvtByte2Str(text))
        
        self.weapon_str.clear()
        for text in self.weapon_byte:
            self.weapon_str.append(table.cvtByte2Str(text))
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.name_byte.clear()
        for text in self.name_str:
            self.name_byte.append(table.cvtStr2Byte(text))
        
        self.weapon_byte.clear()
        for text in self.weapon_str:
            self.weapon_byte.append(table.cvtStr2Byte(text))

    def unpackData(self, buffer: bytes):
        if buffer is None:
            return

        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)

        self.name_byte.clear()
        self.weapon_byte.clear()

        byte_stream.seek(header[2])
        num_enemies = int4(byte_stream.read(4))

        ptr_enemies = header[2] + 4 + 8*num_enemies
        byte_stream.seek(ptr_enemies)
        for idx in range(num_enemies):
            ptr_enemy_name = ptr_enemies + 0x464*idx + 4
            byte_stream.seek(ptr_enemy_name)
            byte_name = byte_stream.read(0x18)
            self.name_byte.append(bytearray(byte_name))
            
            ptr_weapon_name = ptr_enemies + 0x464*idx + 0x34 + 0xf4
            byte_stream.seek(ptr_weapon_name)
            byte_weapon = byte_stream.read(0x18)
            self.weapon_byte.append(bytearray(byte_weapon))

    def packData(self, buffer: bytes):
        if buffer is None:
            return
    
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)

        byte_stream.seek(header[2])
        num_enemies = int4(byte_stream.read(4))

        if num_enemies != len(self.name_byte) or num_enemies != len(self.weapon_byte):
            logging.critical(f"check the number of enemies files, size different; privious({num_enemies}) != current({len(self.name_byte)}, {len(self.weapon_byte)})")

        for idx in range(num_enemies):
            len_name = len(self.name_byte[idx])
            if len_name > 0x18:
                logging.critical(f"check the enemy name, size overflowed({0x18} < {len_name})")
                self.name_byte[idx] = self.name_byte[idx][:0x18]
            elif len_name < 0x18:
                self.name_byte[idx].extend(bytearray(0x18-len_name))
                
            len_weapon = len(self.weapon_byte[idx])
            if len_weapon > 0x18:
                logging.critical(f"check the enemy weapon, size overflowed({0x18}) < {len_weapon}")
                self.weapon_byte[idx] = self.weapon_byte[idx][:0x18]
            elif len_weapon < 0x18:
                self.weapon_byte[idx].extend(bytearray(0x18-len_weapon))

        ptr_enemies = header[2] + 4 + 8*num_enemies
        byte_stream.seek(ptr_enemies)
        for idx in range(num_enemies):
            ptr_enemy_name = ptr_enemies + 0x464*idx + 4
            byte_stream.seek(ptr_enemy_name)
            byte_stream.write(self.name_byte[idx])

            ptr_weapon_name = ptr_enemies + 0x464*idx + 0x34 + 0xf4
            byte_stream.seek(ptr_weapon_name)
            byte_stream.write(self.weapon_byte[idx])

        return byte_stream.getvalue()
        
class psxTIM:
    def __init__(self, buffer: bytes = bytes()):
        self.buffer = buffer
        byte_stream = io.BytesIO(self.buffer)
        
        Magic = int1(byte_stream.read(4))  # 16
        self.BPP = int1(byte_stream.read(4))
        DataLen = int4(byte_stream.read(4))
        self.Image_length = DataLen - 12
        self.Image_x = int2(byte_stream.read(2))
        self.Image_y = int2(byte_stream.read(2))
        self.Image_width = int2(byte_stream.read(2))
        self.Image_height = int2(byte_stream.read(2))
        self.Image_data = byte_stream.read(self.Image_length)
        
        #print(f"{self.Image_width}x{self.Image_height}, {2*self.Image_width*self.Image_height == self.Image_length}")
            
        
class ZND_TIM:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.TIM: List[psxTIM] = []
        self.header: List[int] = []
        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        
        TIM_ptr = header[4]
        TIM_size = header[5]
        byte_stream.seek(TIM_ptr)
        
        header = readHeader(byte_stream, 5, 4)
        numTIM = header[4]
        self.TIM.clear()        
        for idx in range(numTIM):
            TIM_size = int4(byte_stream.read(4))
            TIM_data = byte_stream.read(TIM_size)
            self.TIM.append(psxTIM(TIM_data))
        
        #for idx in range(numTIM):
        #    with open(f'work/test/{idx:03}.TIM', 'wb') as f:
        #        f.write(self.TIM[idx].buffer)
        #print()

    def packData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        if (header[1]//8) != len(self.TIM):
            logging.critical(f"check the number of MPD files, size different; privious({header[0]}) != current({len(self.TIM)})")
        self.TIM.clear()

        byte_stream.seek(header[0])
        for data in self.TIM:
            byte_stream.write(bytes4(data.File_size))   

class ZNDstruct:
    def __init__(self, input_path:str = '') -> None:
        self.buffer = None

        self.MPD = ZND_MPD()
        self.Enemy = ZND_Enemy()
        self.TIM = ZND_TIM()
        
        if input_path:
            self.unpackData(input_path)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.Enemy.cvtByte2Str(table)
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.Enemy.cvtStr2Byte(table)
    
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = file.read()

            self.MPD.unpackData(self.buffer)
            self.Enemy.unpackData(self.buffer)
            self.TIM.unpackData(self.buffer)

    def packData(self, output_path:str):
        if self.buffer is None:
            return

        self.buffer = self.MPD.packData(self.buffer)
        self.buffer = self.Enemy.packData(self.buffer)

        with open(output_path, 'wb') as file:
            file.write(self.buffer)