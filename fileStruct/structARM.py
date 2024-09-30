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
            for idx in range(num_rooms):
                byte_stream.seek(4, os.SEEK_CUR)
                len_graphicsSection.append(int4(byte_stream.read(4)))
                byte_stream.seek(4, os.SEEK_CUR)
            
            self.ptrRoomNames = 4 + num_rooms*12 + sum(len_graphicsSection) + 4
            
            byte_stream.seek(self.ptrRoomNames)
            
            self.names_byte.clear()
            for idx in range(num_rooms):
                self.names_byte.append(byte_stream.read(0x20))
                byte_stream.seek(4, os.SEEK_CUR)

    def convertName(self, table: convert_by_TBL):
        self.names_str.clear()
        for text in self.names_byte:
            self.names_str.append(table.cvtBytes_str(text))
            
    def packData(self, output_path:str):
        if self.buffer is None:
            return

        byte_stream = io.BytesIO(self.buffer)
        num_rooms = int4(byte_stream.read(4))
        
        if num_rooms != len(self.names_byte):
            logging.critical(f"check the number of rooms, size different; roms({num_rooms}) != names({len(self.names_byte)})")

        for idx in range(num_rooms):
            len_name = len(self.names_byte[idx])
            if len_name < 0x20:
                self.names_byte[idx].extend([0]*(0x20 - len_name))
            if len_name > 0x20:
                logging.critical(f"check the room name, size overflowed({len_name} > {0x20})")
                self.names_byte[idx] = self.names_byte[idx][:0x20]

        byte_stream.seek(self.ptrRoomNames)
        for idx in range(num_rooms):
            byte_stream.write(self.names_byte[idx])
            byte_stream.seek(4, os.SEEK_CUR)
            
        with open(output_path, 'wb') as file:
            file.write(self.buffer)