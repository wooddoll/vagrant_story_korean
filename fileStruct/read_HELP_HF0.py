from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *
from fileStruct.structMPD import SectionBase

class ReadHelpStrings(): 
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.itemNums = -1
        self._byte = []
        self._str = []
        self.len_buffer = -1
        
        if buffer is not None:
            self.unpackData(buffer)

    def cvtStr2Byte(self, table: convert_by_TBL):
        self._byte.clear()
        for data in self._str:
            self._byte.append(table.cvtStr2Byte(data))
    
    def cvtByte2Str(self, table: convert_by_TBL):
        self._str.clear()
        for data in self._byte:
            self._str.append(table.cvtByte2Str(data))
    
    def unpackData(self, buffer: bytes):
        len_buffer = len(buffer)
        byte_stream = io.BytesIO(buffer)
        
        self.itemNums = int2(byte_stream.read(2))
        ptrs = []
        for idx in range(self.itemNums):
            pos = int2(byte_stream.read(2))
            ptrs.append(2*pos)
        ptrs.append(len_buffer)

        self._byte.clear()
        for idx in range(self.itemNums):
            pos = ptrs[idx]
            nextpos = ptrs[idx+1]
            data = buffer[pos:nextpos]
            trimed = trimTextBytes(data)
            self._byte.append(bytearray(trimed))

        len_buffer = len(self._byte[-1]) + 1
        if len_buffer%2:
            len_buffer += 1
        self.len_buffer = len_buffer + ptrs[-2]

    def __len__(self):
        return self.len_buffer if 0 < self.itemNums else 0

    def packData(self):
        if 0 >= self.itemNums:
            return None
        
        if self.itemNums != len(self._byte):
            logging.critical(f"check the number of strings, size different; {self.itemNums} != current({len(self._byte)})")
        

        for idx in range(self.itemNums):
            if self._byte[idx][-1] != 0xE7:
                 self._byte[idx].append(0xE7)
            if len(self._byte[idx])%2:  # align 2byte padding
                self._byte[idx].append(0x0)
                
        ptrs = [ self.itemNums + 1 ]
        for idx in range(self.itemNums):
            ptrs.append(ptrs[-1] + len(self._byte[idx])//2)

        byte_stream = io.BytesIO()
        byte_stream.write(bytes2(self.itemNums))
        
        for idx in range(self.itemNums):
            byte_stream.write(bytes2(ptrs[idx]))
            
        for idx in range(len(self._byte)):
            data = self._byte[idx]
            byte_stream.write(data)
        
        currPos = byte_stream.tell()
        if self.len_buffer < currPos:
            logging.warning(f"check the length of strings, size overflowed; {self.len_buffer} < current({currPos})")
        
        self.len_buffer = currPos
        
        return byte_stream.getvalue()

class HELP_HF0: 
    def __init__(self, input_path: str = '') -> None:
        self.header = []
        self.strings = ReadHelpStrings()
        self.Unknown1 = SectionBase()
        self.Unknown2 = SectionBase()
        self.Unknown2 = SectionBase()
        
        if os.path.isfile(input_path):
            self.unpackData(input_path)
        else:
            logging.warning(f'{input_path} is not valid path.')

    def cvtStr2Byte(self, table: convert_by_TBL):
        self.strings.cvtStr2Byte(table)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.strings.cvtByte2Str(table)

    def unpackData(self, input_path: str):
        with open(input_path, 'rb') as file:
            self.buffer = file.read()
            
            byte_stream = io.BytesIO(self.buffer)
            
            self.header = readHeader(byte_stream, 4, 4)
            ptrs = [ 0x10 ]
            for i in range(3):
                ptrs.append(ptrs[i] + self.header[i])
            
            self.strings = ReadHelpStrings(self.buffer[ptrs[0] : ptrs[1]])
            self.Unknown1 = SectionBase(self.buffer[ptrs[1] : ptrs[2]])
            self.Unknown2 = SectionBase(self.buffer[ptrs[2] : ptrs[3]])
            self.Unknown3 = SectionBase(self.buffer[ptrs[3] : ])

    def packData(self, output_path: str):
        Datas = [ self.strings.packData(), self.Unknown1.packData(), self.Unknown2.packData(), self.Unknown3.packData()]
        self.header[0] = len(self.strings)
        self.header[1] = len(self.Unknown1)
        self.header[2] = len(self.Unknown2)
        self.header[3] = len(self.Unknown3)
        
        with open(output_path, 'wb') as file:
            for idx in range(4):
                file.write(bytes4(self.header[idx]))
                
            for idx in range(4):
                file.write(Datas[idx])

def formatHelpText(text_path: str):
    lines: List[str] = []
    with open(text_path, 'rt') as file:
        lines = file.readlines()

    formatedLines: List[str] = []
    maxLinePos = 250
    for line in lines:
        if line[-1] == '\n':
            currLine = line[:-1]
        elif line[-2:] == '\r\n':
            currLine = line[:-2]
        else:
            currLine = line

        len_line = len(currLine)
        
        pos = 0
        lastSpacePos = 0
        indent = 0
        if currLine.startswith('«FA'):
            indent = int(currLine[3:5], 16) + 0x0C
            
        txtPos = 0
        formatedNewLine = ''
        while pos < len_line:
            letter = currLine[pos]
            pos += 1
            
            if letter == '«':
                tmp = ''
                while pos < len_line:
                    letter = currLine[pos]
                    pos += 1
                    if letter == '»':
                        break
                    tmp += letter
                if tmp[:2] == 'FA':
                    txtPos += int(tmp[2:4], 16)
            else:
                if letter == ' ':
                    lastSpacePos = pos-1
                    txtPos += 6
                else:
                    txtPos += 12
            
            if maxLinePos <= txtPos:
                formatedNewLine += currLine[:lastSpacePos]
                formatedLines.append(formatedNewLine)
                currLine = currLine[lastSpacePos+1:]
                len_line = len(currLine)
                pos = 0
                if 0 < indent:
                    formatedNewLine = f'«FA{indent:02X}»'
                else:
                    formatedNewLine = ''
                txtPos = indent
        formatedNewLine += currLine
        formatedLines.append(formatedNewLine)

    return formatedLines
                    