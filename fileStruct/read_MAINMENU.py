from typing import Union, List, Tuple
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from copy import deepcopy

class SpecialWordData:
    def __init__(self, ptr: int, length: int, closer = False) -> None:
        self.ptr = ptr
        self.length = length
        self.closer = closer
        self._str = ''
        self._byte = bytearray()
        
def create1strings0Class(FileName: str, words: List[SpecialWordData]):
    class Class_Nstrings(): 
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.words = deepcopy(words)
            
            if input_path:
                self.unpackData(input_path)

        def cvtStr2Byte(self, table: convert_by_TBL):
            for word in self.words:
                _byte = table.cvtStr2Byte(word._str)
                __byte = bytearray()
                len_byte = len(_byte)
                pos = 0
                while pos < len_byte:
                    t = _byte[pos]
                    if t < 0xE5:
                        __byte.append(0xEC)
                        __byte.append(t)
                        pos += 1
                    else:
                        __byte.extend(_byte[pos:pos+2])
                        pos += 2
                
                word._byte = __byte if word.closer else __byte[:-1]

        def cvtByte2Str(self, table: convert_by_TBL):
            for word in self.words:
                _byte = bytearray()
                for i in range(0, len(word._byte), 2):
                    t = word._byte[i:i+2]
                    if t[0] == 0xEC and t[1] < 0xE5:
                        _byte.append(t[1])
                    else:
                        _byte.extend(t)
                
                if not word.closer:
                    _byte.append(0xE7)

                word._str = table.cvtByte2Str(_byte)

        def unpackData(self, input_path: str):
            filePath = input_path
            if not os.path.isfile(input_path):
                if os.path.isdir(input_path):
                    filePath = str(Path(input_path) / Path(FileName))
                    if not os.path.isfile(filePath):
                        logging.critical(f'{input_path} is not valid path.')
                else:
                    logging.critical(f'{input_path} is not valid path.')
                
            with open(filePath, 'rb') as file:
                self.buffer = file.read()
                
                for word in self.words:
                    file.seek(word.ptr)
                    word._byte = bytearray(file.read(word.length))

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
                
                for word in self.words:
                    file.seek(word.ptr)
                    len_byte = len(word._byte)
                    if len_byte > word.length:
                        logging.critical(f'string overflow MAINMENU {word.length} < {len_byte}')
                    _byte = deepcopy(word._byte)
                    if len_byte < word.length:
                        diff = word.length - len_byte
                        if word.closer:
                            zeros = bytes(word.length-len_byte)
                            _byte.extend(zeros)
                        elif diff%2:
                            logging.critical('why? !!!')
                        else:
                            zc = diff//2
                            for i in range(zc):
                                _byte.extend(b'\xEC\x8F')
                            
                    file.write(_byte)

    return Class_Nstrings

MAINMENU_en = create1strings0Class('MENU/MAINMENU.PRG', [SpecialWordData(0x8860, 0x6, True), SpecialWordData(0x88D4, 0x1D, False)])
MAINMENU_jp = create1strings0Class('MENU/MAINMENU.PRG', [SpecialWordData(0x88D8, 0x6, True), SpecialWordData(0x894C, 0x1C, False)])
