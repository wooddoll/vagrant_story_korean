from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class ReadNames():
    def __init__(self, itemBytes: int, itemNums: int, buffer: Union[bytes, None] = None) -> None:
        self.buffer = buffer
        self.itemNums = itemNums
        self.itemBytes = itemBytes
        self._byte = []
        self._str = []
        
        if buffer is not None:
            self.unpackData(buffer)

    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for data in self._str:
            self._byte.append(table.cvtStr_Bytes(data))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for data in self._byte:
            self._str.append(table.cvtBytes_str(data))
            
    def unpackData(self, buffer: bytes):
        self.buffer = buffer        
        len_Buffer = len(buffer)
        
        len_items = len_Buffer // self.itemBytes
        if len_items != self.itemNums:
            logging.critical("!!!")
        
        byte_stream = io.BytesIO(buffer)
        
        self._byte.clear()
        for _ in range(self.itemNums):
            bytename = byte_stream.read(self.itemBytes)
            self._byte.append(bytename) 

    def packData(self):
        if self.buffer is None:
            return None

        if len(self._byte) != self.itemNums:
            logging.critical("!!!")
            
        byte_stream = io.BytesIO(self.buffer)
        for idx in range(self.itemNums):
            len_bytes = len(self._byte[idx])
            
            if len_bytes > self.itemBytes:
                bytename = self._byte[idx][:self.itemBytes]
            else:
                bytename = self._byte[idx]
                
            byte_stream.seek(idx * self.itemBytes)
            byte_stream.write(bytename)


class ItemNames():
    ItemNumber = 512
    ItemBytes = 0x18

    def __init__(self, input_path: str = '') -> None:
        self.names = ReadNames(self.ItemBytes, self.ItemNumber)
        self.names_byte = self.names._byte
        self.names_str = self.names._str

        if input_path:
            self.unpackData(input_path)

    def cvtName2Byte(self, table: convert_by_TBL):
        self.names.cvtStr2Byte(table)
        self.names_byte = self.names._byte
    
    def cvtByte2Name(self, table: convert_by_TBL):
        self.names.cvtByte2Str(table)
        self.names_str = self.names._str
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            self.names.unpackData(buffer)
        
        self.strings_byte = self.names._byte

    def packData(self, output_path:str):
        byteData = self.names.packData()
        if byteData is not None:
            with open(output_path, 'wb') as file:
                file.write(byteData)
