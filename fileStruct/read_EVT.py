from typing import Union, List, Dict
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

from fileStruct.readStrFile import ReadStrings
from fileStruct.structMPD import ScriptSection

class read_EVT: 
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytes()
        self.data = ScriptSection()
        self.strings_byte = self.data.dialogText.strings_byte
        self.strings_str = self.data.dialogText.strings_str
        
        if os.path.isfile(input_path):
            self.unpackData(input_path)
        else:
            logging.warning(f'{input_path} is not valid path.')
            
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.data.cvtStr2Byte(table)
        self.strings_byte = self.data.dialogText.strings_byte
        
    def cvtByte2Str(self, table: convert_by_TBL):
        self.data.cvtByte2Str(table)
        self.strings_str = self.data.dialogText.strings_str
        
    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            self.buffer = file.read()
            self.data.unpackData(self.buffer)
        
    def packData(self, output_path: str):
        prevStr = self.data.header[2] - self.data.header[1]
        
        buffer = self.data.packData()

        new_len_buffer = len(self.data.dialogText.strings) if 0 < self.data.dialogText.strings.itemNums else 0
        new_len_buffer = ((new_len_buffer+3)//4)*4

        ppx = False
        if not all([x==0 for x in self.data.unknownSection1.buffer]):
            ppx = True
        if not all([x==0 for x in self.data.unknownSection2.buffer]):
            ppx = True
        if prevStr < new_len_buffer:
            if ppx:
                logging.critical(f"{Path(output_path).stem}, check the length of strings, size overflowed; {prevStr} < current({new_len_buffer})")
            else:
                logging.warning(f"{Path(output_path).stem}, check the length of strings, size overflowed; {prevStr} < current({new_len_buffer})")
                        
        if buffer is not None:
            self.buffer = buffer
            with open(output_path, 'wb') as file:
                file.write(self.buffer)
                currSize = file.tell()
                if 4096 < currSize:
                    over = currSize - 4096
                    logging.critical(f"check the length of strings, size overflowed; {new_len_buffer-over} < current({new_len_buffer})")


class EVENT_EVT:
    def __init__(self, input_folder: str) -> None:
        self.evtFiles: Dict[int, ScriptSection] = {}
        
        if os.path.isdir(input_folder):
            self.unpackData(input_folder)
        else:
            logging.warning(f'{input_folder} is not valid path.')
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        for k, v in self.evtFiles.items():
            v.cvtStr2Byte(table)
        
    def cvtByte2Str(self, table: convert_by_TBL):
        for k, v in self.evtFiles.items():
            v.cvtByte2Str(table)
        
    def unpackData(self, input_folder: str):
        self.evtFiles.clear()
        
        folder_path = Path(input_folder) / Path('EVENT')
        file_list = [file for file in folder_path.rglob('*.EVT') if file.is_file()]
        file_list = sorted(file_list)
        for filepath in file_list:
            relative_path = filepath.relative_to(input_folder)
            idx = int(relative_path.stem)
            
            evt = read_EVT(str(filepath))
            
            if evt.strings_byte:
                self.evtFiles[idx] = evt
    
    def packData(self, output_folder: str):
        for k, v in self.evtFiles.items():
            idx = int(k)
            #logging.info(f"{idx:04}.EVT")
            #print(f"{idx:04}.EVT")
            output_path =  Path(output_folder) / Path('EVENT') / Path(f'{idx:04}.EVT')
            v.packData(str(output_path))



