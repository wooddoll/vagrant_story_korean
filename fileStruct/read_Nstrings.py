from typing import Union, List, Tuple
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readStrFile import ReadStrings
from fileStruct.readWordFile import ReadWords

class WordPos:
    def __init__(self, ptr: int, length: int, num: int, stride = -1) -> None:
        self.Ptr = ptr
        self.Length = length
        self.Num = num
        self.Stride = stride if 0 < stride else length

class Class_Nstrings:
    def __init__(self, input_path: str = '') -> None:
        self.strings: List[ReadStrings] = []
        self.words: List[ReadWords] = []
    def cvtStr2Byte(self, table: convert_by_TBL) -> None:
        pass
    def cvtByte2Str(self, table: convert_by_TBL) -> None:
        pass
    def unpackData(self, input_path: str) -> None:
        pass
    def packData(self, output_path: str) -> None:
        pass

def createNstringsNwordsClass(FileName: str, NstringPtrs: List[int], Nwors: List[WordPos] = [], criticalOverflow = False):
    class Class_Nstrings(): 
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.strings: List[ReadStrings] = []
            self.words: List[ReadWords] = []

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
            for strings in self.strings:
                strings.cvtStr2Byte(table)
                
            for words in self.words:
                words.cvtStr2Byte(table)

        def cvtByte2Str(self, table: convert_by_TBL):
            for strings in self.strings:
                strings.cvtByte2Str(table)
            
            for words in self.words:
                words.cvtByte2Str(table)

        def unpackData(self, input_path: str):    
            with open(input_path, 'rb') as file:
                self.buffer = file.read()

                self.strings.clear()
                for ptr in NstringPtrs:
                    self.strings.append(ReadStrings(self.buffer[ptr:]))
                
                self.words.clear()
                for ptr in Nwors:
                    self.words.append(ReadWords(ptr.Length, ptr.Num, self.buffer[ptr.Ptr : ptr.Ptr + ptr.Num*ptr.Stride], ptr.Stride))

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
                
                for idx in range(len(NstringPtrs)):
                    print(f"index: {idx}")
                    byteData = self.strings[idx].packData()
                    if byteData is not None:
                        file.seek(NstringPtrs[idx])
                        file.write(byteData)
                
                for idx in range(len(Nwors)):
                    byteData = self.words[idx].packData()
                    if byteData is not None:
                        file.seek(Nwors[idx].Ptr)
                        file.write(byteData)

    return Class_Nstrings

MENU0_jp = createNstringsNwordsClass('MENU/MENU0.PRG', [0x2258, 0x30BC])
MENU0_en = createNstringsNwordsClass('MENU/MENU0.PRG', [0x2258, 0x3594])
MENU1 = createNstringsNwordsClass('MENU/MENU1.PRG', [0xC78])
MENU2_jp = createNstringsNwordsClass('MENU/MENU2.PRG', [0x1e90, 0x2478])
MENU2_en = createNstringsNwordsClass('MENU/MENU2.PRG', [0x1e90, 0x26D8])

MENU3_jp = createNstringsNwordsClass('MENU/MENU3.PRG', [0x6bb4])
MENU3_en = createNstringsNwordsClass('MENU/MENU3.PRG', [0x6bb8])

MENU4_en = createNstringsNwordsClass('MENU/MENU4.PRG', [0x4C48])
MENU4_jp = createNstringsNwordsClass('MENU/MENU4.PRG', [0x4c44])

MENU5_en = createNstringsNwordsClass('MENU/MENU5.PRG', [0x5bfc, 0x5E18, 0x60B0])
MENU5_jp = createNstringsNwordsClass('MENU/MENU5.PRG', [0x5c14, 0x5DDC, 0x5FC8])

MENU7_en = createNstringsNwordsClass('MENU/MENU7.PRG', [0x81b0])
MENU7_jp = createNstringsNwordsClass('MENU/MENU7.PRG', [0x7c54])

MENU8_en = createNstringsNwordsClass('MENU/MENU8.PRG', [0x2d58])
MENU8_jp = createNstringsNwordsClass('MENU/MENU8.PRG', [0x429c])

MENU9_jp_Ptrs = [0x5f9c, 0x5fc8, 0x611c, 0x6320, 0x671c, 0x6850, 0x6ca8, 0x6d00, 0x6e6c]
MENU9_jp = createNstringsNwordsClass('MENU/MENU9.PRG', MENU9_jp_Ptrs)

MENU9_en_Ptrs = [0x5d20, 0x5d64, 0x5ee4, 0x61bc, 0x67dc, 0x6a00, 0x6d98, 0x6e0c, 0x6fdc]
MENU9_en = createNstringsNwordsClass('MENU/MENU9.PRG', MENU9_en_Ptrs)

MENUB = createNstringsNwordsClass('MENU/MENUB.PRG', [0x7a80])

