import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *
from fileStruct.readStrFile import ReadStrings
from fileStruct.readNameFile import ReadNames

class BATTLE_PRG():
    FileName = 'BATTLE/BATTLE.PRG'
    StringPtr = 0x82068     
    NamePtr = 0x83758
    NameNumber = 20
    NameBytes = 0x18

    def __init__(self, input_path: str = '') -> None:
        self.strings = ReadStrings()
        self.strings_byte = self.strings._byte
        self.strings_str = self.strings._str
        
        self.names = ReadNames(self.NameBytes, self.NameNumber)
        self.names_byte = self.names._byte
        self.names_str = self.names._str
        
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
        self.strings.cvtStr2Byte(table)
        self.strings_byte = self.strings._byte
        
        self.names.cvtStr2Byte(table)
        self.names_byte = self.names._byte

    def cvtByte2Name(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)
        self.strings_str = self.strings._str
        
        self.names.cvtByte2Str(table)
        self.names_str = self.names._str
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            
            self.strings.unpackData(buffer[self.StringPtr:])
            self.strings_byte = self.strings._byte
            
            self.names.unpackData(buffer[self.NamePtr:self.NamePtr + self.NameNumber*self.NameBytes])

    def packData(self, output_path:str):
        if len(self.strings._byte) != self.strings.itemNums:
            logging.critical("!!!")
        if len(self.names_byte) != self.NameNumber:
            logging.critical("!!!")

        with open(output_path, 'wb') as file:
            stringData = self.strings.packData()
            if stringData is not None:
                file.seek(self.StringPtr)
                file.write(stringData)
            
            nameData = self.names.packData()
            if nameData is not None:
                file.seek(self.NamePtr)
                file.write(nameData)