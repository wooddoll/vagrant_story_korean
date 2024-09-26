
import sys
import os
from subprocess import Popen, PIPE
import signal
import shlex
import logging

from VS_pathes import *

def run_cmd(cmd, path, log=False):
    if log:
        log = open(os.path.join(path, 'log.txt'), 'wt')
    else:
        log = PIPE

    proc = Popen(shlex.split(cmd), stdout=log, stderr=log, cwd=path, shell=False)
    try:
        outs, errs = proc.communicate()
    except KeyboardInterrupt:
        proc.send_signal(signal.SIGKILL)
        errs = False
    
    if log is not PIPE:
        log.close()

    if errs:
        print(errs.decode("utf-8"))
        
    return outs.decode("utf-8") if outs is not None else None

def readLBAinfoLog(path: str):
    LBAinfo = []
    with open(path, 'rt') as f:
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