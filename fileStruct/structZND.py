from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *




class ZND_MPD_data():
    def __init__(self) -> None:
        self.LBApos: int = 0        # LBA pos
        self.file_size: int = 0     # bytes !!! not lba, rounded up to multiple of 2048
        self.file_name: str = ''

class ZND_MPD():
    def __init__(self, buffer: bytes | None = None) -> None:
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
            data = ZND_MPD_data()
            data.LBApos = int4(byte_stream.read(4))
            data.file_size = int4(byte_stream.read(4))

            self.MPD.append(data)

    def packData(self, buffer: bytearray):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        if header[0] != len(self.MPD):
            logging.critical(f"check the number of MPD files, size different; privious({header[0]}) != current({len(self.MPD)})")
        self.MPD.clear()

        byte_stream.seek(header[0])
        for data in self.MPD:
            byte_stream.write(bytes4(data.LBApos))
            byte_stream.write(bytes4(data.file_size))        

class ZND_Enemy():
    def __init__(self, buffer: bytes | None = None) -> None:
        self.name_byte: List[bytearray] = []
        self.weapon_byte: List[bytearray] = []

        self.name_str: List[str] = []
        self.weapon_str: List[str] = []

        if buffer is not None:
            self.unpackData(buffer)

    def convertName(self, table: convert_by_TBL):
        self.name_str.clear()
        for text in self.name_byte:
            self.name_str.append(table.cvtBytes_str(text))
        
        self.weapon_str.clear()
        for text in self.weapon_byte:
            self.weapon_str.append(table.cvtBytes_str(text))

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

    def packData(self, buffer: bytearray):
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
            if len_name < 0x18:
                self.name_byte[idx].extend([0]*(0x18 - len_name))
            if len_name > 0x18:
                logging.critical(f"check the enemy name, size overflowed({len_name} > {0x18})")
                self.name_byte[idx] = self.name_byte[idx][:0x18]
            
            len_weapon = len(self.weapon_byte[idx])
            if len_weapon < 0x18:
                self.weapon_byte[idx].extend([0]*(0x18 - len_weapon))
            if len_weapon > 0x18:
                logging.critical(f"check the enemy weapon, size overflowed({len_weapon} > {0x18})")
                self.weapon_byte[idx] = self.weapon_byte[idx][:0x18]

        ptr_enemies = header[1] + 4 + 8*num_enemies
        byte_stream.seek(ptr_enemies)
        for idx in range(num_enemies):
            ptr_enemy_name = ptr_enemies + 0x464*idx + 4
            byte_stream.seek(ptr_enemy_name)
            byte_stream.write(self.name_byte[idx])

            ptr_weapon_name = ptr_enemies + 0x464*idx + 0x34 + 0xf4
            byte_stream.seek(ptr_weapon_name)
            byte_stream.write(self.weapon_byte[idx])

class ZNDstruct():
    def __init__(self, input_path:str = '') -> None:
        self.buffer = None

        self.MPD = ZND_MPD()
        self.Enemy = ZND_Enemy()
        if input_path:
            self.unpackData(input_path)

    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = bytearray(file.read())

            self.MPD.unpackData(self.buffer)
            self.Enemy.unpackData(self.buffer)

    def packData(self, output_path:str):
        if self.buffer is None:
            return

        self.MPD.packData(self.buffer)
        self.Enemy.packData(self.buffer)

        with open(output_path, 'wb') as file:
            file.write(self.buffer)