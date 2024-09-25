# © 2024, wooddoll <fly4moon@hotmail.com>

from PIL import Image
import os

def makeTable(outpath: str = "vagrant_jpn.tbl"):
    path = "D:/Users/wooddoll/Downloads/Maker CHD/Vagrant Story/Vagrant_Story_translation_korean/font/font14_table.txt"
    
    table = {}
    with open(path, 'rt', encoding='utf8') as f:
        lines = f.readlines()

        index = 0
        for line in lines:
            ll = len(line) - 1
            if ll > 18:
                ll = 18
            
            cidx = index*18
            for i in range(ll):
                if cidx < 256:
                    strHex = "0x%0.2X" % cidx
                else:
                    strHex = "0x%0.4X" % cidx

                table[strHex] = str(line[i])

                cidx += 1
            
            index += 1

    t_table = [ [0]*18 for _ in range(126)]
    
    for k, v in table.items():
        idx = int(k, 16)
        rows = idx // 18
        cols = idx % 18

        if v == '□':
            v = 0
        t_table[rows][cols] = v
    
    A = 448
    B = 846
    C = 1265
    table.clear()
    for r, line in enumerate(t_table):
        for c, letter in enumerate(line):
            if letter == 0:
                continue
            index = 18*r + c
            if index < 229:
                strHex = "%0.2X" % index
            elif 229 <= index and index < A:
                strHex = "%0.4X" % (index + 0xEC00)
            elif A <= index and index < B:
                strHex = "%0.4X" % (index + 0xEC5C)
            elif B <= index and index < C:
                strHex = "%0.4X" % (index + 0xECB8)
            elif C <= index and index <= 1889:
                strHex = "%0.4X" % (index + 0xED14)
            elif 1974 <= index and index <= 2183:
                strHex = "%0.4X" % (index + 0xEEC8)
            else:
                strHex = "%0.4X" % (index + 0xEEC8)

            table[strHex] = letter

    if outpath:
        with open(outpath, 'wt', encoding='utf8') as f:
            f.write("EB=«16b Pad»\n")
            f.write("E7=«End»\n")
            f.write("E8=«↵»\n")
            f.write("F801=«p1»\n")
            f.write("F802=«p2»\n")
            f.write("F803=«p3»\n")
            f.write("F804=«p4»\n")
            f.write("F805=«p5»\n")
            f.write("F806=«p6»\n")
            f.write("F807=«p7»\n")
            f.write("F808=«p8»\n")
            f.write("F809=«p9»\n")
            f.write("F80A=«p10»\n")
            f.write("FA06=«?»\n")
            f.write("8F=«Space»\n")
            f.write("\n")

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

def makeTestFontMap():
    pass

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
