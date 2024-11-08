import logging
from rich.logging import RichHandler
logging.basicConfig(
        level=logging.WARNING, 
        format="[%(filename)s:%(lineno)s] >> %(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

from font import makeTBL, cvtFontBin

import fileStruct

from fileStruct.structARM import ARMstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structMPD import MPDstruct

#from fileStruct.read_MON_BIN import MON_BIN
from fileStruct.read_HELP_HF0 import *
from fileStruct.readStrFile import *
from fileStruct.readWordFile import *

from fileStruct.read_MAINMENU import *

#from fileStruct.read_SL_Main import SL_Main
#from fileStruct.read_TITLE_PRG import TITLE_PRG_en, TITLE_PRG_jp
#from fileStruct.read_BATTLE_PRG import *
#from fileStruct.read_MENU9_PRG import *
from fileStruct import read_Nstrings as rN
from fileStruct.read_EVT import EVENT_EVT
from fileStruct.read_ButtonName import ButtonSpecial

from font import dialog, cvtFontBin
import utils
from VS_pathes import *
import pandas as pd
import io
from pathlib import Path
from tqdm import tqdm
import yaml
import json





PATH_testMPD = "MAP/MAP001.MPD"
PATH_testZND = "MAP/ZONE009.ZND"

#dummyTBL = dialog.convert_by_TBLdummy()

#jpnTBL = makeTBL.makeTable("font/font14_table.txt", "font/jpn.tbl")
#_jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")
jpnTBL = dialog.convert_by_TBL("font/font12jp.tbl")
#udaTBL = makeTBL.makeTable("font/font12_table.txt", "font/usa.tbl", 21)
usaTBL = dialog.convert_by_TBL("font/usa.tbl")
korTBL = dialog.convert_by_TBL("font/kor.tbl")

#exit()

def test1():
    mpd = MPDstruct()
    mpd_path = Path(PATH_JPN_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))
    
    mpd.cvtByte2Str(jpnTBL)
    print(mpd.scriptSection.scriptOpcodes)
    
    mpd.cvtStr2Byte(jpnTBL)
    mpd.packData('work/test/MAP001.MPD')
    exit()
    # «»   »«   ↵
    #mpd.scriptSection.dialogText.strings_str[0] = '«F800»貿↵易↵都↵市↵グ↵レ↵イ↵ラ↵ン↵ド'
    #mpd.scriptSection.dialogText.strings_str[1] = '«F800»バ↵ル↵ド↵ル↵バ↵公↵爵↵萄'
    #                                                                        _     <-     8     I    i?     X
    mpd.scriptSection.dialogText.strings_str[2] = "«FB98»«FB04»«F47E»«8F»«F54F»«FA06»«F67E»«F74F»«F750»«F7A1»"
    #mpd.scriptSection.dialogText.strings_str[3] = '«FB68»«FB04»まだです。'
    #mpd.scriptSection.dialogText.strings_str[4] = '«FB30»«FA18»⋯火を消せ。↵«FA18»これでは館曲体が燃えてしまうぞ。↵«FA18»それでは意味がない。'
    #mpd.scriptSection.dialogText.strings_str[5] = '«FB30»«FA18»騎士占を二手に分け,一方を↵«FA18»反逆者どものせん滅に,↵«FA18»もう一方を消火にあたらせるんだ。'
    #mpd.scriptSection.dialogText.strings_str[6] = '«FB68»«FB04»ハッ,ただちに。'
    #mpd.scriptSection.dialogText.strings_str[7] = '«FBB8»«FB04»⋯⋯⋯シドニーめ«F80A»,«F801»どこにいる?'
    mpd.scriptSection.dialogText.cvtStr2Byte(jpnTBL)
    
    mpd_out = f'work/test/{PATH_testMPD}'
    mpd.packData(mpd_out)

    mpd_out = str(Path(os.getcwd()) / Path(mpd_out))
    cmd = f'{PATH_psxinject} "{PATH_TEMP_VARGRANTSTORY_IMAGE}" {PATH_testMPD} "{str(mpd_out)}"'
    utils.run_cmd(cmd, PATH_TEMP)
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
    mpd_path = Path(PATH_JPN_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))
    
    out_path = Path(PATH_TEMP) / Path(f'{Path(PATH_testMPD).stem}.csv')
    dialogLists = readExelDialog(str(out_path))
    
    for idx in range(len(mpd.scriptSection.dialogText.dialogBytes)):
        text = dialogLists[idx]
        byteText = jpnTBL.cvtStr2Byte(text)
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
    znd_path = f'{PATH_JPN_VARGRANTSTORY}/{PATH_testZND}'
    znd = ZNDstruct(znd_path)

    znd.Enemy.cvtByte2Str(jpnTBL)

    outpath = Path(PATH_TEMP) / Path('Test') / Path(PATH_testZND)
    znd.packData(str(outpath))

