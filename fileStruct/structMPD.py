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

debugPos = ''

def findReverse(buffer: bytes, candidate: List[int], start: int):
    len_file = len(buffer)
    maxStr = len(candidate)
    ptr = candidate[start] - 4
    while 0 < ptr:
        idx0 = int2(buffer[ptr:ptr+2])
        pos = ptr+2
        if 0 < idx0 and idx0 <= maxStr:
            prev = idx0
            inc = True
            for i in range(idx0-1):
                    curr = int2(buffer[pos:pos+2])
                    pos += 2
                    if prev >= curr: 
                        inc = False
                        ptr -= 2
                        break
                    xPtr = ptr + 2*curr
                    if len_file <= xPtr:
                        inc = False
                        ptr -= 2
                        break
                    matched = False
                    for xx in candidate:
                        if xPtr == xx:
                            matched = True
                            break
                    if not matched:
                        inc = False
                        ptr -= 2
                        break
                    prev = curr
            if inc:
                return ptr, idx0
        else:
            ptr -= 2
        
    return -1, -1

def findStrings(buffer: bytes):
    byte_stream = io.BytesIO(buffer)           
    len_file = len(buffer)
    ptrStrEnd = []
    for ptr in range(0, len_file, 2):
        data = byte_stream.read(2)
        if data[1] == 0xE7 or (data[0] == 0xE7 and (data[1] == 0x00 or data[1] == 0xEB)):
            ptrStrEnd.append(ptr+2)
    if not ptrStrEnd: return []
    
    devStrPoses: List[int] = []
    startIdx = len(ptrStrEnd) - 1
    while 0 <= startIdx:
        ptr, count = findReverse(buffer, ptrStrEnd, startIdx)
        if 0 < ptr and 0 < count:
            lenStr = ptrStrEnd[-1] - ptr
            if count == 1 and 40 < lenStr:
                startIdx -= 1
                ptrStrEnd = ptrStrEnd[:startIdx+1]
                continue
            devStrPoses.append(ptr)
        else:
            break
        
        for i, x in enumerate(ptrStrEnd):
            if ptr < x:
                startIdx = i - 1
                ptrStrEnd = ptrStrEnd[:i]
                break
        
    return sorted(devStrPoses)
    
    
class SectionBase:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.buffer = None

        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        if self.buffer is None:
            return 0

        size = len(self.buffer)
        if size%4:
            logging.critical("why not div. by 4?")
        return size
    
    def unpackData(self, buffer: bytes):
        self.buffer = bytearray(buffer) if buffer is not None else None

    def packData(self):
        return self.buffer

