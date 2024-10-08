from PIL import Image
import os
from typing import Dict, Union, List
import logging

def makeTable(font14_table: str, outpath: str = "", LINE_COLS = 18):    
    table = {}
    with open(font14_table, 'rt', encoding='utf8') as f:
        lines = f.readlines()

        index = 0
        for line in lines:
            ll = len(line) - 1
            if ll > LINE_COLS:
                ll = LINE_COLS
            
            cidx = index*LINE_COLS
            for i in range(ll):
                if cidx < 256:
                    strHex = "0x%0.2X" % cidx
                else:
                    strHex = "0x%0.4X" % cidx

                if table.get(strHex) is not None:
                    logging.critical(f'duplicated {strHex}={str(line[i])}')
                table[strHex] = str(line[i])

                cidx += 1
            
            index += 1

    t_table = [ [0]*LINE_COLS for _ in range(126)]
    
    for k, v in table.items():
        idx = int(k, 16)
        rows = idx // LINE_COLS
        cols = idx % LINE_COLS

        if v == '☒':
            v = 0
        t_table[rows][cols] = v
    
    #             0       1      2        3       4        5       6        7      8
    tblSection = (229,   420,   840,    1260,   1680,    1890,   1974,    2184,   2244)
    tblAddress =   (0xEC00, 0xEC5C, 0xECB8, 0xED14, 0xEDEE,  0x0,  0xEEC8, 0xEF24)
    table.clear()
    for r, line in enumerate(t_table):
        for c, letter in enumerate(line):
            if letter == 0: continue

            index = LINE_COLS*r + c
            if index < tblSection[0]:
                strHex = "%0.2X" % index
            elif tblSection[0] <= index and index < tblSection[1]:
                strHex = "%0.4X" % (index + tblAddress[0])
            elif tblSection[1] <= index and index < tblSection[2]:
                strHex = "%0.4X" % (index + tblAddress[1])
            elif tblSection[2] <= index and index < tblSection[3]:
                strHex = "%0.4X" % (index + tblAddress[2])
            elif tblSection[3] <= index and index < tblSection[4]:
                strHex = "%0.4X" % (index + tblAddress[3])
            elif tblSection[4] <= index and index < tblSection[5]:
                strHex = "%0.4X" % (index + tblAddress[4])
            elif tblSection[6] <= index and index < tblSection[7]:
                strHex = "%0.4X" % (index + tblAddress[6])
            elif tblSection[8] == index:
                strHex = "%0.4X" % (index + tblAddress[7])
            #else:
            #    logging.critical("out of font tbl")

            table[strHex] = letter

    if outpath:
        with open(outpath, 'wt', encoding='utf8') as f:
            #f.write("EB=«16b Pad»\n")
            #f.write("E7=«End»\n")
            #f.write("E8=«↵»\n")
            #f.write("F801=«p1»\n")
            #f.write("F802=«p2»\n")
            #f.write("F803=«p3»\n")
            #f.write("F804=«p4»\n")
            #f.write("F805=«p5»\n")
            #f.write("F806=«p6»\n")
            #f.write("F807=«p7»\n")
            #f.write("F808=«p8»\n")
            #f.write("F809=«p9»\n")
            #f.write("F80A=«p10»\n")
            #f.write("FA06=«?»\n")
            #f.write("8F=«Space»\n")
            #f.write("\n")

            for k, v in table.items():
                f.write(f"{k}={v}\n")

    #row = 0
    #for line in t_table:
    #    print(f"{row}: ", end='')
    #    for c in line:
    #        print(f"{c} ", end='')
    #    print()
    #    row += 1

    return table

def readTBL(path: str) -> Dict[int, str]:
    lines = []
    with open(path, 'rt', encoding='utf-8') as file:
        lines = file.readlines()
    
    tbl = {}
    for line in lines:
        pos = line.find('=')
        if pos == -1: continue
        txts = line.split('=')
        
        tbl[int(txts[0], 16)] = txts[1][:-1]
    
    return tbl

def str2Bytes():
    table = makeTable()
    table['E8'] = "«↵»"
    while(True):
        text = input("db> ")
        if not text:
            break

        txts = text.split(',')
        maxTxt = len(txts)
        print(f'{maxTxt}, "', end='')

        idx = 0
        while(idx < maxTxt):
            ii = int(txts[idx], 16)
            idx += 1
            if 0xE7 == ii:
                break
            elif 0xE8 == ii:
                print("↵", end='')
                continue
            elif 229 < ii :
                lo = int(txts[idx], 16)
                idx += 1
                ii = (ii << 8) | lo
                strHex = "%0.4X" % ii
            else:
                strHex = "%0.2X" % ii

            c = table.get(strHex, None)
            if c is not None:
                print(c, end='')
        print('"')
