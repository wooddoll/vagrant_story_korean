import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readStrFile import ReadStrings

class MENU8_PRG(): 
    FileName = 'MENU/MENU8.PRG'
    StringPtr = 0x2d58

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
