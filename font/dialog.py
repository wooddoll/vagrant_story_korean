from typing import Dict, Union, List
from pathlib import Path
import pandas as pd
import os
from copy import deepcopy
import logging
import yaml
from tqdm import tqdm
from font.makeTBL import readTBL
from utils import *

ITALIC_CHARICTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!?/,:+-"

class convert_by_TBLdummy():
    def __init__(self) -> None:
        pass
    def cvtByte2Str(self, bytesText: bytes) -> str:
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
                letter = f'{tmp:04X} '
            else:
                letter = f'{tmp:02X} '

            if letter is None:
                strText += f'«{tmp:04X}»'
            else:
                strText += letter

        return strText
  
class convert_by_TBL():
    def __init__(self, table: Union[str, dict]) -> None:
        if isinstance(table, str):
            self.fwd_tbl = readTBL(table)
        elif isinstance(table, dict):
            self.fwd_tbl = table
        else:
            logging.critical('table is not path or dict')

        self.duplicated = {}
        self.inv_tbl = {}
        for k, v in self.fwd_tbl.items():
            if len(v) != 1:
                continue
            
            pre = self.inv_tbl.get(v)
            if pre is not None:
                preV = pre[0]
                if len(pre) == 2:
                    preV = (preV << 8) | pre[1]
                self.duplicated[v] = [ preV, k ]
                    
            if k < 0xE5:
                self.inv_tbl[v] = [k]
            else:
                v1 = (k >> 8) & 0xFF
                v2 = k & 0xFF
                self.inv_tbl[v] = [v1, v2]
    
    def cvtByte2Str(self, bytesText: bytes) -> str:
        pos = 0
        length = len(bytesText)

        strText = ''
        while(pos < length):
            letter = None
            tmp = bytesText[pos]
            pos += 1
            
            if tmp == 0xE7:
                break
            elif tmp == 0xE8:
                strText += '↵'
                continue
            elif tmp >= 0xE5:
                if pos < length:
                    tmp = (tmp << 8) | bytesText[pos]
                    pos += 1
                letter = self.fwd_tbl.get(tmp)
                dub = self.duplicated.get(letter)
                if dub is not None and tmp == dub[1]:
                    letter = f'[{letter}]'
            else:
                letter = self.fwd_tbl.get(tmp)

            if letter is None:
                strText += f'«{tmp:02X}»' if tmp <= 0xFF else f'«{tmp:04X}»'
            else:
                strText += letter

        strText = strText.replace('][', '')
        
        return strText

    def cvtStr2Byte(self, strText: str) -> bytearray:
        length = len(strText)
        pos = 0
        byteText = bytearray()
        italic = False
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
                
                len_tmp = len(tmp)
                for i in range(0, len_tmp, 2):
                    byteText.append(int(tmp[i:i+2], 16))
                continue
            elif letter in ['↵', '\n', '\r', '\r\n']:
                byteText.append(0xE8)
                continue
            elif letter == '[':
                italic = True
                continue
            elif letter == ']':
                italic = False
                continue
            else:
                ret = self.inv_tbl.get(letter)
                dub = self.duplicated.get(letter)
                if dub is not None:
                    dubV = dub[1] if italic else dub[0]
                    if dubV < 0xE5:
                        ret = [dubV]
                    else:
                        ret = [ dubV>>8, dubV&0xFF ]

                if ret is not None:
                    byteText.extend(ret)
                else:
                    logging.critical(f"'{letter}' is invalid.")
                    byteText.append(0xF7)
                    byteText.append(0x07)
        
        if byteText and byteText[-1] != 0xE7:
            byteText.append(0xE7)
        return byteText

def getControl(text: str):
    if len(text) < 6:
        return '', text

    if text[0] == '«':
        return text[:6], text[6:]
    else:
        return '', text

def checkHead(text: str):
    head = ''
    _h, retTxt = getControl(text)
    while _h:
        if _h[1] == 'F' and _h[2] == 'A':
            retTxt = _h + retTxt
            break
        else:
            head += _h
            _h, retTxt = getControl(retTxt)

    return head, retTxt

def checkFirstSpace(text: str):
    length = len(text)
    space = 0
    pos = 0
    while pos < length:
        letter = text[pos]
        pos += 1
        if letter == ' ':
            space += 6
        elif letter == '☐':
            space += 12
        elif letter == '«':
            temp = []
            while letter != '»':
                letter = text[pos]
                pos += 1
                if letter != '»':
                    temp.append(letter)

            if len(temp) == 4:
                tmp0 = temp[0]+temp[1]
                tmp1 = temp[2]+temp[3]
                if tmp0.upper() == 'FA':
                    num = int(tmp1, 16)
                    if num > 0x7F:
                        num -= 0x100
                    space += num
                    break
        else:
            pos -= 1
            break
    return space, text[pos:]



def checkFirst(text: str) -> List[int]:
    ret = []
    lines = text.split('↵')
    for line in lines:
        _cols, last = checkFirstSpace(line)
        ret.append(_cols)
    sp0 = ret[0]
    AllSame = True
    for i in range(1, len(ret)):
        if sp0 != ret[i]:
            AllSame = False
            break
    if AllSame:
        return [sp0]
    return ret

