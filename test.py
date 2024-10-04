
from font import makeTBL, cvtFontBin

import fileStruct

from fileStruct.structARM import ARMstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structMPD import MPDstruct

from fileStruct.read_MON_BIN import MON_BIN
from fileStruct.read_MCMAN_BIN import MCMAN_BIN
from fileStruct.read_ITEMNAME_BIN import ITEMNAME_BIN
from fileStruct.read_ITEMHELP_BIN import ITEMHELP_BIN

from fileStruct.read_SL_Main import SL_Main
from fileStruct.read_TITLE_PRG import TITLE_PRG
from fileStruct.read_BATTLE_PRG import BATTLE_PRG
from fileStruct.read_MENU0_PRG import MENU0_PRG
from fileStruct.read_MENU1_PRG import MENU1_PRG
from fileStruct.read_MENU2_PRG import MENU2_PRG
from fileStruct.read_MENU3_PRG import MENU3_PRG
from fileStruct.read_MENU4_PRG import MENU4_PRG
from fileStruct.read_MENU5_PRG import MENU5_PRG
from fileStruct.read_MENU7_PRG import MENU7_PRG
from fileStruct.read_MENU8_PRG import MENU8_PRG
from fileStruct.read_MENU9_PRG import MENU9_PRG
from fileStruct.read_MENUB_PRG import MENUB_PRG
from fileStruct.read_MENUD_PRG import MENUD_PRG
from fileStruct.read_MENUE_PRG import MENUE_PRG
from fileStruct.read_MENU12_PRG import MENU12_PRG

from font import dialog
import utils
from VS_pathes import *
import pandas as pd
import io
from pathlib import Path
import logging
from tqdm import tqdm
import yaml

logging.basicConfig(
    level=logging.DEBUG, 
    format="[%(filename)s:%(lineno)s] >> %(message)s"
)



PATH_testMPD = "MAP/MAP001.MPD"
PATH_testZND = "MAP/ZONE009.ZND"

#dummyTBL = dialog.convert_by_TBLdummy()

#jpnTBL = makeTBL.makeTable("font/font14_table.txt", "font/jpn.tbl")
jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")

#udaTBL = makeTBL.makeTable("font/font12_table.txt", "font/usa.tbl", 21)
usaTBL = dialog.convert_by_TBL("font/usa.tbl")

#exit()

def test1():
    mpd = MPDstruct()
    mpd_path = Path(PATH_TEMP_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))
    mpd.scriptSection.dialogText.cvtByte2Str(jpnTBL)
    mpd.scriptSection.dialogText.cvtStr2Byte(jpnTBL)
    mpd.packData(f'work/test/{PATH_testMPD}')

    dialogLists = fileStruct.structMPD.exportTextFromMPD(mpd, jpnTBL)
    df = pd.DataFrame(dialogLists, columns=['Index', 'rows', 'cols', 'Original'])
    #out_path = os.path.join(PATH_TEMP, f'{Path(PATH_testMPD).stem}.csv')
    outpath = Path(PATH_TEMP) / Path(f'Test/{Path(PATH_testMPD).stem}.csv')
    df.to_csv(outpath, index=False, encoding='utf-8')

#test1()


def readExelDialog(csv_path:str):
    dialogLists = []
    df = pd.read_csv(csv_path, encoding='utf-8')
    num_rows, num_columns = df.shape
    for idx in range(num_rows):
        Index = int(df.iloc[idx]['Index'])
        rows = int(df.iloc[idx]['rows'])
        cols = int(df.iloc[idx]['cols'])
        original = df.iloc[idx]['Original']
        if cols == 1:
            original = dialog.flat2vertical(original)

        dialogLists.append(original)

    return dialogLists

def test2():
    mpd = MPDstruct()
    mpd_path = Path(PATH_TEMP_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))
    
    out_path = Path(PATH_TEMP) / Path(f'{Path(PATH_testMPD).stem}.csv')
    dialogLists = readExelDialog(str(out_path))
    
    for idx in range(len(mpd.scriptSection.dialogText.dialogBytes)):
        text = dialogLists[idx]
        byteText = jpnTBL.cvtStr_Bytes(text)
        mpd.scriptSection.dialogText.dialogBytes[idx] = byteText
    
    outpath = Path(PATH_TEMP) / Path('Test') / Path(PATH_testMPD)
    mpd.packData(str(outpath))