def test4w():
    folder_path = Path(PATH_JPN_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.glob('*.ZND') if file.is_file()]
    file_list = sorted(file_list)
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)
        
        znd = ZNDstruct(str(filepath))
        for idx in range(len(znd.TIM.TIM)):
            with open(f'work/test/{relative_path.stem}_{idx:03}.TIM', 'wb') as f:
                f.write(znd.TIM.TIM[idx].buffer)
#test4w()

def extract_ZND_jp_en():
    namesInfiles = {}
    weaponesInfiles = {}

    folder_path = Path(PATH_JPN_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.rglob('*.ZND') if file.is_file()]
    file_list = sorted(file_list)
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        znd = ZNDstruct(str(filepath))
        znd.Enemy.cvtByte2Str(jpnTBL)

        namesInfiles[relative_path.stem] = znd.Enemy.name_str
        weaponesInfiles[relative_path.stem] = znd.Enemy.weapon_str

    _namesInfiles = {}
    _weaponesInfiles = {}

    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.rglob('*.ZND') if file.is_file()]
    file_list = sorted(file_list)
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        znd = ZNDstruct(str(filepath))
        znd.Enemy.cvtByte2Str(usaTBL)

        _namesInfiles[relative_path.stem] = znd.Enemy.name_str
        _weaponesInfiles[relative_path.stem] = znd.Enemy.weapon_str
    
    ###

    name_texts = {}
    weapon_texts = {}
    for k, v in namesInfiles.items():
        npc_jp = namesInfiles[k]
        npc_en = _namesInfiles[k]
        
        weapon_jp = weaponesInfiles[k]
        weapon_en = _weaponesInfiles[k]
    
        len_npc_jp = len(npc_jp)
        len_npc_en = len(npc_en)
        if len_npc_jp != len_npc_en:
            logging.critical("!!!")
        len_weapon_jp = len(weapon_jp)
        len_weapon_en = len(weapon_en)
        if len_weapon_jp != len_weapon_en:
            logging.critical("!!!")
    
        
        for idx in range(len_npc_jp):
            if not npc_jp[idx] and (not npc_en[idx] or npc_en[idx] == 'nothing' or npc_en[idx] == 'nothing '):
                continue
            
            if name_texts.get(npc_jp[idx]) is None:
                name_texts[npc_jp[idx]] = npc_en[idx]
        
        
        for idx in range(len_weapon_jp):
            if not weapon_jp[idx] and (not weapon_en[idx] or weapon_en[idx] == 'nothing' or weapon_en[idx] == 'nothing '):
                continue
            
            if weapon_texts.get(weapon_jp[idx]) is None:
                weapon_texts[weapon_jp[idx]] = weapon_en[idx]

    names = {}
    idx = 0
    for k, v in name_texts.items():
        _name = {}
        _name['Name'] = k
        _name['@@localazy:comment:Name'] = v
        names[f'{idx:03}'] = _name
        idx += 1
    
    weapons = {}
    idx = 0
    for k, v in weapon_texts.items():
        _name = {}
        _name['Weapon'] = k
        _name['@@localazy:comment:Weapon'] = v
        weapons[f'{idx:03}'] = _name
        idx += 1

    dialogLists = {}
    dialogLists['MAP_ZND'] = { 'NPCs' : names, 'WEAPONs' : weapons } 
    with open(f'work/strings/MAP_ZND_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)
    
def extract_ARM_jp_en():
    folder_path = Path(PATH_JPN_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.ARM') if file.is_file()]
    file_list = sorted(file_list)
    
    namesInfiles = {}
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        arm = ARMstruct(str(filepath))
        arm.cvtByte2Str(jpnTBL)

        namesInfiles[relative_path.stem] = arm.names_str

    ####
    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.ARM') if file.is_file()]
    file_list = sorted(file_list)
    
    engInfiles = {}
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        arm = ARMstruct(str(filepath))
        arm.cvtByte2Str(usaTBL)

        engInfiles[relative_path.stem] = arm.names_str
    ###

    arm_names = {}
    for k, v in namesInfiles.items():
        jp = namesInfiles[k]
        en = engInfiles[k]
    
        len_jpn = len(jp)
        len_usa = len(en)
        if len_jpn != len_usa:
            logging.critical("!!!")
    
        texts = {}
        for idx in range(len(jp)):
            if not jp[idx] and not en[idx]:
                continue
        
            singleRow = {}
            singleRow['string'] = jp[idx]
            singleRow['@@localazy:comment:string'] = en[idx]
            texts[f'{idx:03}'] = singleRow

        arm_names[k] = texts

    dialogLists = {}
    dialogLists['SMALL_ARM'] = arm_names
    with open(f'work/strings/SMALL_ARM_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)

def check1():
    mpd = MPDstruct()
    mpd_path = Path(PATH_TEMP) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))

    print(mpd)
#check1()


#findword = dialog.Find_Word2()
#findword.find_in_folder(PATH_JPN_VARGRANTSTORY, "work/find_in_folder.yaml")
#exit()


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

def cvtBytes_jp():
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
        inp_text = jpnTBL.cvtByte2Str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")

def cvtBytes_jp_inv():
    while True:
        inp_text = input('Jpn_inv>')
        if not inp_text: break
        
        len_inp = len(inp_text)
        if len_inp == 1:
            exit()
        
        inp_bytes = jpnTBL.cvtStr2Byte(inp_text)
        for v in inp_bytes:
            print(f"{v:02X} ", end='')
        print()



def cvtBytes_en():
    while True:
        inp_text = input('Eng>')
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
        inp_text = usaTBL.cvtByte2Str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")

def cvtBytes_kor():
    while True:
        inp_text = input('Kor>')
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
        inp_text = korTBL.cvtByte2Str(_inp_bytes)
        for v in _inp_bytes:
            print(f"{v:02X} ", end='')
        print(f"\n{inp_text}")


def cvtBytes_kor_inv():
    while True:
        inp_text = input('Kor_Inv>')
        if not inp_text: break
        
        len_inp = len(inp_text)
        if len_inp == 1:
            exit()
        
        inp_bytes = korTBL.cvtStr2Byte(inp_text)
        for v in inp_bytes:
            print(f"{v:02X} ", end='')
        print()


def extract_SL_Main_jp_en():
    mainpath = Path(PATH_JPN_VARGRANTSTORY) / Path('SLPS_023.77')
    skill_jpn = rN.SL_Main_jp(str(mainpath))
    skill_jpn.cvtByte2Str(jpnTBL)
    ####
    mainpath = Path(PATH_USA_VARGRANTSTORY) / Path('SLUS_010.40')
    skill_usa = rN.SL_Main_en(str(mainpath))
    skill_usa.cvtByte2Str(usaTBL)
    ###

    texts = {}
    for idx, txt in enumerate(skill_jpn.words[0]._str):
        jp = txt
        en = skill_usa.words[0]._str[idx]

        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts[f'{idx:03}'] = singleRow

    texts2 = {}
    for idx, txt in enumerate(skill_jpn.strings[0]._str):
        jp = txt
        en = skill_usa.strings[0]._str[idx]

        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts2[f'{idx:03}'] = singleRow

    dialogLists = {}
    dialogLists['SL_Main'] = texts
    dialogLists['SL_Main_1'] = texts2
    with open(f'work/strings/SLPS_main_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)

#extract_SL_Main_jp_en()
#exit()

def extract_TITLE_PRG_jp_en():
    mainpath = Path(PATH_JPN_VARGRANTSTORY) / Path('TITLE/TITLE.PRG')
    namesInfiles = []
    skill_jpn = TITLE_PRG_jp(str(mainpath))
    skill_jpn.cvtByte2Str(jpnTBL)
    namesInfiles.extend(skill_jpn.names_str)

    ####
    mainpath = Path(PATH_USA_VARGRANTSTORY) / Path('TITLE/TITLE.PRG')
    engInfiles = []
    skill_usa = TITLE_PRG_en(str(mainpath))
    skill_usa.cvtByte2Str(usaTBL)
    engInfiles.extend(skill_usa.names_str)

    ###
    
    len_jpn = len(namesInfiles)
    len_usa = len(engInfiles)
    if len_jpn != len_usa:
        logging.critical("!!!")
    
    texts = {}
    for idx in range(len_jpn):
        jp = namesInfiles[idx]
        en = engInfiles[idx]
    
        if not jp and not en:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts[f'{idx:03}'] = singleRow

    dialogLists = {}
    dialogLists['TITLE'] = texts
    with open(f'work/strings/TITLE_TITLE_PRG_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)
    return

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
    inp_path = Path(PATH_JPN_VARGRANTSTORY) / Path("MENU/MCMAN.BIN")
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



#test7()
        
def test8():
    inp_path = Path(PATH_JPN_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")
    itemhelp = rN.ITEMHELP(str(inp_path))
    itemhelp.cvtByte2Str(jpnTBL)
    
    for idx in range(itemhelp.strings[0].itemNums):
        print(f"{idx}({len(itemhelp.strings[0]._byte[idx])}): {itemhelp.strings[0]._str[idx]}")
        
    print()


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
    names_en.cvtByte2Str(usaTBL)
    names_jp = ITEMNAME_BIN(str(Path(PATH_JPN_VARGRANTSTORY) / Path('MENU/ITEMNAME.BIN')))
    names_jp.cvtByte2Str(jpnTBL)
    
    texts = []
    for jp, en in zip(names_jp.strings_str, names_en.strings_str):
        texts.append([jp, en])

    return texts
    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_ITEMNAME_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')

def extract_ITEMHELP_jp_en():
    help_jp = ITEMHELP_BIN(str(Path(PATH_JPN_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")))
    help_jp.cvtByte2Str(jpnTBL)
    help_en = ITEMHELP_BIN(str(Path(PATH_USA_VARGRANTSTORY) / Path("MENU/ITEMHELP.BIN")))
    help_en.cvtByte2Str(usaTBL)

    texts = []
    for jp, en in zip(help_jp.strings_str, help_en.strings_str):
        texts.append([jp, en])

    return texts
    df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    outpath = 'work/strings/MENU_ITEMHELP_BIN.csv'
    df.to_csv(outpath, index=False, encoding='utf-8')

def extract_ITEM_jp_en():
    itemName = extract_ITEMNAME_jp_en()
    itemHelp = extract_ITEMHELP_jp_en()
    
    len_strings = len(itemName)
    if len_strings != len(itemHelp):
        logging.critical(f'why?!!!, Item Name / Help')
    
    texts = {}
    for idx in range(len_strings):
        singleRow = {}
        singleRow['ITEMNAME'] = itemName[0]
        singleRow['@@localazy:comment:ITEMNAME'] = itemName[1]
        singleRow['ITEMHELP'] = itemHelp[0]
        singleRow['@@localazy:comment:ITEMHELP'] = itemHelp[1]
        texts[f'{idx:03}'] = singleRow
    
    dialogLists = {}
    dialogLists['ITEM'] = texts
    with open(f'work/strings/MENU_ITEMNAME_ITEMHELP_BIN.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)

def read_SMALL_MON_BIN_en():
    mon = MON_BIN(PATH_USA_VARGRANTSTORY)
    mon.cvtByte2Str(usaTBL)
    texts_en = []
    for idx in range(mon.ItemNumber):
        texts_en.append( [mon.name_str[idx], mon.strings_str[idx]] )
    
    return texts_en
    df_en = pd.DataFrame(texts_en, columns=['name', 'desc.'])
    outpath = 'work/strings/SMALL_MON_BIN_en.csv'
    df_en.to_csv(outpath, index=False, encoding='utf-8')

def read_SMALL_MON_BIN_jp():
    mon = MON_BIN(PATH_JPN_VARGRANTSTORY)
    mon.cvtByte2Str(jpnTBL)
    texts_jp = []
    for idx in range(mon.ItemNumber):
        texts_jp.append( [mon.name_str[idx], mon.strings_str[idx]] )
    
    return texts_jp
    df_jp = pd.DataFrame(texts_jp, columns=['name', 'desc.'])
    outpath = 'work/strings/SMALL_MON_BIN_jp.csv'
    df_jp.to_csv(outpath, index=False, encoding='utf-8')

def extract_SMALL_MON_BIN():
    help_jp = read_SMALL_MON_BIN_jp()
    help_en = read_SMALL_MON_BIN_en()
    
    len_jpn = len(help_jp)
    len_usa = len(help_en)
    if len_jpn != len_usa:
        logging.critical("!!!")
        
    texts = {}
    for idx in range(len_jpn):       
        singleRow = {}
        
        singleRow['name'] = help_jp[idx][0]
        if help_en[idx][0]:
            singleRow['@@localazy:comment:name'] = help_en[idx][0]
        
        if help_jp[idx][1] or help_en[idx][1]:
            singleRow['description'] = help_jp[idx][1]
            if help_en[idx][1]:
                singleRow['@@localazy:comment:description'] = help_en[idx][1]
        
        texts[f'{idx:03}'] = singleRow
    
    dialogLists = {}
    dialogLists['MON'] = texts
    with open(f'work/strings/SMALL_MON_BIN_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)

def extract_MENU_PRG_jp_en(name: str, suffix: str = 'PRG', useEN = True):
    class_en = None
    class_jp = None
    
    if f'{name}_{suffix}' in globals():
        class_en = globals()[f'{name}_{suffix}']
        class_jp = globals()[f'{name}_{suffix}']
        
    if class_en is None:
        if f'{name}_{suffix}_en' in globals():
            class_en = globals()[f'{name}_{suffix}_en']
        if class_en is None:
            logging.warning(f'wrong function name {name}')
            return
        
    if class_jp is None:
        if f'{name}_{suffix}_jp' in globals():
            class_jp = globals()[f'{name}_{suffix}_jp']
        if class_jp is None:    
            logging.warning(f'wrong function name {name}')
            return
    
    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path(f"MENU/{name}.{suffix}")
    help_en = class_en(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    inp_path = Path(PATH_JPN_VARGRANTSTORY) / Path(f"MENU/{name}.{suffix}")
    help_jp = class_jp(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)
    
    len_strings = len(help_jp.strings_str)
    if useEN:
        if len_strings != len(help_en.strings_str):
            logging.critical(f'why?!!!, {name}_{suffix}')
    
    texts = {}
    if useEN:
        for idx in range(len_strings):
            jp = help_jp.strings_str[idx]
            en = help_en.strings_str[idx]

            if not jp and not en:
                continue
            
            singleRow = {}
            singleRow['string'] = jp
            singleRow['@@localazy:comment:string'] = en
            texts[f'{idx:03}'] = singleRow
    else:
        for idx in range(len_strings):
            jp = help_jp.strings_str[idx]
            if not jp:
                continue
            
            singleRow = {}
            singleRow['string'] = jp
            singleRow['@@localazy:comment:string'] = ''
            texts[f'{idx:03}'] = singleRow

    dialogLists = {}
    dialogLists[name] = texts
    with open(f'work/strings/MENU_{name}_{suffix}_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)
    
    #df = pd.DataFrame(texts, columns=['jp-ja', 'en-us'])
    #outpath = f'work/strings/MENU_{name}_{suffix}.csv'
    #df.to_csv(outpath, index=False, encoding='utf-8')

#extract_MENU_PRG_jp_en('MENU0')

def extract_BATTLE_jp_en():
    inp_path = Path(PATH_JPN_VARGRANTSTORY) / Path("BATTLE/BATTLE.PRG")
    help_jp = BATTLE_PRG_jp(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("BATTLE/BATTLE.PRG")
    help_en = BATTLE_PRG_en(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts1 = {}
    for idx in range(len(help_jp.strings_str)):
        jp = help_jp.strings_str[idx]
        en = help_en.strings_str[idx]
    
        if not jp and not en:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts1[f'{idx:03}'] = singleRow
    
    texts2 = {}
    for idx in range(len(help_jp.words_str)):
        jp = help_jp.words_str[idx]
        en = help_en.words_str[idx]
    
        if not jp and not en:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts2[f'{idx:03}'] = singleRow
    
    texts3 = {}
    for idx in range(len(help_jp.strings2_str)):
        jp = help_jp.strings2_str[idx]
        en = help_en.strings2_str[idx]
    
        if not jp and not en:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts3[f'{idx:03}'] = singleRow
        
        
    dialogLists = {}
    dialogLists['BATTLE_1'] = texts1
    dialogLists['BATTLE_2'] = texts2
    dialogLists['BATTLE_3'] = texts3
    with open(f'work/strings/BATTLE_BATTLE_PRG_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)

#extract_BATTLE_jp_en()
#exit()

def extract_MENU9_jp_en():
    inp_path = Path(PATH_JPN_VARGRANTSTORY) / Path("MENU/MENU9.PRG")
    help_jp = MENU9_PRG_jp(str(inp_path))
    help_jp.cvtByte2Str(jpnTBL)

    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path("MENU/MENU9.PRG")
    help_en = MENU9_PRG_en(str(inp_path))
    help_en.cvtByte2Str(usaTBL)

    texts1 = {}
    for idx in range(len(help_jp.strings1_str)):
        jp = help_jp.strings1_str[idx]
        en = help_en.strings1_str[idx]
    
        if not jp and not en:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        singleRow['@@localazy:comment:string'] = en
        texts1[f'{idx:03}'] = singleRow
    
    texts2 = {}
    for idx in range(len(help_jp.strings2_str)):
        jp = help_jp.strings2_str[idx]
    
        if not jp:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        texts2[f'{idx:03}'] = singleRow
    
    texts3 = {}
    for idx in range(len(help_jp.strings3_str)):
        jp = help_jp.strings3_str[idx]
    
        if not jp:
            continue
        
        singleRow = {}
        singleRow['string'] = jp
        texts3[f'{idx:03}'] = singleRow
    
    dialogLists = {}
    dialogLists['MENU9_1'] = texts1
    dialogLists['MENU9_2'] = texts2
    dialogLists['MENU9_3'] = texts3
    with open(f'work/strings/MENU_MENU9_PRG_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)
    
    return
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
    folder_path = Path(PATH_JPN_VARGRANTSTORY)
    file_list = [file for file in folder_path.rglob('*.PRG') if file.is_file()]
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

    with open('work/test/findStrings.yaml', 'wt', encoding='utf-8') as file:
        yaml.dump(wordinfiles, file, encoding='utf-8')

#findStrings()

def extract_MPD_jp_en():
    mpd_jp, etc_jp = fileStruct.structMPD.makeMPDtexts(PATH_JPN_VARGRANTSTORY+'/MAP', jpnTBL, 'work/strings/MAP_MPDdialog_jp.json', True)
    mpd_en, etc_en = fileStruct.structMPD.makeMPDtexts(PATH_USA_VARGRANTSTORY+'/MAP', usaTBL, 'work/strings/MAP_MPDdialog_en.json', False)
    
    for k, jp in mpd_jp.items():
        en = mpd_en[k]
        if len(jp) >= len(en):
            for i in range(len(en)):
                idx = -(i + 1)
                jp[idx]['@@localazy:comment:string'] = en[idx]['string']
        else:
            print(f'why? {k} {len(jp)}!={len(en)}')
        
        texts = {}
        idx = 0
        for i in range(len(jp)):
            texts[f"{i:03}"] = jp[idx]
            idx += 1
        
        mpd_jp[k] = texts
        
    for k, jp in etc_jp.items():
        _etc_en = etc_en.get(k)
        if _etc_en is not None:
            treasure_en = _etc_en.get('treasure')
            if treasure_en is not None:
                etc_jp[k].update( {'@@localazy:comment:treasure': treasure_en} )
        
            door_en = _etc_en.get('door')
            if door_en is not None:
                for k1, v1 in door_en.items():
                    for k2, v2 in v1.items():
                        etc_jp_k_door = etc_jp[k].get('door')
                        if etc_jp_k_door is not None:
                            etc_jp_k_door_k1 = etc_jp_k_door.get(k1)
                            if etc_jp_k_door_k1 is not None:
                                etc_jp_k_door_k1_k2 = etc_jp_k_door_k1.get(k2)
                                if etc_jp_k_door_k1_k2 is not None:
                                    etc_jp[k]['door'][k1][k2].update( {'@@localazy:comment:string': v2['string']} )
        
        if mpd_jp.get(k) is not None:
            mpd_jp[k].update( etc_jp[k] )
        else:
            mpd_jp[k] = etc_jp[k]
        
    outDict = dict(sorted(mpd_jp.items()))
    
    with open('work/strings/MAP_MPD_ja.json', 'w', encoding='utf-8') as f:
        json.dump(outDict, f, indent=2, ensure_ascii=False)
#extract_MPD_jp_en()
#exit()

def searchByte():
    folder_path = Path(PATH_KOR_VARGRANTSTORY)
    file_list = [file for file in folder_path.rglob('*') if file.is_file()]
    file_list = sorted(file_list)
    #word = bytearray([0x91, 0xE0, 0x90, 0xCD, 0x53, 0xA2, 0xD7, 0xE7])
    #word = bytearray([0xE0, 0x9C, 0x90, 0xCD, 0xED, 0x23, 0xA2, 0xD7])
    #word = bytearray([0xEF, 0x6B, 0xF0, 0x0C, 0x4A, 0x63])
    word = bytearray([0x16 , 0x19 , 0xED , 0x2A , 0xEE , 0xAB , 0x56 , 0x4D , 0x5F])
    len_word = len(word)
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)
        if relative_path.suffix == '.STR': continue
        if relative_path.suffix == '.XA': continue
        if relative_path.stem.startswith('MUSIC'): continue
        if relative_path.stem.startswith('WAVE0'): continue
        
        with open(filepath, 'rb') as file:
            buffer = file.read()
            len_file = len(buffer) - len_word
            for ptr in range(len_file):
                if buffer[ptr:ptr+len_word] == word:
                    print(f"{relative_path}, ptr 0x{ptr:X}")
#searchByte()
#exit()

def extract_SMALL_HF0():
    folder_path = Path(PATH_JPN_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.HF0') if file.is_file()]
    file_list = sorted(file_list)

    jpnInfiles = {}
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        hlp = HELP_HF0(str(filepath))
        hlp.cvtByte2Str(jpnTBL)

        jpnInfiles[relative_path.stem] = hlp.strings._str
    
    ####
    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.HF0') if file.is_file()]
    file_list = sorted(file_list)

    engInfiles = {}
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        hlp = HELP_HF0(str(filepath))
        hlp.cvtByte2Str(usaTBL)

        engInfiles[relative_path.stem] = hlp.strings._str

    ###
    hlp_names = {}
    for k, v in jpnInfiles.items():
        jp = jpnInfiles[k]
        en = engInfiles[k]
    
        len_jpn = len(jp)
        len_usa = len(en)
        if len_jpn != len_usa:
            logging.critical("!!!")
    
        texts = {}
        for idx in range(len(jp)):
            if not jp[idx] and not en[idx]:
                continue
        
            singleRow = {}
            singleRow['string'] = jp[idx]
            #singleRow['@@localazy:comment:string'] = en[idx]
            texts[f'{idx:03}'] = singleRow

        hlp_names[k] = texts

    dialogLists = {}
    dialogLists['SMALL_HELP'] = hlp_names
    with open(f'work/strings/SMALL_HELP_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)
#extract_SMALL_HF0()  
#exit()
def extractAll():
    extract_ARM_jp_en()
    extract_ZND_jp_en()
    extract_MPD_jp_en()
    extract_SL_Main_jp_en()
    extract_TITLE_PRG_jp_en()
    extract_BATTLE_jp_en()
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
    extract_MENU_PRG_jp_en('MENU12', 'BIN')
    extract_MENU_PRG_jp_en('MCMAN', 'BIN')
    extract_SMALL_MON_BIN()
    extract_MENU_PRG_jp_en('ITEMNAME', 'BIN')
    extract_MENU_PRG_jp_en('ITEMHELP', 'BIN')
#  
#extractAll()

def test12():
    system_dat = cvtFontBin.SYSTEM_DAT(f'{PATH_KOR_VARGRANTSTORY}')

    img = system_dat.fontData.getImage()
    img.save('work/font12test.png')
    
    system_dat.fontData.setImage(img)
    
    system_dat.packData('work/system.dat')

def removeControlWord(text: str):
    len_text = len(text)
    ret = ''
    pos = 0
    while pos < len_text:
        if text[pos] == '«':
            while text[pos] != '»':
                pos += 1
            pos += 1
        else:
            ret += text[pos]
            pos += 1
    return ret
        
        
def test13():
    folder_path = Path(PATH_JPN_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.HF0') if file.is_file()]
    file_list = sorted(file_list)

    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        hlp = HELP_HF0(str(filepath))
        hlp.cvtByte2Str(jpnTBL)

        with open(f'work/strings/JPN_{relative_path.stem}_ja.txt', 'w', encoding='utf-8') as f:
            for text in hlp.strings._str:
                teexxt = removeControlWord(text)
                f.write(teexxt)
                f.write('\n')
    
    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.HF0') if file.is_file()]
    file_list = sorted(file_list)

    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        hlp = HELP_HF0(str(filepath))
        hlp.cvtByte2Str(jpnTBL)

        with open(f'work/strings/USA_{relative_path.stem}_en.txt', 'w', encoding='utf-8') as f:
            for text in hlp.strings._str:
                teexxt = removeControlWord(text)
                f.write(teexxt)
                f.write('\n')

def test14():
    extract_MENU_PRG_jp_en('MENU3')
    namedic = MENU3_PRG_jp(PATH_JPN_VARGRANTSTORY)
    namedic.cvtByte2Str(jpnTBL)
    
    for text in namedic.strings_str:
        print(text)
#test14()
    
#extract_SMALL_HF0()
#extract_SMALL_MON_BIN()

def testMENU2():
    loadJp = rN.MENU2_jp(PATH_JPN_VARGRANTSTORY)
    loadEn = rN.MENU2_en(PATH_USA_VARGRANTSTORY)
    
    loadJp.cvtByte2Str(jpnTBL)
    loadEn.cvtByte2Str(usaTBL)
    
    ####
    texts = rN.makeNNstrings(loadJp, loadEn)
    
    textNstr = {}
    textNstr[f"MENU2"] = texts[f'str_0']
    textNstr[f"MENU2_2"] = texts[f'str_1']
    
    with open(f'work/strings/MENU2_ja.json', 'w', encoding='utf-8') as f:
        json.dump(textNstr, f, indent=2, ensure_ascii=False)

def testNNclass():
    for name in rN.FileLoadFuncNames:

        ClassJp, ClassEn = rN.getNNClass(name)        
        loadJp = ClassJp(PATH_JPN_VARGRANTSTORY)
        loadEn = ClassEn(PATH_USA_VARGRANTSTORY)
        
        loadJp.cvtByte2Str(jpnTBL)
        loadEn.cvtByte2Str(usaTBL)
        
        ####
        texts = rN.makeNNstrings(loadJp, loadEn)
        
        textNstr = {}
        if name in rN.FileLoad1Strs:
            if texts.get('str_0') is not None:
                textNstr[name] = texts['str_0']
            if texts.get('word_0') is not None:
                textNstr[name] = texts['word_0']
            
        if name == 'MENU9':
            textNstr[f"MENU9_1"] = texts[f'str_1']
            textNstr[f"MENU9_2"] = texts[f'str_2']
            textNstr[f"MENU9_3"] = texts[f'str_0']
            textNstr[f"MENU9_4"] = texts[f'str_3']
            textNstr[f"MENU9_5"] = texts[f'str_4']
            textNstr[f"MENU9_6"] = texts[f'str_5']
            textNstr[f"MENU9_7"] = texts[f'str_6']
            textNstr[f"MENU9_8"] = texts[f'str_7']
            textNstr[f"MENU9_9"] = texts[f'str_8']
        
        if name == 'BATTLE':
            textNstr[f"BATTLE_1"] = texts[f'str_0']
            textNstr[f"BATTLE_2"] = texts[f'word_0']
            textNstr[f"BATTLE_3"] = texts[f'str_1']
            textNstr[f"BATTLE_4"] = texts[f'str_2']
        
        if name == 'MENU5':
            textNstr[f"MENU5_1"] = texts[f'str_0']
            textNstr[f"MENU5_2"] = texts[f'str_1']
            textNstr[f"MENU5_3"] = texts[f'str_2']
            
        if name == 'INITBTL':
            subText = {}
            subText[f"000"] = texts[f'word_0']
            subText[f"001"] = texts[f'word_1']
            textNstr['INITBTL'] = subText
        
        if name == 'MON':
            subText = {}

            for idx in range(150):
                monName = texts['word_0'].get(f'{idx:03}')
                monDesc = texts['str_0'].get(f'{idx:03}')
                if monDesc is not None:
                    subText[f"{idx:03}"] = {'name':monName['string'], 
                                            "@@localazy:comment:name":monName['@@localazy:comment:string'], 
                                            'description':monDesc['string'], 
                                            "@@localazy:comment:description":monDesc['@@localazy:comment:string']}
                else:
                    subText[f"{idx:03}"] = {'name':monName['string'], 
                                            "@@localazy:comment:name":monName['@@localazy:comment:string']}
            textNstr['MON'] = subText
        with open(f'work/strings/{name}_ja.json', 'w', encoding='utf-8') as f:
            json.dump(textNstr, f, indent=2, ensure_ascii=False)
        ####
        
        loadJp.cvtStr2Byte(jpnTBL)
        loadEn.cvtStr2Byte(usaTBL)
        
        loadJp.packData('work/test/PACKjp')
        loadEn.packData('work/test/PACKen')

    loadEn = MAINMENU_en(PATH_USA_VARGRANTSTORY)
    loadJp = MAINMENU_jp(PATH_JPN_VARGRANTSTORY)
    loadEn.cvtByte2Str(usaTBL)
    loadJp.cvtByte2Str(jpnTBL)
    singleRow = {}
    singleRow['string'] = loadJp._str
    comment = loadEn._str
    if comment:
        comment = comment.replace('☐', ' ')
        singleRow['@@localazy:comment:string'] = comment
    text = {'MAINMENU' : { '000' : singleRow } }
    with open(f'work/strings/MAINMENU_ja.json', 'w', encoding='utf-8') as f:
            json.dump(text, f, indent=2, ensure_ascii=False)
    
#testNNclass()

def readEVT():
    evts_jp = EVENT_EVT(PATH_JPN_VARGRANTSTORY)
    evts_jp.cvtByte2Str(jpnTBL)
    
    evts_en = EVENT_EVT(PATH_USA_VARGRANTSTORY)
    evts_en.cvtByte2Str(usaTBL)
    
    texts = {}
    for k in evts_jp.evtFiles.keys():
        text_file = {}
        _jp = evts_jp.evtFiles[k]
        _en = evts_en.evtFiles[k]
        for idx in range(len(_jp.strings_str)):
            jp = _jp.strings_str[idx]
            if idx < len(_en.strings_str):
                en = _en.strings_str[idx]
            else:
                en = ''

            if not jp and not en:
                continue
            
            singleRow = {}
            singleRow['string'] = jp
            singleRow['@@localazy:comment:string'] = en
            text_file[f'{idx:03}'] = singleRow
        texts[f'{int(k):03}'] = text_file

    with open(f'work/strings/EVENT_EVT_ja.json', 'w', encoding='utf-8') as f:
        json.dump({'EVENT_EVT': texts}, f, indent=2, ensure_ascii=False)
#readEVT()
#exit()

def testMPD():
    folder_path = Path(PATH_USA_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.rglob('*.MPD') if file.is_file()]
    file_list = sorted(file_list)

    #for filepath in tqdm(file_list, desc="Processing"):
    for filepath in file_list:
        relative_path = filepath.relative_to(folder_path)
        
        map = MPDstruct(str(filepath))
    
        #if map.doorSection.buffer is not None:
        #    with open(f'work/test/MAP/{relative_path.stem}.door.BIN', 'wb') as file:
        #        file.write( map.doorSection.buffer )
    #print(map)

def testMPD_():
    filepath = Path(PATH_USA_VARGRANTSTORY) / Path('MAP/MAP042.MPD')
    map = MPDstruct(str(filepath), fileStruct.structMPD.DoorPtrs_en)
    print()
#testMPD_()

#utils.findStringsFromFile(str(Path(PATH_JPN_VARGRANTSTORY) / Path('MENU/NAMEDIC.BIN')))
#exit()

def testNAMEDIC():
    NAMEDIC = rN.NAMEDIC(PATH_JPN_VARGRANTSTORY)
    NAMEDIC.cvtByte2Str(jpnTBL)
    
    dialogLists = {}
    texts1 = {}
    for string in NAMEDIC.strings:
        for idx, text in enumerate(string._str):
            texts1.update({f'{idx:03}': {'string' : text}})
    dialogLists['NAMEDIC'] = texts1
    with open(f'work/strings/MENU_NAMEDIC_BIN_ja.json', 'w', encoding='utf-8') as f:
        json.dump(dialogLists, f, indent=2, ensure_ascii=False)
        
#test15()

def testButtonSpecial():
    btn = ButtonSpecial(PATH_KOR_VARGRANTSTORY)
    btn.cvtByte2Str(jpnTBL)
    btn._str[0] = '결정'
    btn._str[1] = '←삭제'
    btn._str[2] = '삭제'
    btn._str[3] = '삽입'
    btn.cvtStr2Byte(korTBL)
    btn.packData(PATH_KOR_VARGRANTSTORY)
    

#exit()

while True:
    cvtBytes_jp()
    cvtBytes_jp_inv()
    cvtBytes_en()
    cvtBytes_kor()
    cvtBytes_kor_inv()


