from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

maxByteLen = 0

class ReadStrings(): 
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.itemNums = 0
        self._byte = []
        self._str = []
        self.len_buffer = 0
        
        if buffer is not None:
            self.unpackData(buffer)

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
            
            #global maxByteLen
            #xxx = table.cvtStr2Byte(self._str[-1])
            #if maxByteLen < len(xxx):
            #    maxByteLen = len(xxx)
            #    print(f"max string len: {maxByteLen}")
    
    def unpackData(self, buffer: bytes):
        len_buffer = len(buffer)
        byte_stream = io.BytesIO(buffer)
        
        self.itemNums = int2(byte_stream.read(2))
        byte_stream.seek(0)
        
        ptrs = []
        if self.itemNums:
            for idx in range(self.itemNums):
                pos = int2(byte_stream.read(2))
                ptrs.append(2*pos)
            last_300 = ptrs[-1] + 300
            ptrs.append(min(len_buffer, last_300))

        self._byte.clear()
        for idx in range(self.itemNums):
            pos = ptrs[idx]
            nextpos = ptrs[idx+1]
            data = buffer[pos:nextpos]
            len_data = getTextLength(data)
            self._byte.append(bytearray(data[:len_data]))

        if not self._byte:
            self.len_buffer = 0
        else:
            len_buffer = len(self._byte[-1])
            if len_buffer%2:
                len_buffer += 1
            self.len_buffer = ptrs[-2] + len_buffer

    def __len__(self):
        return self.len_buffer if 0 < self.itemNums else 0

    def packData(self):
        if 0 >= self.itemNums:
            return None
        
        if self.itemNums != len(self._byte):
            logging.critical(f"check the number of strings, size different; {self.itemNums} != current({len(self._byte)})")
        
        ptrs = [ self.itemNums ]
        for idx in range(self.itemNums):
            if not self._byte[idx] or self._byte[idx][-1] != 0xE7:
                 self._byte[idx].append(0xE7)
            if len(self._byte[idx])%2:  # align 2byte padding
                self._byte[idx].append(0xEB)
        
        for idx in range(self.itemNums):
            ptrs.append(ptrs[-1] + len(self._byte[idx])//2)

        byte_stream = io.BytesIO()
        for idx in range(self.itemNums):
            byte_stream.write(bytes2(ptrs[idx]))
            
        for idx in range(self.itemNums):
            data = self._byte[idx]
            #if 80 < len(data):
            #    logging.critical(f"check the length of strings, size overflowed; {80} < current({len(data)})")
            #    logging.critical(f"{idx}: {self._str[idx]}")
            byte_stream.write(data)
        
        currPos = byte_stream.tell()
        if self.len_buffer < currPos:
            logging.warning(f"check the length of strings, size overflowed; {self.len_buffer} < current({currPos})")
        
        self.len_buffer = currPos
        
        return byte_stream.getvalue()

def createStringClass(FileName: str, StringPtr: int):
    class Class_String: 
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.strings = ReadStrings()
            self.strings_byte = self.strings._byte
            self.strings_str = self.strings._str
            self.len_buffer = -1
            
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
            self.strings.cvtStr2Byte(table)
            self.strings_byte = self.strings._byte

        def cvtByte2Str(self, table: convert_by_TBL):
            self.strings.cvtByte2Str(table)
            self.strings_str = self.strings._str

        def unpackData(self, input_path: str):
            with open(input_path, 'rb') as file:
                self.buffer = file.read()

                self.strings.unpackData(self.buffer[StringPtr:])
                self.strings_byte = self.strings._byte
                
                if StringPtr == 0x0:
                    fileSize = os.path.getsize(input_path)
                    self.len_buffer = ((fileSize + 2047)//2048)*2048
                else:
                    self.len_buffer = len(self.strings)
            
        def packData(self, output_path: str):
            byteData = self.strings.packData()
            
            new_len_buffer = len(self.strings)
            if self.len_buffer < new_len_buffer:
                logging.critical(f"check the length of strings, size overflowed; {self.len_buffer} < current({new_len_buffer})")
                    
            self.len_buffer = new_len_buffer

            if byteData is not None:
                with open(output_path, 'wb') as file:
                    file.write(self.buffer)
                    file.seek(StringPtr)
                    file.write(byteData)
    
    return Class_String

MENU0_PRG = createStringClass('MENU/MENU0.PRG', 0x2258)
MENU1_PRG = createStringClass('MENU/MENU1.PRG', 0xC78)
MENU2_PRG = createStringClass('MENU/MENU2.PRG', 0x1e90)

MENU3_PRG_jp = createStringClass('MENU/MENU3.PRG', 0x6bb4)
MENU3_PRG_en = createStringClass('MENU/MENU3.PRG', 0x6bb8)

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
ITEMHELP_BIN = createStringClass('MENU/ITEMHELP.BIN', 0x0)

NAMEDIC_BIN = createStringClass('MENU/NAMEDIC.BIN', 0x0)