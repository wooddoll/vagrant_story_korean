import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readWordFile import ReadWords

def create_TITLE_PRG(Ptr: int):
    FileName = 'TITLE/TITLE.PRG'
    Number = 8
    Length = 0x18
    Stride = 0x20
        
    class TITLE_PRG():
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.names = ReadWords(Length, Number, None, Stride)
            self.names_byte = self.names._byte
            self.names_str = self.names._str

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
            self.names.cvtStr2Byte(table)
            self.names_byte = self.names._byte

        def cvtByte2Str(self, table: convert_by_TBL):
            self.names.cvtByte2Str(table)
            self.names_str = self.names._str

        def unpackData(self, input_path: str):
            with open(input_path, 'rb') as file:
                self.buffer = file.read()
                self.names.unpackData(self.buffer[Ptr : Ptr + Number*Stride])
                self.names_byte = self.names._byte

        def packData(self, output_path:str):
            byteData = self.names.packData()
            if byteData is not None:
                with open(output_path, 'wb') as file:
                    file.write(self.buffer)
                    file.seek(Ptr)
                    file.write(byteData)
    return TITLE_PRG

TITLE_PRG_en = create_TITLE_PRG(0xc42C)
TITLE_PRG_jp = create_TITLE_PRG(0xA58C)