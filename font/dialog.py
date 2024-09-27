from typing import Dict, Union, List
from pathlib import Path
import pandas as pd
import os
from copy import deepcopy
import logging
import yaml
from tqdm import tqdm
from fileStruct.structMPD import MPDstruct
from font.makeTBL import readTBL

class convert_by_TBL():
    def __init__(self, table: Union[str, dict]) -> None:
        if isinstance(table, str):
            self.fwd_tbl = readTBL(table)
        elif isinstance(table, dict):
            self.fwd_tbl = table
        else:
            logging.critical('table is not path or dict')

        self.inv_tbl = {}
        for k, v in self.fwd_tbl.items():
            if len(v) != 1:
                continue
            
            if k < 0xE5:
                self.inv_tbl[v] = [k]
            else:
                v1 = (k >> 8) & 0xFF
                v2 = k & 0xFF
                self.inv_tbl[v] = [v1, v2]

    def cvtBytes_str(self, bytesText: bytes) -> str:
        pos = 0
        length = len(bytesText)

        strText = ''
        while(pos < length):
            letter = None
            tmp = bytesText[pos]
            pos += 1
            
            if tmp == 0xE8:
                strText += '↵'
                continue
            elif tmp == 0xE7:
                break
            elif tmp >= 0xE5:
                tmp = (tmp << 8) | bytesText[pos]
                pos += 1
                letter = self.fwd_tbl.get(tmp)
            else:
                letter = self.fwd_tbl.get(tmp)

            if letter is None:
                strText += f'«{tmp:04X}»'
            else:
                strText += letter

        return strText

    def cvtStr_Bytes(self, strText: str) -> bytearray:
        length = len(strText)
        pos = 0
        byteText = bytearray()
        while pos < length:
            tmp = ''
            letter = strText[pos]
            pos += 1
            if letter == '«':
                tmp = ''
                while letter != '»':
                    letter = strText[pos]
                    pos += 1
                    if letter == '»': break
                    tmp += letter
                byteText.append(int(tmp[:2], 16))
                byteText.append(int(tmp[2:], 16))
                continue
            elif letter == '↵':
                byteText.append(0xe8)
                continue
            else:
                ret = self.inv_tbl.get(letter)
                if ret is not None:
                    byteText.extend(ret)

        return byteText

def checkSize(text: str):
    rows = 1
    cols = 1
    _cols = 0

    length = len(text)
    pos = 0
    while pos < length:
        letter = text[pos]
        pos += 1
        if letter == '«':
            while letter != '»':
                letter = text[pos]
                pos += 1
            continue
        elif letter == '↵':
            rows += 1
            _cols = 0
        else:
            _cols += 1
            cols = max(cols, _cols)
    return rows, cols

def vertical2flat(text: str):
    length = len(text)
    pos = 0
    flatText = ''
    while pos < length:
        tmp = ''
        letter = text[pos]
        pos += 1
        if letter == '«':
            tmp = '«'
            while letter != '»':
                letter = text[pos]
                tmp += letter
                pos += 1
            flatText += tmp
            continue
        elif letter == '↵':
            continue
        else:
            flatText += letter

    return flatText

def flat2vertical(text: str):
    length = len(text)
    pos = 0
    verticalText = ''
    while pos < length:
        tmp = ''
        letter = text[pos]
        pos += 1
        if letter == '«':
            tmp = '«'
            while letter != '»':
                letter = text[pos]
                tmp += letter
                pos += 1
            verticalText += tmp
            continue
        elif letter == '↵':
            verticalText += '↵'
        else:
            verticalText += letter
            verticalText += '↵'

    if verticalText[-1] == '↵':
        verticalText = verticalText[:-1]
    return verticalText

def readDictTable(path: str) -> List[List[str]]:
    lines = []
    with open(path, 'rt', encoding='utf-8') as file:
        lines = file.readlines()
    
    table = []
    for line in lines:
        pos = line.find('=')
        if pos == -1: continue
        txts = line.split('=')
        
        table.append([txts[0], txts[1][:-1]])
    
    return table

class ReplaceKeyword():
    def __init__(self, table: Union[str, list]) -> None:
        if isinstance(table, str):
            self.table = readDictTable(table)
        elif isinstance(table, list):
            self.table = table
        else:
            logging.critical('table is not path or dict')
    
    def expandBytes(self, leftTable: convert_by_TBL, rightTable: convert_by_TBL):
        for idx in range(len(self.table)):
            left = self.table[idx][0]
            self.table[idx].append(leftTable.cvtStr_Bytes(left))
            right = self.table[idx][1]
            self.table[idx].append(rightTable.cvtStr_Bytes(right))
    
    def replace(self, text:str):
        outText = deepcopy(text)
        for items in self.table:
            outText = outText.replace(items[0], items[1])
        return outText



