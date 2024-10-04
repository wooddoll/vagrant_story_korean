import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readStrFile import ReadStrings

class MENU9_PRG(): 
    FileName = 'MENU/MENU9.PRG'
    String1Ptr = 0x5D64
    String2Ptr = 0x6e0c

    def __init__(self, input_path: str = '') -> None:
        self.strings1 = ReadStrings()
        self.strings1_byte = self.strings1._byte
        self.strings1_str = self.strings1._str
        
        self.strings2 = ReadStrings()
        self.strings2_byte = self.strings2._byte
        self.strings2_str = self.strings2._str
        
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
        self.strings1.cvtStr2Byte(table)
        self.strings1_byte = self.strings1._byte
        
        self.strings2.cvtStr2Byte(table)
        self.strings2_byte = self.strings2._byte
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings1.cvtByte2Str(table)
        self.strings1_str = self.strings1._str
        
        self.strings2.cvtByte2Str(table)
        self.strings2_str = self.strings2._str
            
    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            
            self.strings1.unpackData(buffer[self.String1Ptr:])
            self.strings1_byte = self.strings1._byte
            
            self.strings2.unpackData(buffer[self.String2Ptr:])
            self.strings2_byte = self.strings2._byte
        
    def packData(self, output_path: str):
        byteData1 = self.strings1.packData()
        byteData2 = self.strings2.packData()
        if byteData1 is not None and byteData2 is not None:
            with open(output_path, 'wb') as file:
                file.seek(self.String1Ptr)
                file.write(byteData1)
                
                file.seek(self.String2Ptr)
                file.write(byteData2)
