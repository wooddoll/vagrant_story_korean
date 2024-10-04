import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readNameFile import ReadNames


class TITLE_PRG():
    FileName = 'TITLE/TITLE.PRG'
    
    ItemPtr = 0xc42C
    ItemNumber = 8
    ItemBytes = 0x20

    def __init__(self, input_path: str = '') -> None:
        self.names = ReadNames(self.ItemBytes, self.ItemNumber)
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
        self.names.cvtStr2Byte(table)
        self.names_byte = self.names._byte
    
    def cvtByte2Name(self, table: convert_by_TBL):
        self.names.cvtByte2Str(table)
        self.names_str = self.names._str
            
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            self.names.unpackData(buffer[self.ItemPtr:self.ItemPtr+self.ItemNumber*self.ItemBytes])
            self.names_byte = self.names._byte

    def packData(self, output_path:str):
        byteData = self.names.packData()
        if byteData is not None:
            with open(output_path, 'wb') as file:
                file.seek(self.ItemPtr)
                file.write(byteData)
