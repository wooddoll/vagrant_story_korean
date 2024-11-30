
from typing import Union, List
import sys
import os
from subprocess import Popen, PIPE
import signal
import shlex
import logging
import io
from pathlib import Path
from VS_pathes import *

def int4(buffer: bytes):
    return int.from_bytes(buffer[0:4], byteorder='little')
def int2(buffer: bytes):
    return int.from_bytes(buffer[0:2], byteorder='little')
def int1(buffer: bytes):
    return int.from_bytes(buffer[0:1], byteorder='little')

def bytes4(num: int):
    return num.to_bytes(4, byteorder='little', signed=False)
def bytes2(num: int):
    return num.to_bytes(2, byteorder='little', signed=False)
def bytes1(num: int):
    return num.to_bytes(1, byteorder='little', signed=False)

def readHeader(byte_stream: io.BytesIO, num: int, byteSize: int):
    headerValues = []
    if byteSize == 1:
        for _ in range(num):
            headerValues.append(int(byte_stream.read(1)))
    elif byteSize == 2:
        for _ in range(num):
            headerValues.append(int2(byte_stream.read(2)))
    elif byteSize == 4:
        for _ in range(num):
            headerValues.append(int4(byte_stream.read(4)))

    return headerValues


def run_cmd(cmd, path, log=False):
    if log:
        log = open(os.path.join(path, 'log.txt'), 'wt', encoding='utf-8')
    else:
        log = PIPE

    proc = Popen(shlex.split(cmd), stdout=log, stderr=log, cwd=path, shell=False)
    try:
        outs, errs = proc.communicate()
    except KeyboardInterrupt:
        proc.send_signal(signal.SIGKILL)
        errs = False
    
    if isinstance(log, io.IOBase):
        log.close()

    if errs:
        print(errs.decode("utf-8"))
        
    return outs.decode("utf-8") if outs is not None else None

def readLBAinfoLog(path: str):
    LBAinfo = []
    with open(path, 'rt', encoding='utf-8') as f:
        lines = f.readlines()
        for idx in range(2,len(lines)):
            lba = lines[idx].split(' ')
            if lba[3] == 'f':
                info = []
                info.append(int(lba[0], 16))
                info.append(int(lba[1], 16))
                info.append(int(lba[2], 16))
                if lba[4][-1] == '\n':
                    info.append(lba[4][:-1])
                else:
                    info.append(lba[4])

                LBAinfo.append(info)

    return LBAinfo

def getLBAInfo(image_path:str):
    
    cmd = f"{PATH_psxrip} -t {image_path}"
    outs = run_cmd(cmd, 'C:/TEMP', True)

    LBAinfo = readLBAinfoLog('C:/TEMP/log.txt')
    LBAinfo_lba = {}
    LBAinfo_path = {}
    for info in LBAinfo:
        LBAinfo_lba[info[0]] = info[1:]
        LBAinfo_path[info[3]] = info[:3]

    return LBAinfo, LBAinfo_lba, LBAinfo_path


#getLBAInfo(PATH_ORIGINAL_VARGRANTSTORY_IMAGE)

def injectFile(image_path:str, path_file):
    cmd = f"{PATH_psxinject} {image_path} {path_file}"
    outs = run_cmd(cmd, 'C:/TEMP')

#injectFile(PATH_TEMP_VARGRANTSTORY_IMAGE, "")

def getByteTextLength(bytesText: bytes) -> int:
    pos = 0
    length = len(bytesText)
    while(pos < length):
        tmp = bytesText[pos]
        pos += 1
        
        if tmp == 0xE7:
            break
        elif tmp == 0xE8:
            continue
        elif tmp >= 0xE5:
            tmp = (tmp << 8) | bytesText[pos]
            if pos < length:
                pos += 1
            if tmp == 0xE6E7:
                break
    return pos

def trimTextBytes(textbytes: bytes):
    len_bytes = len(textbytes)
    pos = 1
    while pos < len_bytes:
        if textbytes[-pos] == 0xE7: 
            break
        pos += 1

    return textbytes[:len_bytes-pos+1]

def format_byte_array(textbytes: bytearray, ControlWord: bool = False):
    if not ControlWord:
        return ','.join(f'0x{byte:02X}' for byte in textbytes)
    
    result = []
    i = 0
    while i < len(textbytes):
        byte = textbytes[i]
        if byte < 0xe5:
            result.append(f'0x{byte:02X}')
            i += 1
        else:
            if i + 1 < len(textbytes):
                next_byte = textbytes[i + 1]
                combined = (byte << 8) | next_byte
                result.append(f'0x{combined:04X}')
                i += 2
            else:
                result.append(f'0x{byte:02X}')
                i += 1
    return ','.join(result)




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
    
    
def findStringsFromFile(filepath: str):
    with open(filepath, 'rb') as file:
        buffer = file.read()
        devStrPoses = findStrings(buffer)
        if devStrPoses:
            _filepath = Path(filepath)
            print(f"{int(_filepath.stem)} : [", end='')
            for p in devStrPoses: print(f"0x{p:04X}, ", end='')
            print('], ', end='')