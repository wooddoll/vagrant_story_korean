from typing import Union, List, Dict
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *

from fileStruct.readStrFile import ReadStrings

class read_EVT: 
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytes()
        self.strings = ReadStrings()
        self.strings_byte = self.strings._byte
        self.strings_str = self.strings._str
        self.stringPtr = -1
        self.len_buffer = -1
        
        if os.path.isfile(input_path):
            self.unpackData(input_path)
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
            self.buffer = file.read()
            len_buffer = int2(self.buffer[:2])
            self.stringPtr = int2(self.buffer[2:4])
            self.len_buffer = len_buffer - self.stringPtr
            self.strings.unpackData(self.buffer[self.stringPtr:len_buffer])
            self.strings_byte = self.strings._byte
        
    def packData(self, output_path: str):
        byteData = self.strings.packData()
        
        new_len_buffer = len(self.strings)
        if self.len_buffer < new_len_buffer:
            logging.critical(f"check the length of strings, size overflowed; {self.len_buffer} < current({new_len_buffer})")
                
        self.len_buffer = new_len_buffer
        if byteData is not None:
            with open(output_path, 'wb') as file:
                file.write(self.buffer)
                file.seek(self.stringPtr)
                file.write(byteData)


class EVENT_EVT:
    def __init__(self, input_folder: str) -> None:
        self.evtFiles: Dict[int, read_EVT] = {}
        
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
            output_path =  Path(output_folder) / Path(f'{idx:04}.EVT')
            v.packData(str(output_path))




def readEVT():
    evts_jp = EVENT_EVT(PATH_JPN_VARGRANTSTORY)
    evts_jp.cvtByte2Str(jpnTBL)
    
    evts_en = EVENT_EVT(PATH_USA_VARGRANTSTORY)
    evts_en.cvtByte2Str(usaTBL)
    
    texts = {}
    for k in evts_jp.evtFiles.keys():
        text_file = {}
        _jp = evts_jp.evtFiles[k]
        _en = evts_en.evtFiles[k]
        for idx in range(len(_jp.strings_str)):
            jp = _jp.strings_str[idx]
            if idx < len(_en.strings_str):
                en = _en.strings_str[idx]
            else:
                en = ''

            if not jp and not en:
                continue
            
            singleRow = {}
            singleRow['string'] = jp
            singleRow['@@localazy:comment:string'] = en
            text_file[f'{idx:03}'] = singleRow
        texts[f'{int(k):03}'] = text_file
    
    print()