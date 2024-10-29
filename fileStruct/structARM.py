from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *


class ARMstruct():
    def __init__(self, input_path:str = '') -> None:
        self.buffer = None

        self.ptrRoomNames: int = 0
        self.names_str: List[str] = []
        self.names_byte: List[bytearray] = []
        
        if input_path:
            self.unpackData(input_path)

    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = bytearray(file.read())
            byte_stream = io.BytesIO(self.buffer)
            
            num_rooms = int4(byte_stream.read(4))
            len_graphicsSection = []
            for _ in range(num_rooms):
                byte_stream.seek(4, os.SEEK_CUR)
                len_graphicsSection.append(int4(byte_stream.read(4)))
                byte_stream.seek(4, os.SEEK_CUR)
            
            self.ptrRoomNames = 4 + num_rooms*12 + sum(len_graphicsSection) + 4
            
            self.names_byte.clear()
            for idx in range(num_rooms):
                byte_stream.seek(self.ptrRoomNames + 0x24*idx)
                self.names_byte.append(bytearray( byte_stream.read(0x1c) ))

    def cvtByte2Str(self, table: convert_by_TBL):
        self.names_str.clear()
        for text in self.names_byte:
            self.names_str.append(table.cvtByte2Str(text))
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.names_byte.clear()
        for text in self.names_str:
            self.names_byte.append(table.cvtStr2Byte(text))
            
    def packData(self, output_path:str):
        if self.buffer is None:
            return

        byte_stream = io.BytesIO(self.buffer)
        num_rooms = int4(byte_stream.read(4))
        
        if num_rooms != len(self.names_byte):
            logging.critical(f"check the number of rooms, size different; roms({num_rooms}) != names({len(self.names_byte)})")

        for idx in range(num_rooms):
            len_name = len(self.names_byte[idx])
            if 0x1c < len_name:
                logging.critical(f"check the room {idx} name, size overflowed({0x1c} < {len_name})")
                self.names_byte[idx] = self.names_byte[idx][:0x1b]
                self.names_byte[idx].append(0xe7)
            elif len_name < 0x1c:
                self.names_byte[idx].extend(bytearray(0x1c-len_name))
    
        with open(output_path, 'wb') as file:
            file.write(self.buffer)

            file.seek(self.ptrRoomNames)
            for idx in range(num_rooms):
                file.seek(self.ptrRoomNames + idx*0x24)
                file.write(self.names_byte[idx])