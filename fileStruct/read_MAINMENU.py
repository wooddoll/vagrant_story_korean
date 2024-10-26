from typing import Union, List, Tuple
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from copy import deepcopy


def create1strings0Class(FileName: str, stringPtr: int, stringLength: int):
    class Class_Nstrings(): 
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self._str = ''
            self._byte = bytearray()

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
            _byte = table.cvtStr2Byte(self._str)
            self._byte = _byte[:-1]

        def cvtByte2Str(self, table: convert_by_TBL):
            self._byte.append(0xE7)
            self._str = table.cvtByte2Str(self._byte)

        def unpackData(self, input_path: str):    
            with open(input_path, 'rb') as file:
                self.buffer = file.read()
                file.seek(stringPtr)
                self._byte = bytearray(file.read(stringLength))

        def packData(self, output_path: str):
            outPath = ''
            if os.path.isfile(output_path):
                outPath = output_path
            elif os.path.isdir(output_path):
                filepath = Path(output_path) / Path(FileName)
                outPath = str(filepath)
            else:
                logging.warning(f'{output_path} is not valid path.')
                
            with open(outPath, 'wb') as file:
                file.write(self.buffer)
                file.seek(stringPtr)
                len_byte = len(self._byte)
                if len_byte > stringLength:
                    logging.critical(f'string overflow MAINMENU {stringLength} < {len_byte}')
                _byte = deepcopy(self._byte)
                if len_byte < stringLength:
                    zeros = bytes(stringLength-len_byte)
                    _byte.extend(zeros)
                file.write(_byte)

    return Class_Nstrings

MAINMENU_en = create1strings0Class('MENU/MAINMENU.PRG', 0x88D4, 0x1D)
MAINMENU_jp = create1strings0Class('MENU/MAINMENU.PRG', 0x894C, 0x1C)
