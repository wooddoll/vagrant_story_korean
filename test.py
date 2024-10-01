
from font import makeTBL, cvtFontBin

import fileStruct
from fileStruct.structMPD import MPDstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structARM import ARMstruct
from fileStruct.structMain import Mainstruct
from fileStruct.readNameFile import ItemNames
from fileStruct.readStrFile import ReadItemHelp
from fileStruct.readMONFile import MonStructure

from font import dialog
import utils
from VS_pathes import *
import pandas as pd
import os
from pathlib import Path
import logging
from tqdm import tqdm

logging.basicConfig(
    level=logging.DEBUG, 
    format="[%(filename)s:%(lineno)s] >> %(message)s"
)



PATH_testMPD = "MAP/MAP041.MPD"
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


def extractZNDnames():
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
    
def extractARMnames():
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
        inp_text = input('Hex>')
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
        
        _inp_bytes = bytes(inp_bytes)
        inp_text = jpnTBL.cvtBytes_str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")

#cvtBytes()


def cvtBytes2():
    while True:
        inp_text = input('Hex>')
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
        
        _inp_bytes = bytes(inp_bytes)
        inp_text = usaTBL.cvtBytes_str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")




def makeSkillnames():
    mainpath = Path(PATH_TEMP_VARGRANTSTORY) / Path('SLPS_023.77')
    namesInfiles = []
    skill_jpn = Mainstruct(str(mainpath))
    skill_jpn.convertName(jpnTBL)
    namesInfiles.extend(skill_jpn.names_str)

    ####
    mainpath = Path(PATH_USA_VARGRANTSTORY) / Path('SLUS_010.40')
    engInfiles = []
    skill_usa = Mainstruct(str(mainpath))
    skill_usa.convertName(usaTBL)
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

def MCMAN_en_jp():
    inp_path = Path(PATH_TEMP_VARGRANTSTORY) / Path("MENU/MCMAN.BIN")
    help_jp = ReadItemHelp(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/MCMAN.BIN")
    help_en = ReadItemHelp(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.string_str, help_en.string_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_MCMAN_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')


def ITEMHELP_en_jp():
    inp_path = Path(PATH_TEMP_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    help_jp = ReadItemHelp(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    help_en = ReadItemHelp(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.string_str, help_en.string_str):
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

def ItemNames_en_jp():
    names_en = ItemNames(PATH_USA_VARGRANTSTORY)
    names_en.cvtByte2Name(usaTBL)
    names_jp = ItemNames(PATH_TEMP_VARGRANTSTORY)
    names_jp.cvtByte2Name(jpnTBL)
    
    texts = []
    for jp, en in zip(names_jp.name_str, names_en.name_str):
        texts.append([jp, en])

    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_ITEMNAME_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')

def SMALL_MON_BIN_en():
    mon = MonStructure(PATH_USA_VARGRANTSTORY)
    mon.cvtByte2Name(usaTBL)
    texts_en = []
    for idx in range(mon.ItemNumber):
        texts_en.append( [mon.name_str[idx], mon.string_str[idx]] )
    
    df_en = pd.DataFrame(texts_en, columns=['name', 'desc.'])
    outpath = 'work/strings/SMALL_MON_BIN_en.csv'
    df_en.to_csv(outpath, index=False, encoding='utf-8')

def SMALL_MON_BIN_jp():
    mon = MonStructure(PATH_TEMP_VARGRANTSTORY)
    mon.cvtByte2Name(jpnTBL)
    texts_jp = []
    for idx in range(mon.ItemNumber):
        texts_jp.append( [mon.name_str[idx], mon.string_str[idx]] )
    
    df_jp = pd.DataFrame(texts_jp, columns=['name', 'desc.'])
    outpath = 'work/strings/SMALL_MON_BIN_jp.csv'
    df_jp.to_csv(outpath, index=False, encoding='utf-8')

def extractAll():
    ITEMHELP_en_jp()
    exit()
    extractARMnames()
    extractZNDnames()
    makeSkillnames()
    ItemNames_en_jp()
    MCMAN_en_jp()
    
    SMALL_MON_BIN_en()
    SMALL_MON_BIN_jp()

    fileStruct.structMPD.makeMPDtexts(PATH_TEMP_VARGRANTSTORY+'/MAP', jpnTBL, 'work/strings/MAP_MPDdialog_jp.csv')
    fileStruct.structMPD.makeMPDtexts(PATH_USA_VARGRANTSTORY+'/MAP', usaTBL, 'work/strings/MAP_MPDdialog_en.csv')
    
extractAll()

#cvtBytes2()