#282 : [0x0058, 0x012C, ]
DoorPtrs_jp = { 0 : [0x0044, 0x009C, ], 17 : [0x0330, ], 18 : [0x0068, 0x00D8, ], 20 : [0x01E0, 0x03E8, 0x0514, 0x05E4, 0x0714, ], 24 : [0x0058, ], 25 : [0x0058, ], 26 : [0x0058, ], 28 : [0x0070, ], 30 : [0x00A4, 0x0148, ], 32 : [0x0058, 0x04C4, 0x054C, ], 34 : [0x0254, 0x0384, 0x0438, ], 38: [0xB0,], 42 : [0x0058, 0x00E0, ], 43 : [0x0058, ], 45 : [0x0058, ], 46 : [0x0058, 0x036C, 0x0438, 0x04F0, ], 50 : [0x0064, ], 51 : [0x0058, 0x00DC, ], 59 : [0x0058, ], 60 : [0x0574, 0x05E8, 0x07F8, ], 61 : [0x0058, ], 63 : [0x0058, ], 67 : [0x0058, ], 69 : [0x0058, ], 75 : [0x011C, ], 77 : [0x0058, ], 79 : [0x0058, ], 83 : [0x0058, 0x00DC, ], 88 : [0x0058, ], 90 : [0x0058, 0x00EC, ], 94 : [0x0058, ], 96 : [0x0058, ], 99 : [0x0198, ], 106 : [0x0058, 0x00DC, ], 109 : [0x006C, 0x012C, ], 110 : [0x0064, ], 112 : [0x0058, ], 113 : [0x0090, ], 115 : [0x0064, ], 121 : [0x006C, 0x012C, ], 124 : [0x0200, ], 140 : [0x0058, 0x00EC, ], 142 : [0x0058, 0x00E8, ], 145 : [0x0058, ], 149 : [0x0588, ], 150 : [0x01F8, 0x03A8, 0x0660, 0x0934, 0x0D3C, ], 151 : [0x0094, ], 153 : [0x00BC, 0x0124, ], 155 : [0x0060, ], 156 : [0x0050, ], 159 : [0x00BC, ], 164 : [0x0058, ], 177 : [0x0060, ], 179 : [0x0120, 0x030C, ], 180 : [0x019C, ], 181 : [0x019C, ], 182 : [0x023C, ], 183 : [0x019C, ], 184 : [0x019C, ], 185 : [0x019C, ], 186 : [0x019C, ], 187 : [0x019C, ], 188 : [0x019C, ], 189 : [0x019C, ], 190 : [0x00B0, 0x0268, ], 191 : [0x019C, ], 192 : [0x01D8, ], 193 : [0x019C, ], 194 : [0x019C, ], 195 : [0x019C, ], 196 : [0x019C, ], 197 : [0x019C, ], 198 : [0x019C, ], 199 : [0x01D8, ], 201 : [0x00FC, ], 202 : [0x00B8, ], 203 : [0x013C, 0x03CC, 0x0708, 0x0A40, 0x0BCC, 0x0E54, ], 223 : [0x0058, ], 228 : [0x0058, ], 231 : [0x0094, ], 232 : [0x0094, ], 233 : [0x0094, ], 235 : [0x0058, 0x00CC, ], 236 : [0x0058, ], 241 : [0x0064, ], 248 : [0x0058, 0x00E4, ], 249 : [0x0058, ], 252 : [0x0058, ], 257 : [0x0058, ], 264 : [0x006C, 0x012C, ], 265 : [0x0058, 0x00E0, ], 266 : [0x0058, ], 268 : [0x0124, ], 269 : [0x00B8, ], 271 : [0x00AC, 0x0150, ], 272 : [0x00AC, 0x0154, ], 277 : [0x0058, ], 282 : [0x0058, ], 286 : [0x0058, ], 288 : [0x0058, ], 290 : [0x0058, ], 298 : [0x0058, ], 310 : [0x009C, ], 312 : [0x0058, ], 314 : [0x0058, ], 315 : [0x0058, ], 316 : [0x0068, 0x00D8, ], 318 : [0x0078, 0x0178, ], 321 : [0x0078, 0x0178, ], 334 : [0x0058, ], 336 : [0x0068, 0x00D8, ], 340 : [0x0058, ], 344 : [0x0080, 0x0190, ], 345 : [0x0068, 0x00D8, ], 350 : [0x00FC, 0x01F4, ], 352 : [0x0174, 0x0320, 0x03D4, ], 356 : [0x0058, 0x00E4, ], 358 : [0x0068, 0x00D8, ], 360 : [0x0058, 0x00E8, ], 362 : [0x0058, 0x00E0, ], 366 : [0x0058, 0x00E4, ], 368 : [0x006C, 0x00DC, ], 371 : [0x0058, ], 377 : [0x0058, 0x00E4, ], 382 : [0x006C, 0x00DC, ], 383 : [0x0058, 0x00E0, ], 387 : [0x0058, 0x00E4, ], 392 : [0x0058, 0x00E4, ], 396 : [0x0068, 0x01B4, 0x02E8, 0x03EC, ], 404 : [0x0058, ], 408 : [0x0058, 0x00DC, ], 416 : [0x0110, 0x026C, ], 417 : [0x00C8, 0x0258, ], }
DoorPtrs_en = {0 : [0x0044, 0x009C, ], 17 : [0x0330, ], 18 : [0x0068, 0x00E8, ], 20 : [0x01E0, 0x0418, 0x0574, 0x0650, ], 24 : [0x0058, ], 25 : [0x0058, ], 26 : [0x0058, ], 28 : [0x0070, ], 30 : [0x00A4, 0x0154, ], 32 : [0x04D8, 0x0564, ], 34 : [0x0254, ], 38: [0xB0,], 42 : [0x0058, 0x00E4, ], 46 : [0x0058, 0x0370, 0x044C, 0x0514, ], 50 : [0x0064, ], 51 : [0x0058, 0x00E0, ], 60 : [0x0058, ], 61 : [0x0058, ], 63 : [0x0058, ], 67 : [0x0058, ], 69 : [0x0058, ], 75 : [0x011C, ], 77 : [0x0058, ], 79 : [0x0058, ], 83 : [0x0058, 0x00E0, ], 88 : [0x0058, ], 90 : [0x0058, 0x00F0, ], 94 : [0x0058, ], 96 : [0x0058, ], 99 : [0x0198, ], 106 : [0x0058, 0x00E0, ], 109 : [0x006C, 0x013C, ], 110 : [0x0064, ], 113 : [0x0090, ], 115 : [0x0064, ], 121 : [0x006C, 0x013C, ], 140 : [0x0058, 0x00F0, ], 142 : [0x0058, 0x00EC, ], 145 : [0x0058, ], 149 : [0x0588, ], 150 : [0x067C, 0x0968, 0x0D98, ], 151 : [0x0094, ], 153 : [0x0140, ], 155 : [0x0060, ], 156 : [0x0050, ], 177 : [0x0060, ], 179 : [0x0120, 0x0318, ], 180 : [0x019C, ], 181 : [0x019C, ], 182 : [0x023C, ], 183 : [0x019C, ], 184 : [0x019C, ], 185 : [0x019C, ], 186 : [0x019C, ], 187 : [0x019C, ], 188 : [0x019C, ], 189 : [0x019C, ], 190 : [0x0284, ], 191 : [0x019C, ], 192 : [0x01D8, ], 193 : [0x019C, ], 194 : [0x019C, ], 195 : [0x019C, ], 196 : [0x019C, ], 197 : [0x019C, ], 198 : [0x019C, ], 199 : [0x01D8, ], 203 : [0x03E8, 0x0728, 0x0A70, 0x0C08, 0x0E94, ], 223 : [0x0058, ], 231 : [0x0094, ], 232 : [0x0094, ], 233 : [0x0094, ], 235 : [0x0058, 0x00D8, ], 241 : [0x0064, ], 248 : [0x0058, 0x00E8, ], 249 : [0x0058, ], 252 : [0x0058, ], 257 : [0x0058, ], 264 : [0x006C, 0x013C, ], 265 : [0x0058, 0x00E4, ], 266 : [0x0058, ], 268 : [0x0124, ], 271 : [0x00AC, 0x015C, ], 272 : [0x00AC, 0x0160, ], 277 : [0x0058, ], 282 : [0x0058, ], 286 : [0x0058, ], 290 : [0x0058, ], 298 : [0x0058, ], 310 : [0x009C, ], 312 : [0x0058, ], 314 : [0x0058, ], 315 : [0x0058, ], 316 : [0x0068, 0x00E8, ], 318 : [0x0078, 0x0188, ], 321 : [0x0078, 0x0188, ], 334 : [0x0058, ], 336 : [0x0068, 0x00E8, ], 340 : [0x0058, ], 344 : [0x0080, 0x019C, ], 345 : [0x0068, 0x00E8, ], 350 : [0x0210, ], 352 : [0x0174, 0x0320, 0x03D4, ], 356 : [0x0058, 0x00E8, ], 358 : [0x0068, 0x00E8, ], 360 : [0x0058, 0x00EC, ], 362 : [0x0058, 0x00E4, ], 366 : [0x0058, 0x00E8, ], 368 : [0x006C, 0x00EC, ], 371 : [0x0058, ], 377 : [0x0058, 0x00E8, ], 382 : [0x006C, 0x00EC, ], 383 : [0x0058, 0x00E4, ], 387 : [0x0058, 0x00E8, ], 392 : [0x0058, 0x00E8, ], 396 : [0x0068, 0x01C0, 0x0304, 0x0418, ], 404 : [0x0058, ], 408 : [0x0058, 0x00E0, ], 416 : [0x0110, 0x026C, ],}

