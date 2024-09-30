from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *


class Mainstruct():
    ptrSkillNames: int = 0x3C1DC
    
    def __init__(self, input_path:str = '') -> None:
        self.buffer = None

        self.names_str: List[str] = []
        self.names_byte: List[bytearray] = []
        
        if input_path:
            self.unpackData(input_path)

    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = bytearray(file.read())
            byte_stream = io.BytesIO(self.buffer)
            
            self.names_byte.clear()
            
            byte_stream.seek(self.ptrSkillNames)
            for idx in range(256):
                byte_stream.seek(0x1C, os.SEEK_CUR)
                self.names_byte.append(byte_stream.read(0x18))

    def convertName(self, table: convert_by_TBL):
        self.names_str.clear()
        for text in self.names_byte:
            self.names_str.append(table.cvtBytes_str(text))
            
    def packData(self, output_path:str):
        if self.buffer is None:
            return

        byte_stream = io.BytesIO(self.buffer)
        
        if 256 != len(self.names_byte):
            logging.critical(f"check the number of skills, size different; 256 != names({len(self.names_byte)})")

        for idx in range(256):
            len_name = len(self.names_byte[idx])
            if len_name < 0x18:
                self.names_byte[idx].extend([0]*(0x18 - len_name))
            if len_name > 0x18:
                logging.critical(f"check the room name, size overflowed({len_name} > {0x18})")
                self.names_byte[idx] = self.names_byte[idx][:0x18]

        byte_stream.seek(self.ptrSkillNames)
        for idx in range(256):
            byte_stream.seek(0x1C, os.SEEK_CUR)
            byte_stream.write(self.names_byte[idx])
            
        with open(output_path, 'wb') as file:
            file.write(self.buffer)
