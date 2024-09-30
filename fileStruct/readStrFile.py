from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class ReadStrings():
    OFFSET = 0x54E
    
    def __init__(self, input_path: str = '') -> None:
        self.string_byte = []
        self.string_str = []

        if input_path:
            self.unpackData(input_path)

    def cvtName2Byte(self, table: convert_by_TBL):
        self.string_byte.clear()
        for data in self.string_str:
            byteData = table.cvtStr_Bytes(data)
            if byteData[-1] != 0xE7:
                byteData.append(0xE7)
            len_byteData = len(byteData)
            if (len_byteData%2) == 1:
                byteData.append(0xEB)
            self.string_byte.append(byteData)
    
    def cvtByte2Name(self, table: convert_by_TBL):
        self.string_str.clear()
        for data in self.string_byte:
            self.string_str.append(table.cvtBytes_str(data))
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            len_buffer = len(buffer)

            self.string_byte.clear()
            pos = self.OFFSET
            while pos < len_buffer:
                curr = pos
                while buffer[curr] != 0xE7:
                    curr += 1
                    if curr >= len_buffer: break
                
                if curr < len_buffer and buffer[curr+1] == 0xEB:
                    curr += 1
                data = buffer[pos:curr]
                self.string_byte.append(data)
                
                pos = curr + 1

    def packData(self, output_path:str):
        with open(output_path, 'wb') as file:
            for idx in range(len(self.string_byte)):
                data = self.string_byte[idx]
                file.write(data)
