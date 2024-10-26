import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *
from fileStruct.readStrFile import ReadStrings

class read_MCMAN():
    FileName = 'MENU/MCMAN.BIN'
    
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytes()       
        self.strings = ReadStrings()
        
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
        
        for data in self.strings._byte:
            if data[-1] == 0xE7 and len(data)%2:
                data[-1] = 0xE6
                data.append(0xE7)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)

    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = file.read()
            self.strings.unpackData(self.buffer)

    def packData(self, output_path:str):
        if len(self.strings._byte) != self.strings.itemNums:
            logging.critical("!!!")

        with open(output_path, 'wb') as file:
            file.write(self.buffer)
            
            stringData = self.strings.packData()
            if stringData is not None:
                file.seek(0)
                file.write(stringData)
                