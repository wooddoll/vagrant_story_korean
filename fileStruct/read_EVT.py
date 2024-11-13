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
        self.Unknown1 = bytes()
        self.Unknown2 = bytes()
        
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
            byte_stream = io.BytesIO(self.buffer)
            head = readHeader(byte_stream, 4, 2)

            self.strings.unpackData(self.buffer[head[1]:head[2]])
            self.Unknown1 = self.buffer[head[2]:head[3]]
            self.Unknown2 = self.buffer[head[3]:head[0]]
            
            self.strings_byte = self.strings._byte
        
    def packData(self, output_path: str):
        byte_stream = io.BytesIO(self.buffer)
        head = readHeader(byte_stream, 4, 2)
        byteData = self.strings.packData(True)
        new_len_buffer = len(byteData) if byteData is not None else 0
        new_len_buffer = ((new_len_buffer+3)//4)*4

        prevStr = head[2] - head[1]

        ppx = False
        if not all([x==0 for x in self.Unknown1]):
            ppx = True
        if not all([x==0 for x in self.Unknown2]):
            ppx = True
        if prevStr < new_len_buffer:
            if ppx:
                logging.critical(f"{Path(output_path).stem}, check the length of strings, size overflowed; {prevStr} < current({new_len_buffer})")
            else:
                logging.warning(f"{Path(output_path).stem}, check the length of strings, size overflowed; {prevStr} < current({new_len_buffer})")

        shift = 0
        if prevStr < new_len_buffer:
            shift = new_len_buffer - prevStr
        
        head[0] += shift
        head[2] += shift
        head[3] += shift
                        
        if byteData is not None:
            with open(output_path, 'wb') as file:
                file.write(self.buffer)
                file.seek(0)
                file.write(bytes2(head[0]))
                file.write(bytes2(head[1]))
                file.write(bytes2(head[2]))
                file.write(bytes2(head[3]))
                file.seek(head[1])
                file.write(byteData)
                file.seek(head[2])
                file.write(self.Unknown1)
                file.seek(head[3])
                file.write(self.Unknown2)
                currSize = file.tell()
                if 4096 < currSize:
                    over = currSize - 4096
                    logging.critical(f"check the length of strings, size overflowed; {new_len_buffer-over} < current({new_len_buffer})")


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
            #logging.info(f"{idx:04}.EVT")
            #print(f"{idx:04}.EVT")
            output_path =  Path(output_folder) / Path('EVENT') / Path(f'{idx:04}.EVT')
            v.packData(str(output_path))



