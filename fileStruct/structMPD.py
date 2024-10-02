from typing import Union
import io
import os
import logging
import math
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *
from tqdm import tqdm
from font import dialog
import pandas as pd
from fileStruct.readNameFile import ReadNames
from fileStruct.readStrFile import ReadStrings

class SectionBase():
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = None

        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        return len(self.buffer) if self.buffer is not None else 0
    
    def unpackData(self, buffer: bytes):
        self.buffer = bytearray(buffer) if buffer is not None else None

    def packData(self):
        return self.buffer

class TreasureSection():
    ptrWeaponName = 0x94
    
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = None
        self.name_str = ''
        self.name_byte = None

        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        return len(self.buffer) if self.buffer is not None else 0
    
    def unpackData(self, buffer: bytes):
        if buffer is not None:
            self.buffer = bytearray(buffer)
        else:
            return
        
        byte_stream = io.BytesIO(self.buffer)
        byte_stream.seek(self.ptrWeaponName)
        data = byte_stream.read(0x18)
        self.name_byte = trimTextBytes(data)

    def cvtByte2Name(self, table: convert_by_TBL):
        self.name_str = table.cvtBytes_str(self.name_byte)
        
    def cvtName2Byte(self, table: convert_by_TBL):
        self.name_byte = table.cvtStr_Bytes(self.name_str, True)
            
    def packData(self):
        if self.buffer is None:
            return

        byte_stream = io.BytesIO(self.buffer)
        byte_stream.seek(self.name_byte)
        byte_stream.write(0x18)
        
        return self.buffer

class DialogText():
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.strings = ReadStrings()
        self.strings_byte = self.strings._byte
        self.strings_str = self.strings._str
        
        if buffer is not None:
            self.unpackData(buffer)
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.strings.cvtStr2Byte(table)
        self.strings_byte = self.strings._byte
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)
        self.strings_str = self.strings._str
    
    def unpackData(self, buffer: bytes):
        self.strings.unpackData(buffer)
        self.strings_byte = self.strings._byte
        
    def packData(self):
        if self.strings.buffer is None:
            return None
        
        preSize = len(self.strings.buffer) - 2*self.strings.itemNums
        sumBytes = 0
        for text in self.strings_byte:
            sumBytes += len(text)
        if preSize < sumBytes:
            logging.warning(f"check the dialogs length, size overflowed; privious({preSize}) < current({sumBytes})")
        
        return self.strings.packData()
  
