from typing import Union, List, Tuple
import os
import io
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readStrFile import ReadStrings
from utils import *
from copy import deepcopy

def int2Hex(integer: int, table: convert_by_TBL):
    tmp = f'{integer:03X}'
    data = table.cvtStr2Byte(tmp)
    return data

def createStringBINNClass(FileName: str, keepPos: List[int] = [], startPtr = 0x0):
    class StringBINNClass(): 
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.ptrs: List[int] = []
            self.strings = ReadStrings()
            self.itemNums = 0
            if input_path:
                self.unpackData(input_path)

        def cvtStr2Byte(self, table: convert_by_TBL):
            self.strings.cvtStr2Byte(table)

        def cvtByte2Str(self, table: convert_by_TBL):
            self.strings.cvtByte2Str(table)

        def unpackData(self, input_path: str):
            inputFile = ''
            if os.path.isfile(input_path):
                inputFile = input_path
            elif os.path.isdir(input_path):
                filepath = Path(input_path) / Path(FileName)
                if os.path.isfile(str(filepath)):
                    inputFile = str(filepath)
                else:
                    logging.warning(f'{input_path} is not valid path.')
                    return
            else:
                logging.warning(f'{input_path} is not valid path.')
                return
            
            
            with open(inputFile, 'rb') as file:
                self.buffer = file.read()
                self.strings.unpackData(self.buffer[startPtr:])

                byte_stream = io.BytesIO(self.buffer[startPtr:])
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
                filepath = Path(output_path) / Path(FileName)
                outPath = str(filepath)
            else:
                logging.warning(f'{output_path} is not valid path.')

            byteData = self.strings.packData()
            pre_sizes = []
            for idx in range(self.itemNums):
                pre_sizes.append(self.ptrs[idx+1] - self.ptrs[idx])

            cur_sizes = []
            for idx in range(self.itemNums):
                cur_sizes.append(len(self.strings._byte[idx]))
                
            ptrs = deepcopy(self.ptrs)

            if keepPos:
                for idx in range(self.itemNums):
                    if idx in keepPos:
                        ptrs[idx] = self.ptrs[idx]
                    else:
                        if 0 < idx:
                            ptrs[idx] = ptrs[idx-1] + cur_sizes[idx-1]

            if not keepPos:
                for idx in range(self.strings.itemNums):
                    #print(f'{idx}th data, {pre_sizes[idx]} / {cur_sizes[idx]}')
                    if pre_sizes[idx] < cur_sizes[idx]:
                        logging.critical(f'{idx}th data overflow, {pre_sizes[idx]} < {cur_sizes[idx]}')
            else:
                for idx in keepPos:
                    #print(f'{idx}th data, {pre_sizes[idx]} / {cur_sizes[idx]}')
                    if pre_sizes[idx] < cur_sizes[idx]:
                        logging.critical(f'{idx}th data overflow, {pre_sizes[idx]} < {cur_sizes[idx]}')

            if byteData is not None:
                with open(outPath, 'wb') as file:
                    file.write(self.buffer)

                    file.seek(startPtr)
                    for idx in range(self.strings.itemNums):
                        file.write(bytes2(ptrs[idx]//2))

                    for idx in range(self.strings.itemNums):
                        file.seek(startPtr+ptrs[idx])
                        file.write(self.strings._byte[idx])
    return StringBINNClass


MCMAN = createStringBINNClass('MENU/MCMAN.BIN')

ITEMHELP_indexes = list(range(373, 413))
#ITEMHELP_indexes.extend([438, 439])
ITEMHELP_indexes.extend(list(range(641, 679)))
ITEMHELP = createStringBINNClass('MENU/ITEMHELP.BIN', ITEMHELP_indexes)
MENU4 = createStringBINNClass('MENU/MENU4.PRG', [7, 8, 9, 10, 11, 12], 0x4c44)

BATTLE_3 = createStringBINNClass('BATTLE/BATTLE.PRG', [11], 0x83080)

MENU0 = createStringBINNClass('MENU/MENU0.PRG', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 0x2258)
MENU1 = createStringBINNClass('MENU/MENU1.PRG', [30], 0xC78)
MENU2 = createStringBINNClass('MENU/MENU2.PRG', [0, 1, 2, 3, 4, 5], 0x1e90)
MENU2_1 = createStringBINNClass('MENU/MENU2.PRG', [12, 13, 14, 15, 16, 17], 0x2478)
MENU3 = createStringBINNClass('MENU/MENU3.PRG', [], 0x6bb4)
MENU7 = createStringBINNClass('MENU/MENU7.PRG', startPtr=0x7c54)
MENU12 = createStringBINNClass('MENU/MENU12.BIN')
#NAMEDIC = createStringBINNClass('MENU/NAMEDIC.BIN', [9, 10, 11, 12])
MENUB = createStringBINNClass('MENU/MENUB.PRG', startPtr=0x7a80)

MON = createStringBINNClass('SMALL/MON.BIN', [], 0x19C8)

FileLoadFuncNames = ['MENU0', 'MENU1', 'MENU2', 'MENU2_1', 'MENU3', 'MENU4', 'MENU7', 'MENU12', 'MCMAN', 'ITEMHELP',
                     'MENUB', 'BATTLE_3', 'MON' ]

def getNNClass(className: str):
    Class_jp = None
    
    if className in globals():
        Class_jp = globals()[className]
        
    if Class_jp is None:
        if f'{className}_jp' in globals():
            Class_jp = globals()[f'{className}_jp']
        if Class_jp is None:    
            logging.warning(f'wrong function name {className}')
    
    return Class_jp