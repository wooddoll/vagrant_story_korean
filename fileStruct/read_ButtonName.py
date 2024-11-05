from typing import Union, List, Tuple
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
import io
import utils

START_BUTTON = [0x2468, 0x2480]
X_BUTTON = [0x240C, 0x2428, 0x2440]
SQUARE_BUTTON = [0x23C8, 0x23E0]
TRIANGLE_BUTTON = [0x2380, 0x23A4]
BUTTONS = [START_BUTTON, X_BUTTON, SQUARE_BUTTON, TRIANGLE_BUTTON]

class ButtonSpecial:
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytes()
        self._str: List[str] = []
        self._byte: List[bytearray] = []
        
        if input_path:
            self.unpackData(input_path)
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for _str in self._str:
            string = bytearray()
            for letter in _str:
                _byte = table.cvtStr2Byte(letter)[:-1]
                _letter = int.from_bytes(_byte, byteorder='big')
                if 0xFF < _letter:
                    _letter -= 0xEC00
                string.extend(utils.bytes2(_letter))
            self._byte.append(string)
        
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for _byte in self._byte:
            common = bytearray()
            len_byte = len(_byte)
            for i in range(0, len_byte, 2):
                letter = utils.int2(_byte[i:i+2])
                if 0x00FF < letter:
                    letter += 0xEC00
                    _letter = letter.to_bytes(2, byteorder='big', signed=False)
                    common.extend(_letter)
                else:
                    _letter = letter.to_bytes(1, byteorder='big', signed=False)
                    common.extend(_letter)
            
            _str = table.cvtByte2Str(common)
            self._str.append(_str)
        
    def unpackData(self, input_path: str):
        if os.path.isfile(input_path):
            filepath = input_path
        elif os.path.isdir(input_path):
            filepath = str(Path(input_path) / Path('MENU/MENU8.PRG'))
            if not os.path.isfile(str(filepath)):
                logging.critical(f'{input_path} is not valid path.')
                return
        else:
            logging.critical(f'{input_path} is not valid path.')
            return
            
        with open(filepath, 'rb') as file:
            self.buffer = file.read()
            
        byte_stream = io.BytesIO(self.buffer)    
        
        self._byte.clear()
        for BUTTON in BUTTONS:
            string = bytearray()
            for ptr in BUTTON:
                byte_stream.seek(ptr)
                _byte = byte_stream.read(2)
                string.extend(_byte)
            self._byte.append(string)
    
    def packData(self, output_path: str):
        outPath = ''
        if os.path.isfile(output_path):
            outPath = output_path
        elif os.path.isdir(output_path):
            filepath = Path(output_path) / Path('MENU/MENU8.PRG')
            outPath = str(filepath)
        else:
            logging.critical(f'{output_path} is not valid path.')
            return
            
        with open(outPath, 'wb') as file:
            file.write(self.buffer)
            
            for i0, BUTTON in enumerate(BUTTONS):
                for i1, ptr in enumerate(BUTTON):
                    _byte = self._byte[i0][2*i1:2*i1+2]
                    file.seek(ptr)
                    file.write(_byte)