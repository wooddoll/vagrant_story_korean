from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class MonStructure():
    FileName = 'SMALL/MON.BIN'
    ItemNumber = 150
    ItemBytes = 0x2C
    StringPtr = ItemBytes*ItemNumber
    
    def __init__(self, folder_path:str = '') -> None:
        self.name_byte = []
        self.name_str = []
        self.data_byte = []
        
        self.string_byte = []
        self.string_str = []
        
        if folder_path:
            self.unpackData(str(Path(folder_path) / Path(self.FileName)))

    def cvtName2Byte(self, table: convert_by_TBL):
        self.name_byte.clear()
        for text in self.name_str:
            self.name_byte.append(table.cvtStr_Bytes(text))
        
        self.string_byte.clear()
        for text in self.string_str:
            self.string_byte.append(table.cvtStr_Bytes(text))

    def cvtByte2Name(self, table: convert_by_TBL):
        self.name_str.clear()
        for text in self.name_byte:
            self.name_str.append(table.cvtBytes_str(text))
        
        self.string_str.clear()
        for text in self.string_byte:
            self.string_str.append(table.cvtBytes_str(text))
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            len_buffer = len(buffer)
            byte_stream = io.BytesIO(buffer)
            
            self.data_byte.clear()
            self.name_byte.clear()
            for idx in range(self.ItemNumber):
                bytedata = byte_stream.read(self.ItemBytes)
                self.data_byte.append(bytedata[:0x12])
                self.name_byte.append(bytedata[0x12:])

            byte_stream.seek(self.StringPtr)
            ptrs = []
            for idx in range(self.ItemNumber):
                pos = int2(byte_stream.read(2))
                ptrs.append(self.StringPtr + 2*pos)
            ptrs.append(len_buffer)

            self.string_byte.clear()
            for idx in range(self.ItemNumber):
                pos = ptrs[idx]
                nextpos = ptrs[idx+1]
                data = buffer[pos:nextpos]
                self.string_byte.append(data)
                
    def packData(self, output_path:str):
        if len(self.name_byte) != self.ItemNumber:
            logging.critical("!!!")
        if len(self.string_byte) != self.ItemNumber:
            logging.critical("!!!")
        
        len_byteName = self.ItemBytes - 0x12
        with open(output_path, 'wb') as file:
            for idx in range(self.ItemNumber):
                file.seek(idx * self.ItemBytes)
                
                file.write(self.data_byte[idx])
                
                len_bytes = len(self.name_byte[idx])
                if len_bytes > len_byteName:
                    bytename = self.name_byte[idx][:len_byteName]
                else:
                    bytename = self.name_byte[idx]

                file.write(bytename)

            ptrs = [ self.ItemNumber ]
            for idx in range(self.ItemNumber):
                ptrs.append(ptrs[-1] + len(self.string_byte[idx])//2)
            
            file.seek(self.StringPtr)
            for idx in range(self.ItemNumber):
                for idx in range(self.Nums):
                    file.write(bytes2(ptrs[idx]))
            
            for idx in range(len(self.string_byte)):
                data = self.string_byte[idx]
                file.write(data)