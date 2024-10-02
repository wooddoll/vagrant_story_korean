from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *


class ReadStrings(): 
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = buffer
        self.itemNums = -1
        self._byte = []
        self._str = []
        
        if buffer is not None:
            self.unpackData(buffer)

    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for data in self._str:
            self._byte.append(table.cvtStr_Bytes(data, True))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for data in self._byte:
            self._str.append(table.cvtBytes_str(data))
            
    def unpackData(self, buffer: bytes):
        self.buffer = buffer
        len_buffer = len(self.buffer)
        byte_stream = io.BytesIO(self.buffer)
        
        self.itemNums = int2(byte_stream.read(2))
        byte_stream.seek(0)
        
        ptrs = []
        for idx in range(self.itemNums):
            pos = int2(byte_stream.read(2))
            ptrs.append(2*pos)
        ptrs.append(len_buffer)
   
        self._byte.clear()
        for idx in range(self.itemNums):
            pos = ptrs[idx]
            nextpos = ptrs[idx+1]
            data = buffer[pos:nextpos]
            self._byte.append(data)

    def packData(self):
        if self.buffer is None:
            return None
        
        if self.itemNums != len(self._byte):
            logging.critical(f"check the number of texts, size different; {self.itemNums} != current({len(self._byte)})")
        
        ptrs = [ self.itemNums ]
        for idx in range(self.itemNums):
            ptrs.append(ptrs[-1] + len(self._byte[idx])//2)

        byte_stream = io.BytesIO(self.buffer)
        for idx in range(self.itemNums):
            byte_stream.write(bytes2(ptrs[idx]))
            
        for idx in range(len(self._byte)):
            data = self._byte[idx]
            byte_stream.write(data)
        
        return byte_stream.getvalue()


class ReadItemHelp(): 
    def __init__(self, input_path: str = '') -> None:
        self.strings = ReadStrings()
        self.strings_byte = self.strings._byte
        self.strings_str = self.strings._str
        
        if input_path:
            self.unpackData(input_path)

    def cvtStr2Byte(self, table: convert_by_TBL):
        self.strings.cvtStr2Byte(table)
        self.strings_byte = self.strings._byte
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)
        self.strings_str = self.strings._str
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            self.strings.unpackData(buffer)
        
        self.strings_byte = self.strings._byte
        
    def packData(self, output_path:str):
        byteData = self.strings.packData()
        if byteData is not None:
            with open(output_path, 'wb') as file:
                file.write(byteData)
