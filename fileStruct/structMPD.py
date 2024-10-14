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
import json
from fileStruct.readStrFile import ReadStrings
from fileStruct.scriptOPcodes import ScriptOpcodes

class SectionBase:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = None

        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        if self.buffer is None:
            return 0

        return len(self.buffer)
    
    def unpackData(self, buffer: bytes):
        self.buffer = bytearray(buffer) if buffer is not None else None

    def packData(self):
        return self.buffer

class TreasureSection:
    ptrWeaponName = 0x94
    
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = None
        self.name_str = ''
        self.name_byte = bytes()

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

    def cvtByte2Str(self, table: convert_by_TBL):
        self.name_str = table.cvtBytes_str(self.name_byte)
        
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.name_byte = table.cvtStr_Bytes(self.name_str)
            
    def packData(self):
        if self.buffer is None:
            return

        byte_stream = io.BytesIO(self.buffer)
        byte_stream.seek(self.ptrWeaponName)
        if 0x18 < len(self.name_byte):
            logging.critical(f"WeaponName: {self.name_str} is too long. max (24byte.)")
            self.name_byte = self.name_byte[:0x18]
        byte_stream.write(self.name_byte)
        
        return self.buffer

class DialogText:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.strings = ReadStrings()
        self.strings_byte = self.strings._byte
        self.strings_str = self.strings._str
        self.sectionSize = 0
        
        if buffer is not None:
            self.unpackData(buffer)
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.strings.cvtStr2Byte(table)
        self.strings_byte = self.strings._byte
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)
        self.strings_str = self.strings._str
    
    def unpackData(self, buffer: bytes):
        self.sectionSize = len(buffer)
        
        self.strings.unpackData(buffer)
        self.strings_byte = self.strings._byte
    
    def __len__(self):
        return self.sectionSize
    
    def packData(self):
        if 0 >= len(self.strings):
            return None

        sumBytes = 2*self.strings.itemNums
        for text in self.strings_byte:
            sumBytes += len(text)
        sumBytes_pad = ((sumBytes+3)//4)*4
        padding = sumBytes_pad - sumBytes
        
        if self.sectionSize < sumBytes_pad:
            logging.warning(f"check the dialogs length, size overflowed; privious({self.sectionSize}) < current({sumBytes_pad})")
        self.sectionSize = sumBytes_pad
        
        if sumBytes_pad == 0:
            return bytes()
        
        data = self.strings.packData()
        return data + b'\x00'*padding

class ScriptSection:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.header = []
        self.scriptOpcodes   = ScriptOpcodes()
        self.dialogText      = DialogText()
        self.unknownSection1 = SectionBase()
        self.unknownSection2 = SectionBase()

        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        return self.header[0] if self.header else 0

    def cvtStr2Byte(self, table: convert_by_TBL):
        self.dialogText.cvtStr2Byte(table)

    def updateOpcode(self):
        for idx, code in enumerate(self.scriptOpcodes.opcodes):
            if code.Op == 0x11:
                text = self.dialogText.strings_str[ code.Args[1] ]
                code.Note = text
                
                rows, cols = dialog.checkSize(text)
                
                for _idx in reversed(range(idx)):
                    _code = self.scriptOpcodes.opcodes[_idx]
                    if _code.Op == 0x10:
                        w = _code.Args[5]
                        h = _code.Args[6]
                        if w < cols or h < rows:
                            logging.warning(f'dialog text is too long. box_w({w})<text_w({cols}), box_h({h})<text_h({rows})')
                        break
                    
    def cvtByte2Str(self, table: convert_by_TBL):
        self.dialogText.cvtByte2Str(table)
        self.updateOpcode()    
                
    def unpackData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        self.header = readHeader(byte_stream, 8, 2)
        
        poses = [16, self.header[1], self.header[2], self.header[3]]
        sizes = [poses[1]-poses[0], poses[2]-poses[1], poses[3]-poses[2], self.header[0]-poses[3]]
        logging.debug(f"Script / opcode:{sizes[0]}, dialog:{sizes[1]}, unknown1:{sizes[2]}, unknown2:{sizes[3]}")
        
        sections = [self.scriptOpcodes, self.dialogText, self.unknownSection1, self.unknownSection2]
        for idx in range(4):
            if sizes[idx] == 0: continue
            byte_stream.seek(poses[idx])
            sections[idx].unpackData(byte_stream.read(sizes[idx]))

    def packData(self):
        if not self.header:
            return None

        poses = [16]
        sizes = []
        sections = [self.scriptOpcodes, self.dialogText, self.unknownSection1, self.unknownSection2]

        dialogText = self.dialogText.packData()
        
        for idx in range(4):
            sizes.append(len(sections[idx]))
            if idx > 0:
                poses.append(poses[idx-1] + sizes[idx-1])
        sumSizes = sum(sizes) + 16
        logging.debug(f"Script / opcode:{sizes[0]}, dialog:{sizes[1]}, unknown1:{sizes[2]}, unknown2:{sizes[3]}")
        
        if sumSizes > self.header[0]:
            logging.warning(f"check the ScriptSection size, size overflowed({self.header[0]} < {sumSizes})")

        self.header[0] = sumSizes
        self.header[1] = poses[1]
        self.header[2] = poses[2]
        self.header[3] = poses[3]
        
        byte_stream = io.BytesIO()
        for header in self.header:
            byte_stream.write(bytes2(header))
            
        for idx in range(4):
            data = dialogText if idx == 1 else sections[idx].packData()
            if data is not None:
                byte_stream.seek(poses[idx])
                byte_stream.write(data)

        return byte_stream.getvalue()

class MPDstruct:
    def __init__(self, input_path:str = '') -> None:
        self.header = []
        self.roomSection        = SectionBase()
        self.clearedSection     = SectionBase()
        self.scriptSection      = ScriptSection()
        self.doorSection        = SectionBase()
        self.enemySection       = SectionBase()
        self.treasureSection    = TreasureSection()

        if input_path:
            self.unpackData(input_path)

    def __len__(self):
        if not self.header:
            return 0
        
        bufferSize = 0
        for idx in range(1, 12, 2):
            bufferSize += self.header[idx]
            
        return bufferSize
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.scriptSection.cvtStr2Byte(table)
        self.treasureSection.cvtStr2Byte(table)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.scriptSection.cvtByte2Str(table)
        self.treasureSection.cvtByte2Str(table)
        
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            
            filesize = len(buffer)
            lbaSize = ((filesize + 2047)//2048)*2048
            
            logging.info(f"{Path(input_path).stem}: The free space in LBA is {lbaSize - filesize} bytes.")
            byte_stream = io.BytesIO(buffer)

            self.header = readHeader(byte_stream, 12, 4)
            poses = [self.header[0], self.header[2], self.header[4], self.header[6], self.header[8], self.header[10]]
            sizes = [self.header[1], self.header[3], self.header[5], self.header[7], self.header[9], self.header[11]]
            logging.debug(f"MDP / room:{self.header[1]}, cleared:{self.header[3]}, script:{self.header[5]}, door:{self.header[7]}, enemy:{self.header[9]}, treasure:{self.header[1]}")
            sections = [self.roomSection, self.clearedSection, self.scriptSection, self.doorSection, self.enemySection, self.treasureSection]

            for idx in range(6):
                if sizes[idx] == 0: continue
                byte_stream.seek(poses[idx])
                sections[idx].unpackData(byte_stream.read(sizes[idx]))

    def packData(self, output_path:str):
        if not self.header:
            return
        
        fileSize = len(self)
        poses = [self.header[0]]
        sizes = []
        
        scriptSection = self.scriptSection.packData()
        
        sections = [self.roomSection, self.clearedSection, self.scriptSection, self.doorSection, self.enemySection, self.treasureSection]

        for idx in range(6):
            sizes.append(len(sections[idx]))
            if idx > 0:
                poses.append(poses[idx-1] + sizes[idx-1])
        sumSizes = sum(sizes)
        logging.debug(f"MDP / room:{self.header[1]}, cleared:{self.header[3]}, script:{self.header[5]}, door:{self.header[7]}, enemy:{self.header[9]}, treasure:{self.header[1]}")
        
        prevScriptSectionSize = self.header[6] - self.header[4]
        writeSize = len(scriptSection) if scriptSection is not None else 0
        if prevScriptSectionSize < writeSize:
            logging.warning(f"check the section size, size overflowed({prevScriptSectionSize} < {writeSize})")

        for idx in range(0, 12, 2):
            self.header[idx]   = poses[idx//2]
            self.header[idx+1] = sizes[idx//2]
            
        if sumSizes > fileSize:
            prev = math.ceil(fileSize / 2048) * 2048
            curr = math.ceil(sumSizes / 2048) * 2048
            if curr > prev:
                logging.critical(f"check the file size, LBA overflowed({fileSize} < {sumSizes})")
            else:
                logging.warning(f"check the file size, size overflowed({fileSize} < {sumSizes})")

        with open(output_path, 'wb') as file:
            for value in self.header:
                file.write(bytes4(value))

            for idx in range(6):
                data = scriptSection if idx == 2 else sections[idx].packData()
                if data is not None:
                    file.seek(poses[idx])
                    file.write(data)

#mpd = MPDstruct()
#mpd.unpackData("D:/Projects/vagrant_story_korean/font/test/jpn/MAP001.MPD")
#mpd.packData("D:/Projects/vagrant_story_korean/MAP001.MPD")




def exportTextFromMPD(mpd: MPDstruct, fontTable: convert_by_TBL):
    mpd.scriptSection.dialogText.cvtByte2Str(fontTable)
    dialogLists = []
    mpd.scriptSection.dialogText.cvtByte2Str(fontTable)
    for idx in range(mpd.scriptSection.dialogText.strings.itemNums):
        text = mpd.scriptSection.dialogText.strings_str[idx]
        rows, cols = dialog.checkSize(text)
        singleRow = {}
        if cols == 1:
            text = dialog.vertical2flat(text)
        singleRow['string'] = text
        #singleRow['@@localazy:comment:string'] = ''
        singleRow['@@localazy:limit:string'] = str((rows, cols))
        
        
        dialogLists.append(singleRow)
    
    return dialogLists

def makeMPDtexts(folder_path: str, fontTable: convert_by_TBL, out_path: str):
    extension = '*.MPD'
    file_list = list(Path(folder_path).glob(extension))

    dialogLists = {}
    
    keyTBL = dialog.ReplaceKeyword("work/VSDictTable.tbl")

    for filepath in tqdm(file_list, desc="Processing"):
        mpd = MPDstruct(str(filepath))

        texts = exportTextFromMPD(mpd, fontTable)
        if texts:
            dialogLists[filepath.stem] = texts
            #for idx in range(len(texts)):
            #    dialogLists[f'{filepath.stem}[{idx}]'] = texts[idx]

    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(dialogLists, f, indent=2, ensure_ascii=False)
        #df = pd.DataFrame(dialogLists, columns=['File', 'Index', 'rows', 'cols', 'Original'])#, 'Translated'])
        #df.to_csv(out_path, index=False, encoding='utf-8')
        #df.to_excel(out_path, index=False)
    
    return dialogLists

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
            mpd.scriptSection.dialogText.cvtStr2Byte(jpnTBL)

        outpath = os.path.join(output_folder_path, f"{filename}.MPD")
        mpd.packData(outpath)

#dialogLists = readExelDialog('VSdialog.csv')
#importDialog2MPD(dialogLists)