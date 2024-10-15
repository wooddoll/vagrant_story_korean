
import sys
import os
from subprocess import Popen, PIPE
import signal
import shlex
import logging
import io
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