def test3():
    mpd_path = f'{PATH_TEMP}/{PATH_testMPD}'
    cmd = f'{PATH_psxinject} "{PATH_TEMP_VARGRANTSTORY_IMAGE}" {PATH_testMPD} {str(mpd_path)}'
    utils.run_cmd(cmd, PATH_TEMP)


#test2()
#test3()


def test4():
    znd_path = f'{PATH_TEMP_VARGRANTSTORY}/{PATH_testZND}'
    znd = ZNDstruct(znd_path)

    znd.Enemy.convertName(jpnTBL)

    outpath = Path(PATH_TEMP) / Path('Test') / Path(PATH_testZND)
    znd.packData(str(outpath))


def extract_ZND_jp_en():
    namesInfiles = []
    weaponesInfiles = []

    folder_path = Path(PATH_TEMP_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.rglob('*.ZND') if file.is_file()]
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        znd = ZNDstruct(str(filepath))
        znd.Enemy.convertName(jpnTBL)

        namesInfiles.extend(znd.Enemy.name_str)
        weaponesInfiles.extend(znd.Enemy.weapon_str)
    
    ###
    _namesInfiles = []
    _weaponesInfiles = []

    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.rglob('*.ZND') if file.is_file()]
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        znd = ZNDstruct(str(filepath))
        znd.Enemy.convertName(usaTBL)

        _namesInfiles.extend(znd.Enemy.name_str)
        _weaponesInfiles.extend(znd.Enemy.weapon_str)
    
    ###
    
    #for i in range(len(namesInfiles)):
    #    namesInfiles[i] = f"{namesInfiles[i]}={_namesInfiles[i]}"
    #    weaponesInfiles[i] = f"{weaponesInfiles[i]}={_weaponesInfiles[i]}"
#
    #words = set()
    #for name in namesInfiles:
    #    if name:
    #        words.add(name)
    #namesInfiles = sorted(list(words))