def createDoorSectionClass(Ptrs: List[int] = []):
    class DoorSection():
        def __init__(self, buffer: Union[bytes, None] = None) -> None:
            self.buffer = None
            self.strings = []
            self.preSizes = []
            
            if buffer is not None:
                self.unpackData(buffer)

        def __len__(self):
            if self.buffer is None:
                return 0

            return len(self.buffer)

        def cvtStr2Byte(self, table: convert_by_TBL):
            for string in self.strings:
                string.cvtStr2Byte(table)
                
        def cvtByte2Str(self, table: convert_by_TBL):
            for string in self.strings:
                string.cvtByte2Str(table)

        def unpackData(self, buffer: bytes):
            self.buffer = bytes(buffer) if buffer is not None else None
            if self.buffer is None:
                return
            
            for pos in Ptrs:
                self.strings.append(ReadStrings(self.buffer[pos:]))
                len_str = self.strings[-1].len_buffer
                len_str_pad = ((len_str+1)//2)*2
                pad = len_str_pad - len_str
                if pad:
                    res = self.buffer[pos+len_str:pos+len_str+pad]
                    if all([x==0 for x in res]):
                        len_str = len_str_pad
                    else:
                        logging.debug("why?")
                self.preSizes.append(len_str)
            
            return
        
            global debugPos
            devStrPoses = findStrings(self.buffer)
            if devStrPoses:
                print(f"{int(debugPos[3:])} : [", end='')
                for p in devStrPoses: print(f"0x{p:04X}, ", end='')
                print('], ', end='')
 
            with open(f'work/test/MAPen/{debugPos}.door.BIN', 'wb') as file:
                file.write(buffer)

            return
            #global debugPos
            word1 = bytes(b'\xE7\xEB')
            word2 = bytes(b'\xE7\x00')
            len_file = len(buffer) - 2
            for ptr in range(len_file):
                if buffer[ptr:ptr+2] == word1:
                    print(f"{debugPos}, E7EB, ptr: 0x{ptr:X}")
                    with open(f'work/test/MAP/{debugPos}.door.BIN', 'wb') as file:
                        file.write(buffer)
                    break
                if buffer[ptr:ptr+2] == word2:
                    print(f"{debugPos}, E700, ptr: 0x{ptr:X}")
                    with open(f'work/test/MAP/{debugPos}.door.BIN', 'wb') as file:
                        file.write(buffer)
                    break
            
        def packData(self):
            if self.buffer is None:
                return None
            
            byte_stream = io.BytesIO(self.buffer)
            for idx, string in enumerate(self.strings):
                byteData = string.packData()
                currSize = string.len_buffer
                if self.preSizes[idx] < currSize:
                    logging.critical(f"Door overflow: {idx}th ReadString, {self.preSizes[idx]} < {currSize}')")
                    for text in string._str:
                        logging.critical(f"Door overflow: {text}')")

                byte_stream.seek(Ptrs[idx])
                byte_stream.write(byteData)
            
            self.buffer = byte_stream.getvalue()

            return self.buffer
        
    return DoorSection()
    
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
        len_data = getTextLength(data)
        self.name_byte = data[:len_data]

    def cvtByte2Str(self, table: convert_by_TBL):
        self.name_str = table.cvtByte2Str(self.name_byte)
        
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.name_byte = table.cvtStr2Byte(self.name_str)
            
    def packData(self):
        if self.buffer is None:
            return

        byte_stream = io.BytesIO(self.buffer)
        byte_stream.seek(self.ptrWeaponName)
        if 0x18 < len(self.name_byte):
            logging.critical(f"WeaponName: {self.name_str} is too long. max (24byte.)")
            self.name_byte = self.name_byte[:0x17]
            self.name_byte.append(0xE7)
        byte_stream.write(self.name_byte)
        
        self.buffer = byte_stream.getvalue()
   
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

        data = self.strings.packData(True)
        sumBytes = self.strings.len_buffer

        if self.sectionSize < sumBytes:
            logging.info(f"check the dialogs length, size overflowed; privious({self.sectionSize}) < current({sumBytes})")
        self.sectionSize = sumBytes

        if sumBytes == 0:
            return bytes()
        return data

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
                            logging.info(f'dialog text {code.Args[1]} is too long. box_w({w})<text_w({cols}), box_h({h})<text_h({rows})')
                        break
       
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.dialogText.cvtStr2Byte(table)
             
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
            logging.info(f"check the ScriptSection size, size overflowed({self.header[0]} < {sumSizes})")

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
    def __init__(self, input_path: str = '', DoorPtrs = {}) -> None:
        inpPath = Path(input_path)
        
        self.header = []
        self.roomSection        = SectionBase()
        self.clearedSection     = SectionBase()
        self.scriptSection      = ScriptSection()

        key = int(inpPath.stem[3:])
        doorPtr = DoorPtrs.get(key, []) if DoorPtrs else []
        self.doorSection        = createDoorSectionClass(doorPtr)

        self.enemySection       = SectionBase()
        self.treasureSection    = TreasureSection()

        self.fileSize = 0
        
        if input_path:
            self.unpackData(input_path)

    def __len__(self):
        if not self.header:
            return 0
        
        bufferSize = self.header[10] + self.header[11]
        return bufferSize
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.scriptSection.cvtStr2Byte(table)
        self.treasureSection.cvtStr2Byte(table)
        self.doorSection.cvtStr2Byte(table)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.scriptSection.cvtByte2Str(table)
        self.treasureSection.cvtByte2Str(table)
        self.doorSection.cvtByte2Str(table)
        
    def unpackData(self, input_path: str):
        global debugPos
        debugPos = Path(input_path).stem
        
        with open(input_path, 'rb') as file:
            buffer = bytearray(file.read())
            
            self.fileSize = len(buffer)
            lbaSize = ((self.fileSize + 2047)//2048)*2048
            
            logging.info(f"{Path(input_path).stem}: The free space in LBA is {lbaSize - self.fileSize} bytes.")
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

        poses = [self.header[0]]
        sizes = []
        
        scriptSectionData = self.scriptSection.packData()
        
        sections = [self.roomSection, self.clearedSection, self.scriptSection, self.doorSection, self.enemySection, self.treasureSection]

        for idx in range(6):
            sizes.append(len(sections[idx]))
            if idx > 0:
                poses.append(poses[idx-1] + sizes[idx-1])
        sumSizes = poses[5] + sizes[5]
        logging.debug(f"MDP / room:{self.header[1]}, cleared:{self.header[3]}, script:{self.header[5]}, door:{self.header[7]}, enemy:{self.header[9]}, treasure:{self.header[11]}")
        
        prevScriptSectionSize = self.header[5]
        writeSize = len(scriptSectionData) if scriptSectionData is not None else 0
        if prevScriptSectionSize < writeSize:
            logging.info(f"{output_path}, check the section size, size overflowed({prevScriptSectionSize} < {writeSize})")

        for idx in range(0, 12, 2):
            self.header[idx]   = poses[idx//2]
            self.header[idx+1] = sizes[idx//2]
            
        if self.fileSize < sumSizes:
            prev = ((self.fileSize + 2047) // 2048) * 2048
            curr = ((sumSizes + 2047) // 2048) * 2048
            if prev < curr:
                logging.critical(f"{output_path}, check the file size, LBA overflowed({self.fileSize} < {sumSizes})")
            else:
                logging.info(f"{output_path}, check the file size, size overflowed({self.fileSize} < {sumSizes})")

        with open(output_path, 'wb') as file:
            for value in self.header:
                file.write(bytes4(value))

            for idx in range(6):
                data = scriptSectionData if idx == 2 else sections[idx].packData()
                if data is not None:
                    file.seek(poses[idx])
                    file.write(data)

#mpd = MPDstruct()
#mpd.unpackData("D:/Projects/vagrant_story_korean/font/test/jpn/MAP001.MPD")
#mpd.packData("D:/Projects/vagrant_story_korean/MAP001.MPD")




def exportDialogFromMPD(mpd: MPDstruct, fontTable: convert_by_TBL):
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


def exportTresureFromMPD(mpd: MPDstruct, fontTable: convert_by_TBL):
    mpd.treasureSection.cvtByte2Str(fontTable)
    return mpd.treasureSection.name_str

def exportDoorFromMPD(mpd: MPDstruct, fontTable: convert_by_TBL):
    mpd.doorSection.cvtByte2Str(fontTable)
    
    texts0 = {}
    for idx0 in range(len(mpd.doorSection.strings)):
        texts1 = {}
        for idx1 in range(mpd.doorSection.strings[idx0].itemNums):
            text = mpd.doorSection.strings[idx0]._str[idx1]
            texts1[f'{idx1:03}'] = {'string' : text}
        texts0[f'{idx0:03}'] = texts1
    return texts0

def makeMPDtexts(folder_path: str, fontTable: convert_by_TBL, out_path: str, isJp = True):
    extension = '*.MPD'
    file_list = list(Path(folder_path).glob(extension))
    file_list = sorted(file_list)
    
    dialogLists = {}
    etcLists = {}
    #keyTBL = dialog.ReplaceKeyword("work/VSDictTable.tbl")
    doorPtr = DoorPtrs_jp if isJp else DoorPtrs_en
    for filepath in tqdm(file_list, desc="Processing"):
        mpd = MPDstruct(str(filepath), doorPtr)

        texts = exportDialogFromMPD(mpd, fontTable)
        if texts:
            dialogLists[filepath.stem] = texts
            #for idx in range(len(texts)):
            #    dialogLists[f'{filepath.stem}[{idx}]'] = texts[idx]

        texts = exportTresureFromMPD(mpd, fontTable)
        if texts:
            etcLists[filepath.stem] = { 'treasure' : texts } 
        
        texts = exportDoorFromMPD(mpd, fontTable)
        if texts:
            etcLists[filepath.stem] = { 'door' : texts } 
            
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(dialogLists, f, indent=2, ensure_ascii=False)
        #df = pd.DataFrame(dialogLists, columns=['File', 'Index', 'rows', 'cols', 'Original'])#, 'Translated'])
        #df.to_csv(out_path, index=False, encoding='utf-8')
        #df.to_excel(out_path, index=False)
    
    return dialogLists, etcLists

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