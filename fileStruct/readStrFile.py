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
        self.len_buffer = -1
        
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
        len_buffer = len(buffer)
        byte_stream = io.BytesIO(buffer)
        
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
            self._byte.append(trimTextBytes(data))

        len_buffer = len(self._byte[-1]) + 1
        if len_buffer%2:
            len_buffer += 1
        self.len_buffer = len_buffer + ptrs[-2]
        
        self.buffer = buffer[:len_buffer]

    def __len__(self):
        return self.len_buffer if self.buffer is not None else 0

    def packData(self):
        if self.buffer is None:
            return None
        
        if self.itemNums != len(self._byte):
            logging.critical(f"check the number of strings, size different; {self.itemNums} != current({len(self._byte)})")
        
        ptrs = [ self.itemNums ]
        for idx in range(self.itemNums):
            ptrs.append(ptrs[-1] + len(self._byte[idx])//2)

        byte_stream = io.BytesIO(self.buffer)
        for idx in range(self.itemNums):
            byte_stream.write(bytes2(ptrs[idx]))
            
        for idx in range(len(self._byte)):
            data = self._byte[idx]
            byte_stream.write(data)
        
        currPos = byte_stream.tell()
        if self.len_buffer < currPos:
            logging.critical(f"check the length of strings, size overflowed; {self.len_buffer} < current({currPos})")
            
        return byte_stream.getvalue()