def checkLineLength(text: str):
    length = len(text)
    pos = 0
    cols = 0
    halfCharictor = False
    while pos < length:
        letter = text[pos]
        pos += 1
        if letter == '[':
            halfCharictor = True
        elif letter == ']':
            halfCharictor = False
        elif letter == '«':
            TypeCtl = text[pos:pos+2]
            pos += 2
            if text[pos] == '»':
                pos += 1
                continue

            Value = text[pos:pos+2]
            pos += 2
            if TypeCtl.upper() == 'FA':
                num = int(Value, 16)
                if num > 0x7F:
                    num -= 0x100
                cols += num
            if text[pos] == '»':
                pos += 1
                continue
            else:
                logging.critical('control word «» incorrect!!')
        else:
            if letter in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!?/,:+-":
                cols += 6 if halfCharictor else 12
            elif letter in " abcdefghijklmnopqrstuvwxyz⌊⌋\'\".;「」『』()":
                cols += 6
            else:
                cols += 12
    
    return (cols + 5) // 12

def decomposeText(text: str):
    text0 = deepcopy(text)
    
    head, text1 = checkHead(text0)    
    lines = text1.split('↵')
    rows = len(lines)
    
    sps = []
    rawes = []
    cols = []
    for line in lines:
        space, raw = checkFirstSpace(line)
        col = checkLineLength(raw)
        sps.append(space)
        rawes.append(raw)
        cols.append(col)
    
    sp0 = sps[0]
    AllSame = True
    for i in range(1, len(sps)):
        if sp0 != sps[i]:
            AllSame = False
            break
    if AllSame:
        sps = [sp0]
    
    return head, sps, (rows, max(cols)), rawes
    
def checkSize(text: str):
    rows = 1
    cols = 1
    _cols = 0

    lines = text.split('↵')
    rows = len(lines)
    for line in lines:
        _cols = checkLineLength(line)
        cols = max(cols, _cols)
    return rows, cols
    
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
        elif letter in ['↵', '\n']:
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
        elif letter in ['↵', '\n']:
            if text[pos-1] in ['↵', '\n']:
                flatText += ' '
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
            if letter != ' ':
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
            self.table[idx].append(leftTable.cvtStr2Byte(left))
            right = self.table[idx][1]
            self.table[idx].append(rightTable.cvtStr2Byte(right))
    
    def replace(self, text:str):
        outText = deepcopy(text)
        for items in self.table:
            outText = outText.replace(items[0], items[1])
        return outText

class FindKeyword():
    def __init__(self, path_table: str) -> None:
        self.table = []
        
        with open(path_table, "rt", encoding='utf-8') as file:
            lines = file.readlines()
            
            for line in lines:
                if line[0] in ['#', ' ', '\n', '\r']: continue
                txts = line.split(' ')                
                text = ' '.join(txts[1:])
                row = []
                row.append(text)
                row.append(text)
                self.table.append(row)
    
    def expandBytes(self, leftTable: convert_by_TBL, rightTable: convert_by_TBL):
        for idx in range(len(self.table)):
            left = self.table[idx][0]
            self.table[idx].append(leftTable.cvtStr2Byte(left))
            right = self.table[idx][1]
            self.table[idx].append(rightTable.cvtStr2Byte(right))
    
    def replace(self, text:str):
        outText = deepcopy(text)
        for items in self.table:
            outText = outText.replace(items[0], items[1])
        return outText


class Find_Word():
    def __init__(self) -> None:
        dictTable = FindKeyword("work/VSwords_en.txt")
        self.jpbtbl = convert_by_TBL("font/jpn.tbl")
        self.usatbl = convert_by_TBL("font/usa.tbl")
        dictTable.expandBytes(self.jpbtbl, self.usatbl)
        self.dictTable = dictTable.table

    def findWord_in_Bytes(self, data: bytes, word: bytes):
        word0 = word + b'\xE7'
        search_len = len(word0)
        results = []
        for i in range(len(data) - search_len + 1):
            if data[i:i + search_len] == word0:
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
            if str(filepath.suffix) in ['.MPD', '.ARM', '.ZND', '.ZUD', '.SHP', '.SEQ', '.WEP', '.WAV', '.TIM', '.XA']:
                continue
            
            relative_path = filepath.relative_to(folder_path)
            if str(relative_path.parent) in [ "SOUND" ]: 
                continue
            
            detected = self.find_Word_in_File(str(filepath))

            if detected:
                wordinfiles.append([str(relative_path), detected])

        with open(outPath, 'w', encoding='utf-8') as file:
            yaml.dump(wordinfiles, file, encoding='utf-8')

class Find_Word2():
    def __init__(self) -> None:
        self.jpbtbl = convert_by_TBL("font/font12jp.tbl")
        self.wordTable = [['クイックマニュアル', bytes()] ]
        
        for word in self.wordTable:
            word[1] = self.jpbtbl.cvtStr2Byte(word[0])
        

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
        for item in self.wordTable:
            poses = self.findWord_in_Bytes(fileBuffer, item[1])

            if poses:
                wordinfile.append([item[0], poses])
        
        return wordinfile
    
    def find_in_folder(self, input_path: str, outPath: str):
        folder_path = Path(input_path)
        file_list = [file for file in folder_path.rglob('*') if file.is_file()]

        wordinfiles = []
        for filepath in tqdm(file_list, desc="Processing"):
            if str(filepath.suffix) in ['.MPD', '.ARM', '.ZND', '.ZUD', '.SHP', '.SEQ', '.WEP', '.WAV', '.TIM', '.XA']:
                continue
            
            relative_path = filepath.relative_to(folder_path)
            if str(relative_path.parent) in [ "SOUND" ]: 
                continue
            
            detected = self.find_Word_in_File(str(filepath))

            if detected:
                wordinfiles.append([str(relative_path), detected])

        with open(outPath, 'w', encoding='utf-8') as file:
            yaml.dump(wordinfiles, file, encoding='utf-8')


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


