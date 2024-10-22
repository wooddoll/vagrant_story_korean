from typing import Union, List, Tuple
import os
import io
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readStrFile import ReadStrings
from utils import *

def int2Hex(integer: int, table: convert_by_TBL):
    tmp = f'{integer:03X}'
    data = table.cvtStr2Byte(tmp)
    return data
    
class merge_MCMAN(): 
    FileName = 'MENU/MCMAN.BIN'
    def __init__(self, input_path: str = '') -> None:
        self.buffer = bytes()
        self.ptrs: List[int] = []
        self.strings = ReadStrings()

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
        
    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)
        
    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            self.buffer = file.read()
            self.strings.unpackData(self.buffer)
            
            byte_stream = io.BytesIO(self.buffer)
            self.itemNums = int2(byte_stream.read(2))
            byte_stream.seek(0)
            self.ptrs = []
            if self.itemNums:
                for _ in range(self.itemNums):
                    pos = int2(byte_stream.read(2))
                    self.ptrs.append(2*pos)
            self.ptrs.append(len(self.buffer))
    
    def setBlank(self, table: convert_by_TBL):
        len_buffer = len(self.buffer)
        byte_stream = io.BytesIO()
        
        pos = 0
        idx = 0
        while pos < len_buffer:
            data = int2Hex(idx, table)
            byte_stream.write(data)
            pos += 4
            idx += 1
            if 0xFFF < idx:
                idx = 0

        self.buffer = byte_stream.getvalue()
        
    def checkPtrs(self):
        ptrs = [ 2*self.itemNums ]
        for idx in range(self.itemNums):
            if not self.strings._byte[idx] or self.strings._byte[idx][-1] != 0xE7:
                 self.strings._byte[idx].append(0xE7)
            if len(self.strings._byte[idx])%2:  # align 2byte padding
                self.strings._byte[idx].append(0xEB)
        
        for idx in range(self.itemNums):
            ptrs.append(ptrs[-1] + len(self.strings._byte[idx]))
        ptrs.append(len(self.buffer))
        
        pre_sizes = []
        for idx in range(self.itemNums):
            pre_sizes.append(self.ptrs[idx+1] - self.ptrs[idx])
        
        cur_sizes = []
        for idx in range(self.itemNums):
            cur_sizes.append(ptrs[idx+1] - ptrs[idx])
            
        for idx in range(self.itemNums):
            print(f"{idx}: {self.ptrs[idx]}({pre_sizes[idx]}) / {ptrs[idx]}({cur_sizes[idx]})")
            
    def packData(self, output_path: str):
        outPath = ''
        if os.path.isfile(output_path):
            outPath = output_path
        elif os.path.isdir(output_path):
            filepath = Path(output_path) / Path(self.FileName)
            outPath = str(filepath)
        else:
            logging.warning(f'{output_path} is not valid path.')
        
        byteData = self.strings.packData()
        pre_sizes = []
        for idx in range(self.itemNums):
            pre_sizes.append(self.ptrs[idx+1] - self.ptrs[idx])
            
        ptrs = [ 2*self.itemNums ]
        for idx in range(self.itemNums):
            ptrs.append(ptrs[-1] + len(self.strings._byte[idx]))
        
        cur_sizes = []
        for idx in range(self.itemNums):
            cur_sizes.append(ptrs[idx+1] - ptrs[idx])
            
        for idx in range(self.strings.itemNums):
            print(f'{idx}th data, {pre_sizes[idx]} / {cur_sizes[idx]}')
            if pre_sizes[idx] < cur_sizes[idx]:
                logging.critical(f'{idx}th data overflow, {pre_sizes[idx]} < {cur_sizes[idx]}')
            
        if byteData is not None:
            with open(outPath, 'wb') as file:
                file.write(self.buffer)

                file.seek(0)
                for idx in range(self.strings.itemNums):
                    file.write(bytes2(self.ptrs[idx]//2))
                    
                for idx in range(self.strings.itemNums):
                    file.seek(self.ptrs[idx])
                    file.write(self.strings._byte[idx])


'''
def MCMAN_merge(kor_strings: dict):
    curr = merge_MCMAN(PATH_JPN_VARGRANTSTORY)

    curr.cvtByte2Str(jpnTBL)    
    texts = kor_strings['MCMAN']
    for k, v in texts.items():
        idx = int(k)
        txt = v.get('string')
        if txt is None: continue
        curr.strings._str[idx] = txt
        
    curr.cvtStr2Byte(korTBL)
    #curr.checkPtrs()
    #curr.setBlank(jpnTBL)
    curr.packData(PATH_KOR_VARGRANTSTORY)
    
'''