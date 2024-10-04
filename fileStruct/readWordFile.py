from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class ReadWords():
    def __init__(self, wordBytes: int, wordNums: int, buffer: Union[bytes, None] = None) -> None:
        self.buffer = buffer
        self.wordNums = wordNums
        self.wordBytes = wordBytes
        self._byte = []
        self._str = []
        
        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        return self.wordNums*self.wordBytes if self.buffer is not None else 0
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for data in self._str:
            self._byte.append(table.cvtStr_Bytes(data))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for data in self._byte:
            self._str.append(table.cvtBytes_str(data))
            
    def unpackData(self, buffer: bytes):
        self.buffer = buffer[:self.wordBytes*self.wordNums]
        byte_stream = io.BytesIO(buffer)
        
        self._byte.clear()
        for _ in range(self.wordNums):
            bytename = byte_stream.read(self.wordBytes)
            self._byte.append(trimTextBytes(bytename)) 

    def packData(self):
        if self.buffer is None:
            return None

        if len(self._byte) != self.wordNums:
            logging.critical(f"check the words numbers, size mismatched; privious({self.wordNums}) != current({len(self._byte)})")
            
        byte_stream = io.BytesIO(self.buffer)
        for idx in range(self.wordNums):
            len_bytes = len(self._byte[idx])
            
            if len_bytes > self.wordBytes:
                bytename = self._byte[idx][:self.wordBytes]
                logging.critical(f"check the word length, size overflowed; allocated({self.wordBytes}) < current({len_bytes})")
            else:
                bytename = self._byte[idx]
                
            byte_stream.seek(idx * self.wordBytes)
            byte_stream.write(bytename)



def createWordStringClass(filename: str, wordPtr: int, wordSize: int, wordNum: int):
    class Class_Word():
        FileName = filename
        WordPtr = wordPtr
        WordBytes = wordSize
        WordNumber = wordNum

        def __init__(self, input_path: str = '') -> None:
            self.words = ReadWords(self.WordBytes, self.WordNumber)
            self.words_byte = self.words._byte
            self.words_str = self.words._str

            if os.path.isfile(input_path):
                self.unpackData(input_path)
            elif os.path.isdir(input_path):
                filepath = Path(input_path) / Path(self.FileName)
                if os.path.isfile(str(filepath)):
                    self.unpackData(str(filepath))
                else:
                    logging.warning(f'{input_path} is not valid path.')
            else:
                logging.warning(f'{input_path} is not valid path.')

        def cvtName2Byte(self, table: convert_by_TBL):
            self.words.cvtStr2Byte(table)
            self.words_byte = self.words._byte

        def cvtByte2Name(self, table: convert_by_TBL):
            self.words.cvtByte2Str(table)
            self.words_str = self.words._str

        def unpackData(self, input_path:str):
            with open(input_path, 'rb') as file:
                buffer = bytearray(file.read())
                self.words.unpackData(buffer[self.WordPtr : self.WordPtr + self.WordNumber*self.WordBytes])
                self.words_byte = self.words._byte

        def packData(self, output_path:str):
            byteData = self.words.packData()
            if byteData is not None:
                with open(output_path, 'wb') as file:
                    file.seek(self.ItemPtr)
                    file.write(byteData)

    return Class_Word

ITEMNAME_BIN = createWordStringClass('MENU/ITEMNAME.BIN', 0x0, 0x18, 512)