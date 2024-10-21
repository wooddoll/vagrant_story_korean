from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

class ReadWords():
    def __init__(self, wordBytes: int, wordNums: int, buffer: Union[bytes, None] = None, stride: int = -1) -> None:
        self.buffer = buffer
        self.wordNums = wordNums
        self.wordBytes = wordBytes
        self.stride = stride if 0 < stride else wordBytes
        self._byte = []
        self._str = []
        
        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        return self.wordNums*self.wordBytes if self.buffer is not None else 0
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for data in self._str:
            if not data:
                self._byte.append(bytearray([0xE7]))
            else:
                self._byte.append(table.cvtStr2Byte(data))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for data in self._byte:
            self._str.append(table.cvtByte2Str(data))
            
    def unpackData(self, buffer: bytes):
        self.buffer = buffer[:self.wordNums*self.stride]
        byte_stream = io.BytesIO(buffer)
        
        self._byte.clear()
        for idx in range(self.wordNums):
            ptr = idx * self.stride
            byte_stream.seek(ptr)
            bytename = byte_stream.read(self.wordBytes)
            len_text = getTextLength(bytename)
            self._byte.append(bytename[:len_text]) 

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
            
            ptr = idx * self.stride
            byte_stream.seek(ptr)
            byte_stream.write(bytename)
        
        return byte_stream.getvalue()



def createWordClass(FileName: str, WordPtr: int, WordLength: int, WordNum: int, Stride: int = -1):
    class Class_Word():
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.words = ReadWords(WordLength, WordNum, None, Stride)
            self.strings_byte = self.words._byte
            self.strings_str = self.words._str

            if os.path.isfile(input_path):
                self.unpackData(input_path)
            elif os.path.isdir(input_path):
                filepath = Path(input_path) / Path(FileName)
                if os.path.isfile(str(filepath)):
                    self.unpackData(str(filepath))
                else:
                    logging.warning(f'{input_path} is not valid path.')
            else:
                logging.warning(f'{input_path} is not valid path.')

        def cvtStr2Byte(self, table: convert_by_TBL):
            self.words.cvtStr2Byte(table)
            self.strings_byte = self.words._byte

        def cvtByte2Str(self, table: convert_by_TBL):
            self.words.cvtByte2Str(table)
            self.strings_str = self.words._str

        def unpackData(self, input_path: str):
            with open(input_path, 'rb') as file:
                self.buffer = file.read()
                self.words.unpackData(self.buffer[WordPtr : WordPtr + WordNum*Stride])
                self.strings_byte = self.words._byte

        def packData(self, output_path: str):
            byteData = self.words.packData()
            if byteData is not None:
                with open(output_path, 'wb') as file:
                    file.write(self.buffer)
                    file.seek(WordPtr)
                    file.write(byteData)

    return Class_Word

TITLE_PRG_en = createWordClass('TITLE/TITLE.PRG', 0xc42C, 0x18, 8, 0x20)
TITLE_PRG_jp = createWordClass('TITLE/TITLE.PRG', 0xA58C, 0x18, 8, 0x20)

ITEMNAME_BIN = createWordClass('MENU/ITEMNAME.BIN', 0x0, 0x18, 512)

SL_Main_en = createWordClass('SLUS_010.40', 0x3C1F8, 0x18, 256, 0x34)
SL_Main_jp = createWordClass('SLPS_023.77', 0x3C1F8, 0x18, 256, 0x34)
