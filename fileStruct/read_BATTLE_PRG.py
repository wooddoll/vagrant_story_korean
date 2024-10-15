import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *
from fileStruct.readStrFile import ReadStrings
from fileStruct.readWordFile import ReadWords

def createString_Word_Class(filename: str, stringPtr: int, stringPtr2: int, wordPtr: int, wordNum: int, wordBytes: int):
    class Class_String_Word():
        FileName = filename
        StringPtr = stringPtr
        StringPtr2 = stringPtr2
        WordPtr = wordPtr
        WordNumber = wordNum
        WordBytes = wordBytes

        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            
            self.strings = ReadStrings()
            self.strings_byte = self.strings._byte
            self.strings_str = self.strings._str
            
            self.strings2 = ReadStrings()
            self.strings2_byte = self.strings2._byte
            self.strings2_str = self.strings2._str

            self.words = ReadWords(self.WordBytes, self.WordNumber)
            self.words_byte = self.words._byte
            self.words_str = self.words._str

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
            
            self.strings2.cvtStr2Byte(table)
            self.strings2_byte = self.strings2._byte

            self.words.cvtStr2Byte(table)
            self.words_byte = self.words._byte

        def cvtByte2Str(self, table: convert_by_TBL):
            self.strings.cvtByte2Str(table)
            self.strings_str = self.strings._str
            
            self.strings2.cvtByte2Str(table)
            self.strings2_str = self.strings2._str

            self.words.cvtByte2Str(table)
            self.words_str = self.words._str

        def unpackData(self, input_path:str):
            with open(input_path, 'rb') as file:
                self.buffer = file.read()

                self.strings.unpackData(self.buffer[self.StringPtr:])
                self.strings_byte = self.strings._byte
                
                self.strings2.unpackData(self.buffer[self.StringPtr2:])
                self.strings2_byte = self.strings2._byte

                self.words.unpackData(self.buffer[self.WordPtr : self.WordPtr + self.WordNumber*self.WordBytes])

        def packData(self, output_path:str):
            if len(self.strings._byte) != self.strings.itemNums:
                logging.critical("!!!")
            if len(self.words_byte) != self.WordNumber:
                logging.critical("!!!")
            if len(self.strings2._byte) != self.strings2.itemNums:
                logging.critical("!!!")

            with open(output_path, 'wb') as file:
                file.write(self.buffer)
                
                logging.info(f"BATTLE_1 / ")
                stringData = self.strings.packData()
                if stringData is not None:
                    file.seek(self.StringPtr)
                    file.write(stringData)
                
                logging.info(f"BATTLE_2 / ")
                nameData = self.words.packData()
                if nameData is not None:
                    file.seek(self.WordPtr)
                    file.write(nameData)
                
                logging.info(f"BATTLE_3 / ")
                stringData2 = self.strings2.packData()
                if stringData2 is not None:
                    file.seek(self.StringPtr2)
                    file.write(stringData2)

    return Class_String_Word

BATTLE_PRG_en = createString_Word_Class('BATTLE/BATTLE.PRG', 0x82068, 0x831DC, 0x83758, 21, 0x18)
BATTLE_PRG_jp = createString_Word_Class('BATTLE/BATTLE.PRG', 0x82050, 0x83080, 0x83520, 21, 0x18)