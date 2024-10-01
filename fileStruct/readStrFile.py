from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class ReadItemHelp():
    Nums = 679
    
    def __init__(self, input_path: str = '') -> None:
        self.string_byte = []
        self.string_str = []

        if input_path:
            self.unpackData(input_path)

    def cvtStr2Byte(self, table: convert_by_TBL):
        self.string_byte.clear()
        for data in self.string_str:
            self.string_byte.append(table.cvtStr_Bytes(data, True))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self.string_str.clear()
        for data in self.string_byte:
            self.string_str.append(table.cvtBytes_str(data))
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            len_buffer = len(buffer)
            byte_stream = io.BytesIO(buffer)
            
            ptrs = []
            for idx in range(self.Nums):
                pos = int2(byte_stream.read(2))
                ptrs.append(2*pos)
            ptrs.append(len_buffer)
            
            if (ptrs[0]//2) != self.Nums:
                logging.critical(f"check the number of texts, size different; {self.Nums} != current({ptrs[0]//2})")
                
            self.string_byte.clear()
            for idx in range(self.Nums):
                pos = ptrs[idx]
                nextpos = ptrs[idx+1]
                data = buffer[pos:nextpos]
                self.string_byte.append(data)

    def packData(self, output_path:str):
        if self.Nums != len(self.string_byte):
            logging.critical(f"check the number of texts, size different; {self.Nums} != current({len(self.string_byte)})")
        
        ptrs = [ self.Nums ]
        for idx in range(self.Nums):
            ptrs.append(ptrs[-1] + len(self.string_byte[idx])//2)

        with open(output_path, 'wb') as file:
            for idx in range(self.Nums):
                file.write(bytes2(ptrs[idx]))
                
            for idx in range(len(self.string_byte)):
                data = self.string_byte[idx]
                file.write(data)