class Find_Word():
    def __init__(self) -> None:
        dictTable = ReplaceKeyword("work/VSDictTable.tbl")
        self.jpbtbl = convert_by_TBL("font/jpn.tbl")
        self.usatbl = convert_by_TBL("font/usa.tbl")
        dictTable.expandBytes(self.jpbtbl, self.usatbl)
        self.dictTable = dictTable.table

    def findWord_in_Bytes(self, data: bytes, word: bytes):
        search_len = len(word)
        results = []
        for i in range(len(data) - search_len + 1):
            if data[i:i + search_len] == word:
                results.append(i)
    
        return results
    
    def find_Word_in_File(self, path: str):
        fileBuffer = None
        with open(path, 'rb') as file:
            fileBuffer = file.read()

        wordinfile = []
        for item in self.dictTable:
            poses = self.findWord_in_Bytes(fileBuffer, item[2])

            if poses:
                wordinfile.append([item[1], poses])
        
        return wordinfile
    
    def find_in_folder(self, input_path: str, outPath: str):
        folder_path = Path(input_path)
        file_list = [file for file in folder_path.rglob('*') if file.is_file()]

        wordinfiles = []
        for filepath in tqdm(file_list, desc="Processing"):
            if str(filepath.suffix) in ['.MPD', '.ARM', '.ZND', '.ZUD', '.SHP', '.SEQ', '.WEP', '.WAV', '.TIM']:
                continue
            
            relative_path = filepath.relative_to(folder_path)
            if str(relative_path.parent) in ["SOUND" ]: 
                continue
            
            detected = self.find_Word_in_File(str(filepath))

            if detected:
                wordinfiles.append([str(relative_path), detected])

        with open(outPath, 'w') as file:
            yaml.dump(wordinfiles, file, encoding='utf-8')


def exportTextFromMPD(mpd: MPDstruct, jpnTBL: convert_by_TBL):
    dialogLists = []
    for idx, dialogBytes in enumerate(mpd.scriptSection.dialogText.dialogBytes):
        text = jpnTBL.cvtBytes_str(dialogBytes)
        rows, cols = checkSize(text)
        singleRow = []
        singleRow.append(idx)            
        singleRow.append(rows)
        singleRow.append(cols)
        if cols == 1:
            text = vertical2flat(text)
        singleRow.append(text)
        dialogLists.append(singleRow)
    
    return dialogLists

def makeMPDtexts():
    folder_path = Path('D:/Projects/vagrant_story_korean/font/test/jpn')
    extension = '*.MPD'
    file_list = list(folder_path.glob(extension))

    dialogLists = []
    jpnTBL = convert_by_TBL("D:/Projects/vagrant_story_korean/font/jpn.tbl")
    keyTBL = ReplaceKeyword("VSDictTable.tbl")

    for filepath in tqdm(file_list, desc="Processing"):
        mpd = MPDstruct(str(filepath))

        for idx, dialogBytes in enumerate(mpd.scriptSection.dialogText.dialogBytes):
            text = jpnTBL.cvtBytes_str(dialogBytes)
            rows, cols = checkSize(text)

            singleRow = []
            singleRow.append(filepath.stem)
            singleRow.append(idx)            
            singleRow.append(rows)
            singleRow.append(cols)

            if cols == 1:
                text = vertical2flat(text)

            singleRow.append(text)
            # TODO
            knText = keyTBL.replace(text)
            singleRow.append(knText)
            #singleRow.append(text)
            dialogLists.append(singleRow)

    df = pd.DataFrame(dialogLists, columns=['File', 'Index', 'rows', 'cols', 'Original', 'Translated'])
    df.to_csv('VSdialog.csv', index=False, encoding='utf-8')

#makeMPDtexts()

def readExelDialog(csv_path:str):
    dialogLists = {}
    df = pd.read_csv(csv_path)
    num_rows, num_columns = df.shape
    for idx in range(num_rows):
        File = df.iloc[idx]['File']
        Index = int(df.iloc[idx]['Index'])
        rows = int(df.iloc[idx]['rows'])
        cols = int(df.iloc[idx]['cols'])
        original = df.iloc[idx]['Original']
        translated = df.iloc[idx]['Translated']
        if cols == 1:
            translated = flat2vertical(translated)
        
        if dialogLists.get(File) is None:
            dialogLists[File] = []
        
        prevSize = len(dialogLists[File])
        if prevSize < (Index + 1):
            newlist = [''] * (Index + 1)
            for i in range(prevSize):
                newlist[i] = dialogLists[File][i]
            dialogLists[File] = newlist
        dialogLists[File][Index] = translated

    return dialogLists


def importDialog2MPD(original_folder_path: str, dialogLists, jpnTBL:convert_by_TBL, output_folder_path:str):
    #original_folder_path = Path('D:/Projects/vagrant_story_korean/font/test/jpn')
    #output_folder_path = 'D:/Projects/vagrant_story_korean/'
    # TODO replace to krTBL
    #jpnTBL = convert_by_TBL("D:/Projects/vagrant_story_korean/font/jpn.tbl")

    extension = '*.MPD'
    file_list = list(original_folder_path.glob(extension))
    for filepath in tqdm(file_list, desc="Processing"):
        mpd = MPDstruct(str(filepath))

        filename = filepath.stem
        texts = dialogLists.get(filename)
        if texts is not None:
            for idx, dialogBytes in enumerate(mpd.scriptSection.dialogText.dialogBytes):
                byteText = jpnTBL.cvtStr_Bytes(texts[idx])
                mpd.scriptSection.dialogText.dialogBytes[idx] = byteText

        outpath = os.path.join(output_folder_path, f"{filename}.MPD")
        mpd.packData(outpath)

#dialogLists = readExelDialog('VSdialog.csv')
#importDialog2MPD(dialogLists)