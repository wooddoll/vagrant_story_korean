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

def createStringClass(filename: str, stringPtr: int):
    class Class_String: 
        FileName = filename
        StringPtr = stringPtr

        def __init__(self, input_path: str = '') -> None:
            self.strings = ReadStrings()
            self.strings_byte = self.strings._byte
            self.strings_str = self.strings._str

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

        def cvtStr2Byte(self, table: convert_by_TBL):
            self.strings.cvtStr2Byte(table)
            self.strings_byte = self.strings._byte

        def cvtByte2Str(self, table: convert_by_TBL):
            self.strings.cvtByte2Str(table)
            self.strings_str = self.strings._str

        def unpackData(self, input_path: str):
            with open(input_path, 'rb') as file:
                buffer = bytearray(file.read())
                self.strings.unpackData(buffer[self.StringPtr:])
                self.strings_byte = self.strings._byte

        def packData(self, output_path: str):
            byteData = self.strings.packData()
            if byteData is not None:
                with open(output_path, 'wb') as file:
                    file.seek(self.StringPtr)
                    file.write(byteData)
    
    return Class_String

MENU0_PRG = createStringClass('MENU/MENU0.PRG', 0x2258)
MENU1_PRG = createStringClass('MENU/MENU1.PRG', 0xC78)
MENU2_PRG = createStringClass('MENU/MENU2.PRG', 0x1e90)
MENU3_PRG = createStringClass('MENU/MENU3.PRG', 0x6bb8)

MENU4_PRG_en = createStringClass('MENU/MENU4.PRG', 0x4C48)
MENU4_PRG_jp = createStringClass('MENU/MENU4.PRG', 0x4c44)

MENU5_PRG_en = createStringClass('MENU/MENU5.PRG', 0x5bfc)
MENU5_PRG_jp = createStringClass('MENU/MENU5.PRG', 0x5c14)

MENU7_PRG_en = createStringClass('MENU/MENU7.PRG', 0x81b0)
MENU7_PRG_jp = createStringClass('MENU/MENU7.PRG', 0x7c54)

MENU8_PRG_en = createStringClass('MENU/MENU8.PRG', 0x2d58)
MENU8_PRG_jp = createStringClass('MENU/MENU8.PRG', 0x429c)

#9

MENUB_PRG = createStringClass('MENU/MENUB.PRG', 0x7a80)

MENUD_PRG_en = createStringClass('MENU/MENUD.PRG', 0x6d2c)
MENUD_PRG_jp = createStringClass('MENU/MENUD.PRG', 0x6d30)

MENUE_PRG_en = createStringClass('MENU/MENUE.PRG', 0x2654)
MENUE_PRG_jp = createStringClass('MENU/MENUE.PRG', 0x2644)

MENU12_BIN = createStringClass('MENU/MENU12.BIN', 0x0)
MCMAN_BIN = createStringClass('MENU/MCMAN.BIN', 0x0)