import logging
from rich.logging import RichHandler
logging.basicConfig(
        level=logging.DEBUG, 
        format="[%(filename)s:%(lineno)s] >> %(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

from font import makeTBL, cvtFontBin

import fileStruct

from fileStruct.structARM import ARMstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structMPD import MPDstruct

from fileStruct.read_MON_BIN import MON_BIN

from fileStruct.readStrFile import *
from fileStruct.readWordFile import *

from fileStruct.read_SL_Main import SL_Main
from fileStruct.read_TITLE_PRG import TITLE_PRG_en, TITLE_PRG_jp
from fileStruct.read_BATTLE_PRG import *
from fileStruct.read_MENU9_PRG import *

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
_jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")
jpnTBL = dialog.convert_by_TBL("font/font12jp.tbl")
#udaTBL = makeTBL.makeTable("font/font12_table.txt", "font/usa.tbl", 21)
usaTBL = dialog.convert_by_TBL("font/usa.tbl")

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
test1()



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
    znd_path = f'{PATH_JPN_VARGRANTSTORY}/{PATH_testZND}'
    znd = ZNDstruct(znd_path)

    znd.Enemy.cvtByte2Str(jpnTBL)

    outpath = Path(PATH_TEMP) / Path('Test') / Path(PATH_testZND)
    znd.packData(str(outpath))


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
    mainpath = Path(PATH_JPN_VARGRANTSTORY) / Path('SLPS_023.77')
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
    dialogLists['SL_Main'] = texts
    with open(f'work/strings/SLPS_main_ja.json', 'w', encoding='utf-8') as f:
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
    
    dialogLists = {}
    dialogLists['MENU9_1'] = texts1
    dialogLists['MENU9_2'] = texts2
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
    mpd_jp = fileStruct.structMPD.makeMPDtexts(PATH_JPN_VARGRANTSTORY+'/MAP', jpnTBL, 'work/strings/MAP_MPDdialog_jp.json')
    mpd_en = fileStruct.structMPD.makeMPDtexts(PATH_USA_VARGRANTSTORY+'/MAP', usaTBL, 'work/strings/MAP_MPDdialog_en.json')
    for k, en in mpd_en.items():
        jp = mpd_jp[k]
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

    with open('work/strings/MAP_MPD_ja.json', 'w', encoding='utf-8') as f:
        json.dump(mpd_jp, f, indent=2, ensure_ascii=False)
        
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
    extract_MENU_PRG_jp_en('MENU3', 'PRG', False)
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

#exit()



while True:
    cvtBytes()
    cvtBytes2()
    

