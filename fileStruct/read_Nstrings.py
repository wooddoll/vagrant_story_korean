from typing import Union, List
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from fileStruct.readStrFile import ReadStrings


def createNstringsClass(FileName: str, NstringPtrs: List[int]):
    class Class_Nstrings(): 
        def __init__(self, input_path: str = '') -> None:
            self.buffer = bytes()
            self.strings: List[ReadStrings] = []

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

        def cvtByte2Str(self, table: convert_by_TBL):
            for strings in self.strings:
                strings.cvtByte2Str(table)

        def unpackData(self, input_path: str):
            with open(input_path, 'rb') as file:
                self.buffer = file.read()

                self.strings.clear()
                for ptr in NstringPtrs:
                    self.strings.append(ReadStrings(self.buffer[ptr:]))

        def packData(self, output_path: str):
            with open(output_path, 'wb') as file:
                file.write(self.buffer)
                
                for idx in range(len(NstringPtrs)):
                    byteData = self.strings[idx].packData()
                    if byteData is not None:
                        file.seek(NstringPtrs[idx])
                        file.write(byteData)

    return Class_Nstrings



jpStringPtrs = [0x5f9c, 0x5fc8, 0x611c, 0x6320, 0x671c, 0x6850, 0x6ca8, 0x6d00, 0x6e6c]
MENU9_PRG_jp = createNstringsClass('MENU/MENU9.PRG', jpStringPtrs)

enStringPtrs = [0x5d20, 0x5d64, 0x5ee4, 0x61bc, 0x67dc, 0x6a00, 0x6d98, 0x6e0c, 0x6fdc]
MENU9_PRG_en = createNstringsClass('MENU/MENU9.PRG', enStringPtrs)


def read_MENU9():
    MENU9_jp = MENU9_PRG_jp(PATH_JPN_VARGRANTSTORY)
    MENU9_jp.cvtByte2Str(jpnTBL)
    
    MENU9_en = MENU9_PRG_en(PATH_USA_VARGRANTSTORY)
    MENU9_en.cvtByte2Str(usaTBL)
    
    jpntexts = {}
    for idx0, strings in enumerate(MENU9_jp.strings):
        lv1 = {}
        for idx1, text in enumerate(strings._str):
            lv1[f"{idx1:03}"] = text
        jpntexts[f"{idx0:02}"] = lv1
    

    usatexts = {}
    for idx0, strings in enumerate(MENU9_en.strings):
        lv1 = {}
        for idx1, text in enumerate(strings._str):
            lv1[f"{idx1:03}"] = text
        usatexts[f"{idx0:02}"] = lv1

    jpntexts = {}
    for k0, v1 in jpntexts.items():
        texts = {}
        for k1, v2 in v1.items():
            single = { 'string': v2, '@@localazy:comment:string': usatexts[k0][k1] }
            texts[k1] = single
        jpntexts[k0] = texts
    
    with open(f'work/strings/MENU_MENU9_ja.json', 'w', encoding='utf-8') as f:
        json.dump(jpntexts, f, indent=2, ensure_ascii=False)
  