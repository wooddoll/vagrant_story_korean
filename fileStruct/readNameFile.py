from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class ItemNames():
    FileName = 'MENU/ITEMNAME.BIN'
    ItemNumber = 512
    ItemBytes = 0x18
    
    def __init__(self, folder_path:str = '') -> None:
        self.name_byte = []
        self.name_str = []

        if folder_path:
            self.unpackData(str(Path(folder_path) / Path(self.FileName)))

    def cvtName2Byte(self, table: convert_by_TBL):
        self.name_byte.clear()
        for text in self.name_str:
            byteName = table.cvtStr_Bytes(text)
            if byteName[-1] != 0xE7:
                byteName.append(0xE7)
            self.name_byte.append(byteName)
    
    def cvtByte2Name(self, table: convert_by_TBL):
        self.name_str.clear()
        for text in self.name_byte:
            self.name_str.append(table.cvtBytes_str(text))
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            len_Buffer = len(buffer)
            len_items = len_Buffer // self.ItemBytes
            if len_items != self.ItemNumber:
                logging.critical("!!!")
            
            byte_stream = io.BytesIO(buffer)
            
            self.name_byte.clear()
            for idx in range(self.ItemNumber):
                bytename = byte_stream.read(self.ItemBytes)
                self.name_byte.append(bytename) 

    def packData(self, output_path:str):
        if len(self.name_byte) != self.ItemNumber:
            logging.critical("!!!")
            
        with open(output_path, 'wb') as file:
            for idx in range(self.ItemNumber):
                len_bytes = len(self.name_byte[idx])
                
                if len_bytes > self.ItemBytes:
                    bytename = self.name_byte[idx][:self.ItemBytes]
                else:
                    bytename = self.name_byte[idx]

                file.seek(idx * self.ItemBytes)
                file.write(bytename)