#
    #words = set()
    #for name in weaponesInfiles:
    #    if name:
    #        words.add(name)
    #weaponesInfiles = sorted(list(words))

    for i in range(len(namesInfiles)):
        namesInfiles[i] = [ namesInfiles[i], _namesInfiles[i] ]
        weaponesInfiles[i] = [ weaponesInfiles[i], _weaponesInfiles[i] ]
    
    df_name = pd.DataFrame(namesInfiles, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MAP_ZND_names.csv'
    df_name.to_csv(outpath, index=False, encoding='utf-8')

    df_weapon = pd.DataFrame(weaponesInfiles, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MAP_ZND_weapon.csv'
    df_weapon.to_csv(outpath, index=False, encoding='utf-8')

#extractZNDnames()            
    
def extract_ARM_jp_en():
    namesInfiles = []
    folder_path = Path(PATH_TEMP_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.ARM') if file.is_file()]
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        arm = ARMstruct(str(filepath))
        arm.convertName(jpnTBL)

        namesInfiles.extend(arm.names_str)

    ####
    engInfiles = []
    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.ARM') if file.is_file()]
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        arm = ARMstruct(str(filepath))
        arm.convertName(usaTBL)

        engInfiles.extend(arm.names_str)

    ###

    len_jpn = len(namesInfiles)
    len_usa = len(engInfiles)
    if len_jpn != len_usa:
        logging.critical("!!!")
    
    wordInfiles = []
    for i in range(len_jpn):
        jpn = namesInfiles[i]
        eng = engInfiles[i]
        wordInfiles.append([jpn, eng])

    df = pd.DataFrame(wordInfiles, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/SMALL_ARM_names.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')
    
    #outpath = Path('work/ARMnames.csv')
    #with open(outpath, 'wt', encoding='utf-8') as file:
    #    file.write(f"#Area Names\n")
    #    for name in wordInfiles:
    #        file.write(name + '\n')

#extractARMnames()

#makeTBL.makeTable("font/font12_table.txt", "font/usa.tbl", 21)

def check1():
    mpd = MPDstruct()
    mpd_path = Path(PATH_TEMP) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))

    print(mpd)
#check1()


#findword = dialog.Find_Word()
#findword.find_in_folder(PATH_TEMP_VARGRANTSTORY, "work/find_in_folder.yaml")



def makeMPDtexts(folder_path: str, fontTable: dialog.convert_by_TBL, out_path: str):
    extension = '*.MPD'
    file_list = list(Path(folder_path).glob(extension))

    dialogLists = []
    
    keyTBL = dialog.ReplaceKeyword("work/VSDictTable.tbl")

    for filepath in tqdm(file_list, desc="Processing"):
        mpd = MPDstruct(str(filepath))
        mpd.scriptSection.dialogText.cvtByte2Str(fontTable)
        
        for idx in range(mpd.scriptSection.dialogText.strings.itemNums):            
            text = mpd.scriptSection.dialogText.strings_str[idx]
            rows, cols = dialog.checkSize(text)

            singleRow = []
            singleRow.append(filepath.stem)
            singleRow.append(idx)            
            singleRow.append(rows)
            singleRow.append(cols)

            if cols == 1:
                text = dialog.vertical2flat(text)

            singleRow.append(text)

            knText = keyTBL.replace(text)
            singleRow.append(knText)
            
            dialogLists.append(singleRow)

    with open(out_path, "wt", encoding='utf-8') as file:
        for singleRow in dialogLists:
            fileidx = int(singleRow[0][3:])
            idx = int(singleRow[1])
        
            file.write( f"«{fileidx},{idx}»{singleRow[4]}\n" )


    


def cvtBytes():
    while True:
        inp_text = input('Jpn>')
        if not inp_text: break

        inp_bytes = []
        len_inp = len(inp_text)
        i = 0
        while i < len_inp:
            while inp_text[i] == ' ':
                i += 1
                if i >= len_inp: break
                continue
            if i+2 >= len_inp: break
            inp_bytes.append(int(inp_text[i:i+2], 16))
            i += 2
        
        if not inp_bytes:
            exit()
            
        _inp_bytes = bytes(inp_bytes)
        inp_text = jpnTBL.cvtBytes_str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")


def cvtBytes2():
    while True:
        inp_text = input('Usa>')
        if not inp_text: break

        inp_bytes = []
        len_inp = len(inp_text)
        i = 0
        while i < len_inp:
            while inp_text[i] == ' ':
                i += 1
                if i >= len_inp: break
                continue
            if i+2 >= len_inp: break
            inp_bytes.append(int(inp_text[i:i+2], 16))
            i += 2
        
        if not inp_bytes:
            exit()
            
        _inp_bytes = bytes(inp_bytes)
        inp_text = usaTBL.cvtBytes_str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")




def extract_SL_Main_jp_en():
    mainpath = Path(PATH_TEMP_VARGRANTSTORY) / Path('SLPS_023.77')
    namesInfiles = []
    skill_jpn = SL_Main(str(mainpath))
    skill_jpn.cvtByte2Str(jpnTBL)
    namesInfiles.extend(skill_jpn.names_str)

    ####
    mainpath = Path(PATH_USA_VARGRANTSTORY) / Path('SLUS_010.40')
    engInfiles = []
    skill_usa = SL_Main(str(mainpath))
    skill_usa.cvtByte2Str(usaTBL)
    engInfiles.extend(skill_usa.names_str)

    ###
    
    len_jpn = len(namesInfiles)
    len_usa = len(engInfiles)
    if len_jpn != len_usa:
        logging.critical("!!!")
    
    wordInfiles = []
    for i in range(len_jpn):
        jpn = namesInfiles[i]
        eng = engInfiles[i]
        wordInfiles.append([jpn, eng])

    df = pd.DataFrame(wordInfiles, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/SLPS_main.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')
    

#makeSkillnames()

#findword = dialog.Find_Word()
#findword.find_in_folder(PATH_USA_VARGRANTSTORY, "work/find_in_USA.yaml")

def extract_MCMAN_jp_en():
    inp_path = Path(PATH_TEMP_VARGRANTSTORY) / Path("MENU/MCMAN.BIN")
    help_jp = MCMAN_BIN(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/MCMAN.BIN")
    help_en = MCMAN_BIN(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.strings_str, help_en.strings_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_MCMAN_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')


def extract_ITEMHELP_jp_en():
    inp_path = Path(PATH_TEMP_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    help_jp = ITEMHELP_BIN(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    help_en = ITEMHELP_BIN(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.strings_str, help_en.strings_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_ITEMHELP_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')

#test7()
        
def test8():
    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    with open(str(inp_path), 'rb') as file:
        buffer = bytearray(file.read())
        len_buffer = len(buffer)
        
        for i in range(0, len_buffer, 2):
            data0 = utils.int2(buffer[i:i+2])
            data1 = utils.int2(buffer[i+2:i+4])
            data2 = utils.int2(buffer[i+4:i+6])
            data3 = utils.int2(buffer[i+6:i+8])
            
            if (data1 - data0) == 0xf and (data2 - data1) == 0x16 and (data3 - data2) == 0xE:
                print(f"{hex(i)}({hex(data0)}), {hex(i+2)}({hex(data1)}) - ", end='')
                print(f"{hex(i+2)}({hex(data1)}), {hex(i+4)}({hex(data2)}) - ", end='')
                print(f"{hex(i+4)}({hex(data2)}), {hex(i+6)}({hex(data3)})")
                
def test9():
    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    with open(str(inp_path), 'rb') as file:
        buffer = bytearray(file.read())
        len_buffer = len(buffer)
        
        for i in range(679):
            ptr = utils.int2(buffer[2*i:2*i+2]) * 2
            print(f"{i} _ {hex(2*i)} : {hex(ptr)}")

def extract_ITEMNAME_jp_en():
    names_en = ITEMNAME_BIN(str(Path(PATH_USA_VARGRANTSTORY) / Path('MENU/ITEMNAME.BIN')))
    names_en.cvtByte2Name(usaTBL)
    names_jp = ITEMNAME_BIN(str(Path(PATH_TEMP_VARGRANTSTORY) / Path('MENU/ITEMNAME.BIN')))
    names_jp.cvtByte2Name(jpnTBL)
    
    texts = []
    for jp, en in zip(names_jp.names_str, names_en.names_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_ITEMNAME_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')

def extract_SMALL_MON_BIN_en():
    mon = MON_BIN(PATH_USA_VARGRANTSTORY)
    mon.cvtByte2Str(usaTBL)
    texts_en = []
    for idx in range(mon.ItemNumber):
        texts_en.append( [mon.name_str[idx], mon.strings_str[idx]] )
    
    df_en = pd.DataFrame(texts_en, columns=['name', 'desc.'])
    outpath = 'work/strings/SMALL_MON_BIN_en.csv'
    df_en.to_csv(outpath, index=False, encoding='utf-8')

def extract_SMALL_MON_BIN_jp():
    mon = MON_BIN(PATH_TEMP_VARGRANTSTORY)
    mon.cvtByte2Str(jpnTBL)
    texts_jp = []
    for idx in range(mon.ItemNumber):
        texts_jp.append( [mon.name_str[idx], mon.strings_str[idx]] )
    
    df_jp = pd.DataFrame(texts_jp, columns=['name', 'desc.'])
    outpath = 'work/strings/SMALL_MON_BIN_jp.csv'
    df_jp.to_csv(outpath, index=False, encoding='utf-8')

def extract_MENU_PRG_jp_en(name: str):
    func = None
    if f'{name}_PRG' in globals():
        func = globals()[f'{name}_PRG']
    if func is None:
        logging.warning(f'wrong function name {name}')
        return
    
    inp_path = Path(PATH_TEMP_VARGRANTSTORY) / Path(f"MENU/{name}.PRG")
    help_jp = func(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path(f"MENU/{name}.PRG")
    help_en = func(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.strings_str, help_en.strings_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = f'work/strings/MENU_{name}_PRG.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')


def extract_MENU9_jp_en():
    inp_path = Path(PATH_TEMP_VARGRANTSTORY) / Path("MENU/MENU9.BIN")
    help_jp = MENU9_PRG(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/MENU9.BIN")
    help_en = MENU9_PRG(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.strings1_str, help_en.strings1_str):
        texts.append([jp, en])
    
    for jp, en in zip(help_jp.strings2_str, help_en.strings2_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_MENU9_PRG.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')


def find_string_in_File(filePath: str):
    fileBuffer = None
    with open(filePath, 'rb') as file:
        fileBuffer = file.read()
    if fileBuffer is None:
        return None
    
    byte_stream = io.BytesIO(fileBuffer)
    len_file = len(fileBuffer)
    wordinfile = []
    
    pos = 0
    while pos < len_file:
        byte_stream.seek(pos)
        prev = utils.int2(byte_stream.read(2))
        if prev < 2:
            pos += 2
            continue
        
        startPos = pos
        temp = [prev]
        while pos < len_file-2:
            curr = utils.int2(byte_stream.read(2))
            if prev < curr:
                prev = curr
                temp.append(prev)
            elif len(temp) > 3:
                valid = 0
                for inc in temp:
                    byte_stream.seek(startPos + 2*inc - 2)
                    e1 = byte_stream.read(1)
                    e2 = byte_stream.read(1)
                    if int.from_bytes(e1, 'little') == 0xE7 or int.from_bytes(e2, 'little') == 0xE7:
                        valid += 1
                if len(temp)*0.75 < valid:
                    wordinfile.append([hex(startPos), len(temp)])
                    pos = startPos + 2*temp[-1]
                else:
                    pos = startPos + 2*len(temp)
                break
            else:
                pos = startPos + 2*len(temp)
                break
        if pos >= len_file-2:
            break
        
    return wordinfile


def find0BackE7(byteData: bytes, pos: int, step: int):
    v1 = byteData[pos]
    v2 = byteData[pos+1]
    if v1 != 0 or v2 == 0:
        return False
    for i in range(step):
        idx = pos - i
        if idx <= 0: 
            return False
        if byteData[idx] == 0xE7:
            return True
    return False

def subfind(byteData: bytes, startPos: int, step: int = 0x18):
    len_data = len(byteData)
    
    currPos = startPos
    count = 0
    if currPos >= len_data-1:
        return []
    
    while find0BackE7(byteData, currPos, step):
        currPos += step
        count += 1
        if currPos >= len_data:
            break
        
    if count < 3:
        return []
    return [hex(startPos), count]

def findBackE7(byteData: bytes, pos: int, step: int):
    for i in range(step):
        idx = pos - i
        if idx <= 0: 
            return False
        if byteData[idx] == 0xE7 and byteData[idx+1] == 0: 
            return True
    return False

def subfind0X(byteData: bytes, startPos: int, step: int = 0x18):
    len_data = len(byteData)
    
    currPos = startPos + step
    count = 0
    if currPos >= len_data-1:
        return -1
    
    while currPos < len_data-1:
        v1 = byteData[currPos]
        v2 = byteData[currPos+1]
        if v1 == 0 and v2 != 0:
            count += 1
            currPos += step
            continue
        break
        
    if count < 3:
        return -1
    return count

def checkWords(byteData: bytes, startPos: int):
    v1 = byteData[startPos]
    v2 = byteData[startPos+1]
    if v1 != 0 or v2 == 0:
        return -1
    
    len_data = len(byteData)
    pos = startPos + 2
    end = startPos + 0x3F
    isValid = False
    while pos < len_data-1:
        v1 = byteData[pos]
        v2 = byteData[pos+1]
        if v1 == 0xE7 and v2 == 0:
            isValid = True
            break
        if pos >= end:
            break
        pos += 1
    if not isValid:
        return -1
    
    isValid = False
    while pos < len_data-1:
        v1 = byteData[pos]
        v2 = byteData[pos+1]
        if v1 == 0 and v2 != 0:
            isValid = True
            break
        if pos >= end:
            break
        pos += 1
    if not isValid:
        return -1
    
    return pos - startPos

def find_word_in_File(filePath: str):
    byteData = None
    with open(filePath, 'rb') as file:
        byteData = file.read()
    if byteData is None:
        return None
    
    len_data = len(byteData)
    
    wordinfile = []
    #pos = 0x1
    pos = 0x1
    
    while pos < len_data-1:
        step = checkWords(byteData, pos)
        if 0x10 > step:
            pos += 2
            continue

        count = subfind0X(byteData, pos, step)
        if 3 > count:
            pos += 2
            continue
            
        isValidCount = 0
        for i in range(count):
            ppx = pos + step
            if findBackE7(byteData, ppx, step):
                isValidCount += 1
        
        if count*0.75 < isValidCount:
            wordinfile.append([hex(pos), hex(step), count])
            pos += step*count
        else:
            pos += 2
        
    return wordinfile


#wordinfile = find_word_in_File(f'{PATH_USA_VARGRANTSTORY}/BATTLE/BATTLE.PRG')
#print(wordinfile)


def findStrings():
    folder_path = Path(PATH_USA_VARGRANTSTORY)
    file_list = [file for file in folder_path.rglob('*') if file.is_file()]
    wordinfiles = []
    for filepath in tqdm(file_list, desc="Processing"):
        if str(filepath.suffix) in ['.MPD', '.ARM', '.ZND', '.ZUD', '.SHP', '.SEQ', '.WEP', '.WAV', '.TIM', '.XA', '.P', '.ESQ', '.EVT']:
            continue
        
        relative_path = filepath.relative_to(folder_path)
        if str(relative_path.parent) in [ 'SOUND', 'MOV' ]: 
            continue

        detected = find_string_in_File(str(filepath))
        if detected:
            wordinfiles.append([str(relative_path), detected])
        
        detected = find_word_in_File(str(filepath))
        if detected:
            wordinfiles.append([str(relative_path), detected])

    with open('work/test/findStrings.yaml', 'wt') as file:
        yaml.dump(wordinfiles, file, encoding='utf-8')
#findStrings()

def extractAll():
    extract_ARM_jp_en()
    extract_ZND_jp_en()
    
    fileStruct.structMPD.makeMPDtexts(PATH_TEMP_VARGRANTSTORY+'/MAP', jpnTBL, 'work/strings/MAP_MPDdialog_jp.csv')
    fileStruct.structMPD.makeMPDtexts(PATH_USA_VARGRANTSTORY+'/MAP', usaTBL, 'work/strings/MAP_MPDdialog_en.csv')
    
    extract_SMALL_MON_BIN_en()
    extract_SMALL_MON_BIN_jp()
    extract_MCMAN_jp_en()
    extract_ITEMNAME_jp_en()
    extract_ITEMHELP_jp_en()
    
    extract_SL_Main_jp_en()
    extract_MENU_PRG_jp_en('MENU0')
    extract_MENU_PRG_jp_en('MENU1')
    extract_MENU_PRG_jp_en('MENU2')
    extract_MENU_PRG_jp_en('MENU3')
    extract_MENU_PRG_jp_en('MENU4')
    extract_MENU_PRG_jp_en('MENU5')
    extract_MENU_PRG_jp_en('MENU7')
    extract_MENU_PRG_jp_en('MENU8')
    extract_MENU9_jp_en()
    extract_MENU_PRG_jp_en('MENUB')
    extract_MENU_PRG_jp_en('MENUD')
    extract_MENU_PRG_jp_en('MENUE')
    extract_MENU_PRG_jp_en('MENU12')
#  
extractAll()
exit()



while True:
    cvtBytes()
    cvtBytes2()
    


'''
BATTLE.PRG
$82068 - $A2 - $823AA
$831DC - 31 - $833B6
$835DC - $0B - 

TITLE.PRG   / really use?
$C42C - 

MENU0.PRG detected
MENU1.PRG
MENU2.PRG
MENU3.PRG
MENU4.PRG
MENU5.PRG
MENU7.PRG
MENU8.PRG
MENU9.PRG
MENUB.PRG
MENUD.PRG
MENUE.PRG
'''