class DialogText2(SectionBase):
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = None
        self.dialogBytes = []

        if buffer is not None:
            self.unpackData(buffer)

    def readHeader(self):
        if self.buffer is None:
            return [], []
        
        byte_stream = io.BytesIO(self.buffer)
        maxSize = len(self.buffer)

        numDialogs = int2(byte_stream.read(2))
        ptrText = [2*numDialogs]
        for i in range(numDialogs - 1):
            ptrText.append(2*int2(byte_stream.read(2)))

        lenText = []
        for i in range(numDialogs - 1):
            lenText.append(ptrText[i+1] - ptrText[i])
        lenText.append(maxSize - ptrText[-1])

        return ptrText, lenText
    
    def checkDialog(self):
        for idx, text in enumerate(self.dialogBytes):
            endpos = -1
            for i, c in enumerate(text):
                if c == 0xE7:
                    endpos = i + 1
                    break
            if endpos == -1:
                text.extend(bytes1(0xE7))
                endpos = len(text)
            text = text[:endpos]
            size = len(text)
            if size%2 == 1:
                text.extend(bytes1(0xEB))

            self.dialogBytes[idx] = text

    def unpackData(self, buffer: bytes):
        if buffer is not None:
            self.buffer = bytearray(buffer)
        else:
            return
        
        ptrText, lenText = self.readHeader()

        byte_stream = io.BytesIO(buffer)

        self.dialogBytes = []
        for pos, size in zip(ptrText, lenText):
            if size == 0:
                continue

            byte_stream.seek(pos)

            text = bytearray(byte_stream.read(1))
            while(text[-1] != 0xE7):
                text.extend(byte_stream.read(1))

            if len(text) > size:
                logging.critical(f"check the text end mark(E7), size overflowed({len(text)} > {size})")
            
            self.dialogBytes.append(text)

    def packData(self):
        if self.buffer is None:
            return None
        
        self.checkDialog()

        ptrText, lenText = self.readHeader()
        preSize = len(self.buffer) - ptrText[0]

        numTexts = len(self.dialogBytes)
        if ptrText[0]//2 != numTexts:
            logging.critical(f"check the number of dialogs, size different; privious({ptrText[0]//2}) != current({numTexts})")

        ptrText.append(-1)
        for idx, text in enumerate(self.dialogBytes):
            lenText[idx] = len(text)
            ptrText[idx+1] = ptrText[idx] + lenText[idx]
        sumBytes = sum(lenText)

        if preSize < sumBytes:
            logging.warning(f"check the dialogs length, size overflowed; privious({preSize}) < current({sumBytes})")

        byte_stream = io.BytesIO(self.buffer)
        for idx in range(numTexts):
            byte_stream.write(bytes2(ptrText[idx]//2))

        for text in self.dialogBytes:
            byte_stream.write(text)

        return byte_stream.getbuffer()
    
class ScriptSection(SectionBase):
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = bytearray(buffer) if buffer is not None else None

        self.scriptOpcodes      = SectionBase()
        self.dialogText         = DialogText()
        self.unknownSection1    = SectionBase()
        self.unknownSection2    = SectionBase()

        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        if buffer is not None:
            self.buffer = bytearray(buffer)
        else:
            return
        
        byte_stream = io.BytesIO(self.buffer)
        header = readHeader(byte_stream, 8, 2)
        
        poses = [16, header[1], header[2], header[3]]
        sizes = [poses[1]-poses[0], poses[2]-poses[1], poses[3]-poses[2], header[0]-poses[3]]

        sections = [self.scriptOpcodes, self.dialogText, self.unknownSection1, self.unknownSection2]
        for idx in range(4):
            if sizes[idx] == 0: continue
            byte_stream.seek(poses[idx])
            sections[idx].unpackData(byte_stream.read(sizes[idx]))

    def packData(self):
        if self.buffer is None:
            return None

        byte_stream = io.BytesIO(self.buffer)
        header = readHeader(byte_stream, 8, 2)
        poses = [16]
        sizes = []
        sections = [self.scriptOpcodes, self.dialogText, self.unknownSection1, self.unknownSection2]

        for idx in range(4):
            sizes.append(len(sections[idx]))
            if idx > 0:
                poses.append(poses[idx-1] + sizes[idx-1])
        sumSizes = sum(sizes) + 16

        if sumSizes > header[0]:
            logging.warning(f"check the ScriptSection size, size overflowed({sumSizes} > {header[0]})")

        byte_stream.seek(0)
        byte_stream.write(bytes2(sumSizes))
        byte_stream.write(bytes2(poses[1]))
        byte_stream.write(bytes2(poses[2]))
        byte_stream.write(bytes2(poses[3]))
        byte_stream.write(bytes2(header[4]))
        byte_stream.write(bytes2(header[5]))
        byte_stream.write(bytes2(header[6]))
        byte_stream.write(bytes2(header[7]))

        for idx in range(4):
            data = sections[idx].packData()
            if data is not None:
                byte_stream.seek(poses[idx])
                byte_stream.write(data)

        return byte_stream.getbuffer()

class MPDstruct():
    def __init__(self, input_path:str = '') -> None:
        self.buffer = None
        self.roomSection        = SectionBase()
        self.clearedSection     = SectionBase()
        self.scriptSection      = ScriptSection()
        self.doorSection        = SectionBase()
        self.enemySection       = SectionBase()
        self.treasureSection    = TreasureSection()

        if input_path:
            self.unpackData(input_path)

    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = bytearray(file.read())
            
            filesize = len(self.buffer)
            lbaSize = (filesize//2048)*2048
            if filesize > lbaSize:
                lbaSize += 2048
            
            logging.info(f"{Path(input_path).stem}: The free space in LBA is {lbaSize - filesize} bytes.")
            byte_stream = io.BytesIO(self.buffer)

            header = readHeader(byte_stream, 12, 4)
            poses = [header[0], header[2], header[4], header[6], header[8], header[10]]
            sizes = [header[1], header[3], header[5], header[7], header[9], header[11]]

            sections = [self.roomSection, self.clearedSection, self.scriptSection, self.doorSection, self.enemySection, self.treasureSection]

            for idx in range(6):
                if sizes[idx] == 0: continue
                byte_stream.seek(poses[idx])
                sections[idx].unpackData(byte_stream.read(sizes[idx]))

    def packData(self, output_path:str):
        if self.buffer is None:
            return
        
        fileSize = len(self.buffer)
        byte_stream = io.BytesIO(self.buffer)

        header = readHeader(byte_stream, 12, 4)
        poses = [header[0]]
        sizes = []
        
        sections = [self.roomSection, self.clearedSection, self.scriptSection, self.doorSection, self.enemySection, self.treasureSection]

        for idx in range(6):
            sizes.append(len(sections[idx]))
            if idx > 0:
                poses.append(poses[idx-1] + sizes[idx-1])
        sumSizes = sum(sizes)

        scriptSection = self.scriptSection.packData()
        maxScriptSectionSize = header[6] - header[4]
        writeSize = len(scriptSection) if scriptSection is not None else 0
        if writeSize > maxScriptSectionSize:
            logging.warning(f"check the section size, size overflowed({writeSize} > {maxScriptSectionSize})")

        if sumSizes > fileSize:
            prev = math.ceil(fileSize / 2048) * 2048
            curr = math.ceil(sumSizes / 2048) * 2048
            if curr > prev:
                logging.critical(f"check the file size, LBA overflowed({sumSizes} > {fileSize})")
            else:
                logging.warning(f"check the file size, size overflowed({sumSizes} > {fileSize})")

        with open(output_path, 'wb') as file:
            for idx in range(6):
                file.write(bytes4(poses[idx]))
                file.write(bytes4(sizes[idx]))

            for idx in range(6):
                data = scriptSection if idx == 2 else sections[idx].packData()
                if data is not None:
                    file.seek(poses[idx])
                    file.write(data)

#mpd = MPDstruct()
#mpd.unpackData("D:/Projects/vagrant_story_korean/font/test/jpn/MAP001.MPD")
#mpd.packData("D:/Projects/vagrant_story_korean/MAP001.MPD")




def exportTextFromMPD(mpd: MPDstruct, jpnTBL: convert_by_TBL):
    mpd.scriptSection.dialogText.cvtByte2Str(jpnTBL)
    dialogLists = []
    for idx, text in enumerate(mpd.scriptSection.dialogText.strings_str):
        rows, cols = dialog.checkSize(text)
        singleRow = []
        singleRow.append(idx)            
        singleRow.append(rows)
        singleRow.append(cols)
        if cols == 1:
            text = dialog.vertical2flat(text)
        singleRow.append(text)
        dialogLists.append(singleRow)
    
    return dialogLists

def makeMPDtexts(folder_path: str, fontTable: convert_by_TBL, out_path: str):
    extension = '*.MPD'
    file_list = list(Path(folder_path).glob(extension))

    dialogLists = []
    
    keyTBL = dialog.ReplaceKeyword("work/VSDictTable.tbl")

    for filepath in tqdm(file_list, desc="Processing"):
        mpd = MPDstruct(str(filepath))

        for idx, dialogBytes in enumerate(mpd.scriptSection.dialogText.dialogBytes):
            text = fontTable.cvtBytes_str(dialogBytes)
            rows, cols = dialog.checkSize(text)

            singleRow = []
            singleRow.append(filepath.stem)
            singleRow.append(idx)            
            singleRow.append(rows)
            singleRow.append(cols)

            if cols == 1:
                text = dialog.vertical2flat(text)

            singleRow.append(text)
            # TODO
            #knText = keyTBL.replace(text)
            #singleRow.append(knText)
            dialogLists.append(singleRow)

    df = pd.DataFrame(dialogLists, columns=['File', 'Index', 'rows', 'cols', 'Original'])#, 'Translated'])
    df.to_csv(out_path, index=False, encoding='utf-8')
    #df.to_excel(out_path, index=False)

#makeMPDtexts()

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