MENUD_en = createNstringsNwordsClass('MENU/MENUD.PRG', [0x6d2c])
MENUD_jp = createNstringsNwordsClass('MENU/MENUD.PRG', [0x6d30])

MENUE_en = createNstringsNwordsClass('MENU/MENUE.PRG', [0x2654])
MENUE_jp = createNstringsNwordsClass('MENU/MENUE.PRG', [0x2644])

MENU12 = createNstringsNwordsClass('MENU/MENU12.BIN', [0x0])
MCMAN = createNstringsNwordsClass('MENU/MCMAN.BIN', [0x0])
ITEMHELP = createNstringsNwordsClass('MENU/ITEMHELP.BIN', [0x0])

ptr_BATTLE_en = [0x82068, 0x831DC, 0x835DC]
BATTLE_en = createNstringsNwordsClass('BATTLE/BATTLE.PRG', [0x82068, 0x835DC], [WordPos(0x83758, 0x18, 33)])
ptr_BATTLE_jp = [0x82050, 0x83080, 0x8341C]
BATTLE_jp = createNstringsNwordsClass('BATTLE/BATTLE.PRG', [0x8341C], [WordPos(0x83520, 0x18, 33)])

MON = createNstringsNwordsClass('SMALL/MON.BIN', [], [WordPos(0x12, 0x1A, 150, 0x2C)])

TITLE_en = createNstringsNwordsClass('TITLE/TITLE.PRG', [], [WordPos(0xc42C, 0x18, 1, 0x20)])
TITLE_jp = createNstringsNwordsClass('TITLE/TITLE.PRG', [], [WordPos(0xA58C, 0x18, 1, 0x20)])

INITBTL = createNstringsNwordsClass('BATTLE/INITBTL.PRG', [], [WordPos(0x131C, 0x18, 1, 0x20), WordPos(0x1440, 0x18, 1, 0x20)])

ITEMNAME = createNstringsNwordsClass('MENU/ITEMNAME.BIN', [], [WordPos(0x0, 0x18, 512)])

SL_Main_en = createNstringsNwordsClass('SLUS_010.40', [0x405CC], [WordPos(0x3C1F8, 0x18, 256, 0x34)])
SL_Main_jp = createNstringsNwordsClass('SLPS_023.77',[0x405CC], [WordPos(0x3C1F8, 0x18, 256, 0x34)])

NAMEDIC = createNstringsNwordsClass('MENU/NAMEDIC.BIN', [0x0])


FileLoadFuncNames = ['MENU5', 'NAMEDIC', 
                     'MENU9', 'MENUD', 'MENUE', 
                     'BATTLE', 'MON', 'TITLE', 'INITBTL',
                     'ITEMNAME', 'SL_Main']

FileLoad1Strs = ['NAMEDIC', 
                 'MENUD', 'MENUE', 
                 'TITLE', 'ITEMNAME']

def getNNClass(className: str) -> Tuple[Class_Nstrings, Class_Nstrings]:
    Class_en = None
    Class_jp = None
    
    if className in globals():
        Class_en = globals()[className]
        Class_jp = globals()[className]
        
    if Class_en is None:
        if f'{className}_en' in globals():
            Class_en = globals()[f'{className}_en']
        if Class_en is None:
            logging.warning(f'wrong function name {className}')
        
    if Class_jp is None:
        if f'{className}_jp' in globals():
            Class_jp = globals()[f'{className}_jp']
        if Class_jp is None:    
            logging.warning(f'wrong function name {className}')
    
    return Class_jp, Class_en

def makeNNstrings(fileSrc: Class_Nstrings, fileComment: Class_Nstrings):
    str_group = {}
    
    len_strings = len(fileSrc.strings)
    for idx0 in range(len_strings):
        len_str = fileSrc.strings[idx0].itemNums
        if 0 == len_str:
            continue
        
        texts = {}
        for idx1 in range(len_str):
            src = fileSrc.strings[idx0]._str[idx1]
            if not src: 
                continue
            
            comment = fileComment.strings[idx0]._str[idx1]
            singleRow = {}
            singleRow['string'] = src
            if comment:
                comment = comment.replace('☐', ' ')
                singleRow['@@localazy:comment:string'] = comment
            texts[f'{idx1:03}'] = singleRow
    
        str_group[f'str_{idx0}'] = texts
    
    len_words = len(fileSrc.words)
    for idx0 in range(len_words):
        len_str = fileSrc.words[idx0].wordNums
        if 0 == len_str:
            continue
        
        texts = {}
        for idx1 in range(len_str):
            src = fileSrc.words[idx0]._str[idx1]
            if not src: 
                continue
            
            comment = fileComment.words[idx0]._str[idx1]
            singleRow = {}
            singleRow['string'] = src
            if comment:
                singleRow['@@localazy:comment:string'] = comment
            texts[f'{idx1:03}'] = singleRow
    
        str_group[f'word_{idx0}'] = texts
        
    return str_group

