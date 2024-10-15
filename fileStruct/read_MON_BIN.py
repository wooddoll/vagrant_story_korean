import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *
from fileStruct.readStrFile import ReadStrings

class MON_BIN():
    FileName = 'SMALL/MON.BIN'
    ItemNumber = 150
    ItemBytes = 0x2C
    StringPtr = ItemBytes*ItemNumber
    
    def __init__(self, input_path: str = '') -> None:
        self.name_byte = []
        self.name_str = []
        self.data_byte = []
        
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
        self.name_byte.clear()
        for text in self.name_str:
            self.name_byte.append(table.cvtStr_Bytes(text))
        
        self.strings.cvtStr2Byte(table)
        self.strings_byte = self.strings._byte

    def cvtByte2Str(self, table: convert_by_TBL):
        self.name_str.clear()
        for text in self.name_byte:
            self.name_str.append(table.cvtBytes_str(text))
        
        self.strings.cvtByte2Str(table)
        self.strings_str = self.strings._str
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            byte_stream = io.BytesIO(buffer)
            
            self.data_byte.clear()
            self.name_byte.clear()
            for _ in range(self.ItemNumber):
                bytedata = byte_stream.read(self.ItemBytes)
                self.data_byte.append(bytedata[:0x12])
                self.name_byte.append(bytedata[0x12:])

            self.strings.unpackData(buffer[self.StringPtr:])
            self.strings_byte = self.strings._byte
                
    def packData(self, output_path:str):
        if len(self.name_byte) != self.ItemNumber:
            logging.critical("!!!")
        if len(self.strings._byte) != self.ItemNumber:
            logging.critical("!!!")
        
        len_byteName = self.ItemBytes - 0x12
        with open(output_path, 'wb') as file:
            for idx in range(self.ItemNumber):
                file.seek(idx * self.ItemBytes)
                
                file.write(self.data_byte[idx])
                
                len_bytes = len(self.name_byte[idx])
                if len_bytes > len_byteName:
                    bytename = self.name_byte[idx][:len_byteName]
                    logging.critical(f"check the Monster Name size, size overflowed({len_byteName} < {len_bytes})")
                else:
                    bytename = self.name_byte[idx]

                file.write(bytename)

            byteData = self.strings.packData()            
            if byteData is not None:
                file.seek(self.StringPtr)
                file.write(byteData)