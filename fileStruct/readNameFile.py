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

    def __len__(self):
        return self.itemNums*self.itemBytes if self.buffer is not None else 0
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for data in self._str:
            self._byte.append(table.cvtStr_Bytes(data))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for data in self._byte:
            self._str.append(table.cvtBytes_str(data))
            
    def unpackData(self, buffer: bytes):
        self.buffer = buffer[:self.itemBytes*self.itemNums]
        byte_stream = io.BytesIO(buffer)
        
        self._byte.clear()
        for _ in range(self.itemNums):
            bytename = byte_stream.read(self.itemBytes)
            self._byte.append(trimTextBytes(bytename)) 

    def packData(self):
        if self.buffer is None:
            return None

        if len(self._byte) != self.itemNums:
            logging.critical(f"check the words numbers, size mismatched; privious({self.itemNums}) != current({len(self._byte)})")
            
        byte_stream = io.BytesIO(self.buffer)
        for idx in range(self.itemNums):
            len_bytes = len(self._byte[idx])
            
            if len_bytes > self.itemBytes:
                bytename = self._byte[idx][:self.itemBytes]
                logging.critical(f"check the word length, size overflowed; allocated({self.itemBytes}) < current({len_bytes})")
            else:
                bytename = self._byte[idx]
                
            byte_stream.seek(idx * self.itemBytes)
            byte_stream.write(bytename)
