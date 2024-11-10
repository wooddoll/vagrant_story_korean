import logging
from rich.logging import RichHandler
logging.basicConfig(
        level=logging.WARNING, 
        format="[%(filename)s:%(lineno)s] >> %(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

import json
import os
from typing import Union, List
from utils import *
from tqdm import tqdm
from pathlib import Path
from font import fontMaker
from font.fontMaker import HistoKorLetters, font12slots, jpnTableslots, cvtKorFontImage, cvtKorFont14Image
from font.cvtFontBin import packFont14Bin, insertTITLE_font
from PIL import Image, ImageDraw, ImageFont
import math
from font import dialog, cvtFontBin
from copy import deepcopy
import shutil
from fileStruct.structARM import ARMstruct
from fileStruct.structZND import ZNDstruct, Drops
from fileStruct.structMPD import MPDstruct, DoorPtrs_jp, DoorPtrs_en
from fileStruct.read_EVT import EVENT_EVT
from fileStruct import merge_StringBIN as mS
from fileStruct.read_MAINMENU import *
from fileStruct import read_Nstrings as rN
from fileStruct.read_HELP_HF0 import HELP_HF0, formatHelpText
from fileStruct.make_GIM import read_GIM
from fileStruct.read_ButtonName import ButtonSpecial
import subprocess

logging.info(f"loading; --- jpnTBL ---")
jpnTBL = dialog.convert_by_TBL("font/font12jp.tbl")
logging.info(f"loading; --- usaTBL ---")
usaTBL = dialog.convert_by_TBL("font/usa.tbl")

def downlaod_localazy():
    whatLoad = ['MPD']
    with open('work/kor/localzay_keys.json', 'r', encoding='utf-8') as json_file:
        localzay_keys = json.load(json_file)
        cmd = "localazy download"
        processes = []
        
        for k, v in localzay_keys.items():
            if k not in whatLoad:
                continue
            
            os.makedirs(f"work/kor/_{k}_", exist_ok=True)
            with open(f'work/kor/_{k}_/localazy.json', 'w', encoding='utf-8') as f:
                json.dump(v, f)
            
                process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=f'{os.getcwd()}/work/kor/_{k}_', shell=False )
                processes.append( process )
        
        for process in tqdm(processes, desc="Processing"):
            process.wait()        
        
        for k, v in localzay_keys.items():
            if k not in whatLoad:
                continue
            
            shutil.copy(f"work/kor/_{k}_/{v['download']['files']}", 'work/kor')
            shutil.rmtree(f'work/kor/_{k}_')
    
    exit()

#downlaod_localazy()

    
def mergeKorString():
    jpn_strings = {}
    json_list = list(Path('work/strings').glob('*.json'))
    for filepath in tqdm(json_list, desc="Processing"):
        if filepath.stem in ['all_strins_jpn', 'localzay_keys']:
            continue
        
        with open(filepath, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            jpn_strings.update(json_data)
    
    with open('work/strings/all_strins_jpn.json', 'w', encoding='utf-8') as f:
        json.dump(jpn_strings, f, indent=2, ensure_ascii=False)
        
        
    kor_strings = {}
    
    json_list = list(Path('work/kor').glob('*.json'))
    for filepath in tqdm(json_list, desc="Processing"):
        if filepath.stem in ['all_strins_kor', 'localzay_keys']:
            continue
        
        with open(filepath, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            kor_strings.update(json_data)
    
    with open('work/kor/all_strins_kor.json', 'w', encoding='utf-8') as f:
        json.dump(kor_strings, f, indent=2, ensure_ascii=False)
        
    return kor_strings


def collectKorLetters(kor_strings: dict):
    PrimeKeys = ['MENU7', 'MCMAN', 'MENU9_3', 'MENU9_7', 'DUMMY']
    MenuKeys = ['BATTLE_1', 'BATTLE_3', 'BATTLE_4', 'MENU0', 'MENU1', 'MENU2', 'MENU3', 'MENU4', 'MENU5', 'MENU8', 
                'MENU9_1', 'MENU9_2', 'MENU9_4', 'MENU9_5', 'MENU9_6', 'MENU9_8', 'MENU9_9'
                'MENUB', 'MENUD', 'MENUE', 'SL_Main']
    
    def setPrioty(key: str):
        if key in PrimeKeys: 
            return 100
        if key in MenuKeys: 
            return 10
        return 1
    
    histoKor = HistoKorLetters()
    for k0, v0 in kor_strings.items():
        Prioty = setPrioty(k0)
        if isinstance(v0, str):
            histoKor.tasteString(v0, Prioty)
        elif isinstance(v0, dict):
            for k1, v1 in v0.items():
                if isinstance(v1, str):
                    histoKor.tasteString(v1, Prioty)
                elif isinstance(v1, dict):
                    for k2, v2 in v1.items():
                        if isinstance(v2, str):
                            histoKor.tasteString(v2, Prioty)
                        elif isinstance(v2, dict):
                            for k3, v3 in v2.items():
                                if isinstance(v3, str):
                                    histoKor.tasteString(v3, Prioty)
                                elif isinstance(v3, dict):
                                    for k4, v4 in v3.items():
                                        if isinstance(v4, str):
                                            histoKor.tasteString(v4, Prioty)
                                        else:
                                            logging.info('why l4?')
                                else:
                                            logging.info('why l3?')
                        else:
                            logging.info('why l2?')
                else:
                    logging.info('why l1?')
        else:
            logging.info('why l0?')

    
    histoKor.sort()
    
    countPrime = 0
    countAll = 0
    for k, v in histoKor.histo.items():
        if v['level'] >= 100:
            countPrime += 1
        elif v['count'] > 0:
            countAll += 1

    print(f"countAll {countAll}, countPrime {countPrime}")
    
    return histoKor.histo

def posInTable_ja(index: int):
    row = index//21
    col = index%21
    
    x = 12*col
    y = 11*row
    
    return x, y

def posInTable_ko(index: int):
    row = index//21
    col = index%21
    y = row*(14 + 4) + 2
    x = col*(14 + 4) + 2
    
    return x, y
    

def collectJpLetters():
    def calpos(row: int, col: int):
        return row*18 + col
    # 3E - E4
    jpnList = []
    jpnList.extend(list(range(calpos(3, 8), calpos(7, 17))))
    jpnList.extend(list(range(calpos(8, 0), calpos(12, 13))))
    
    return jpnList

def makeKorFontData():
    jpnIndexes, jpnLetters = jpnTableslots(jpnTBL)
    korTBL = deepcopy(jpnTBL)
    korKeys = list(korTBL.fwd_tbl.keys())
    korValues = list(korTBL.fwd_tbl.values())
    
    slots = font12slots()
    slotPos = 0
    kor_strings = mergeKorString()
    _korHisto = collectKorLetters(kor_strings)
    
    idx = 0
    
    korHisto = {}
    for k, v in _korHisto.items():
        korHisto[k] = v
        idx += 1
    
    ji = 0
    for k, v in korHisto.items():
        if v['count'] <= 0:
            break
        korValues[jpnIndexes[ji]] = k
        ji += 1
    
    imgJpKr = Image.open('font/font12jp.png')
    imgKr = Image.open('font/font12jp_kor.png')
    
    for k, v in korHisto.items():
        if v['count'] <= 0:
            break
        kpos = v['pos']
        kx, ky = posInTable_ja(kpos)
        
        jpos = slots[slotPos]
        slotPos += 1

        jx, jy = posInTable_ja(jpos)
        
        kLetterImg = imgKr.crop((kx, ky, kx + 12, ky + 11))
        imgJpKr.paste(kLetterImg, (jx, jy, jx + 12, jy + 11))
    
    krfontImage = 'font/font12kr.png'
    imgJpKr.save(krfontImage)
    
    korTable = {}
    for k, v in zip(korKeys, korValues):
        korTable[k] = v
    with open('font/kor.tbl', 'wt', encoding='utf8') as f:
        for k, v in korTable.items():
            h = f'{k:02X}' if k < 0xFF else f'{k:04X}'
            
            f.write(f"{h}={v}\n")

    
    return korHisto

def applyKorFont():
    krfont12Image = 'font/font12kr.png'
    imgJpKr = Image.open(krfont12Image)
    
    system_dat = cvtFontBin.SYSTEM_DAT(f'{PATH_JPN_VARGRANTSTORY}')
    system_dat.fontData.setImage(imgJpKr)
    
    imgUI = Image.open('work/texture/Textkor2.png')
    system_dat.texture_ui.setImage(imgUI)
    #system_dat.texture_ui.image.save('work/texture/test_2.png')
    system_dat.packData(f'{PATH_KOR_VARGRANTSTORY}/BATTLE/SYSTEM.DAT')
    
    insertTITLE_font(f'{PATH_JPN_VARGRANTSTORY}/TITLE/TITLE.PRG', 'font/font12kr.png', f'{PATH_KOR_VARGRANTSTORY}/TITLE/TITLE.PRG')

    krfont14Image = 'font/font14kr.png'
    packFont14Bin(krfont14Image, f'{PATH_KOR_VARGRANTSTORY}/MENU/FONT14.BIN')
    
def posInTable18_ja(index: int):
    row = index//18
    col = index%18
    
    x = 14*col
    y = 14*row
    
    return x, y

def makeKorFont14(korHisto: dict):
    slots = font12slots()
    slotPos = 0

    imgJpKr = Image.open('font/font14_2b_256.png')
    imgKr = Image.open('font/font14jp_kor.png')
    
    for k, v in korHisto.items():
        if v['count'] <= 0:
            break
        kpos = v['pos']
        kx, ky = posInTable18_ja(kpos)
        
        jpos = slots[slotPos]
        slotPos += 1

        jx, jy = posInTable18_ja(jpos)
        
        kLetterImg = imgKr.crop((kx, ky, kx + 14, ky + 14))
        imgJpKr.paste(kLetterImg, (jx, jy, jx + 14, jy + 14))
    
    draw = ImageDraw.Draw(imgJpKr, 'RGBA')
    imgEng = Image.open('font/system_dat_unpack_F.png')
    xx=2184
    for i in range(84):
        ex = i%21
        ey = i//21
        ex *= 12
        ey *= 11
        jx = xx%18
        jy = xx//18
        jx = jx*14 + 1
        jy = jy*14 + 1
        xx += 1
        eLetterImg = imgEng.crop((ex, ey, ex + 12, ey + 11))
        draw.rectangle((jx, jy, jx + 14, jy + 14), fill=(0, 0, 0, 0))
        imgJpKr.paste(eLetterImg, (jx, jy, jx + 12, jy + 11))
    
    krfontImage = 'font/font14kr.png'
    imgJpKr.save(krfontImage)
    
    packFont14Bin(krfontImage, f'{PATH_KOR_VARGRANTSTORY}/MENU/FONT14.BIN')
    
    exit()

logging.info(f"loading; --- korTBL ---")
korTBL = dialog.convert_by_TBL("font/kor.tbl")


def fixMPD(idx: int, mpd: MPDstruct):
    if idx == 1: mpd.scriptSection.scriptOpcodes.opcodes[51].pos(y=66, h=12)
    if idx == 62: mpd.scriptSection.scriptOpcodes.opcodes[161].pos(y=66, h=12)

def update_MPD(index: int, kor_strings: dict):
    Name = f"MAP{index:03}"
    filepath = f"{PATH_JPN_VARGRANTSTORY}/MAP/{Name}.MPD"
    if Name == 'MAP038':
        print()
    mpd = MPDstruct(str(filepath), DoorPtrs_jp)
    mpd.cvtByte2Str(jpnTBL)

    dictTexts = kor_strings[Name]
    len_dict = len(dictTexts)
    
    treasure = dictTexts.get('treasure')
    if treasure is not None:
        mpd.treasureSection.name_str = treasure
        len_dict -= 1

    door = dictTexts.get('door')
    if door is not None:
        len_dict -= 1
        for k1, v1 in door.items():
            ik1 = int(k1)
            for k2, v2 in v1.items():
                ik2 = int(k2)
                mpd.doorSection.strings[ik1]._str[ik2] = v2['string']
    
    len_string = len(mpd.scriptSection.dialogText.strings_str)
    if len_dict > len_string:
        logging.critical(f"why? {Name} string number differnt! {len_dict} != {len_string}")
    
    
    for k, v in dictTexts.items():
        if k in ['treasure', 'door']:
            continue
        
        idx = int(k)
        rows, cols = dialog.checkSize(mpd.scriptSection.dialogText.strings_str[idx])
        string = v.get('string')
        if string is not None:
            mpd.scriptSection.dialogText.strings_str[idx] = string
            if cols == 1:
                mpd.scriptSection.dialogText.strings_str[idx] = dialog.flat2vertical( mpd.scriptSection.dialogText.strings_str[idx] )
    
    mpd.scriptSection.updateOpcode()
    mpd.cvtStr2Byte(korTBL)

    fixMPD(index, mpd)
    mpd.packData(f"{PATH_KOR_VARGRANTSTORY}/MAP/MAP{index:03}.MPD")
    
    return mpd
    
def updateMAP_MDP(kor_strings: dict):
    print(f"update === MDP === ")
    
    for key in kor_strings.keys():
        if str(key)[:3] == 'MAP' and str(key) != 'MAP_ZND':
            idx = int(str(key)[3:])           
            #logging.info(f"=== MAP{idx:03}.MPD packing ===")
            #print(f"=== MAP{idx:03}.MPD packing ===")
            update_MPD(idx, kor_strings)

def update_ARM(Name: str, dictTexts: dict):
    filepath = f"{PATH_JPN_VARGRANTSTORY}/SMALL/{Name}.ARM"
    arm = ARMstruct(str(filepath))
    arm.cvtByte2Str(jpnTBL)

    len_dict = len(dictTexts)
    len_string = len(arm.names_str)
    if len_dict > len_string:
        logging.critical(f"why? {Name} string number differnt! {len_dict} != {len_string}")
    
    for k, v in dictTexts.items():
        idx = int(k)
        string = v.get('string')
        if string is not None:
            arm.names_str[idx] = string
   
    arm.cvtStr2Byte(korTBL)
    #print(f"{Name}.ARM")
    arm.packData(f"{PATH_KOR_VARGRANTSTORY}/SMALL/{Name}.ARM")
    
    return arm

def update_SMALL_ARM(kor_strings: dict):
    print(f"update === ARM === ")
    
    dictTexts = kor_strings['SMALL_ARM']
    for k, v in dictTexts.items():
        Name = str(k)
        logging.info(f"=== {Name}.ARM packing ===")
        update_ARM(Name, v)

def update_ZND(filepath: Path, NPCs: dict, WEAPONs: dict, drops: List[Drops] = []):
    znd = ZNDstruct(str(filepath))
    znd.cvtByte2Str(jpnTBL)

    for idx, jpName in enumerate(znd.Enemy.name_str):
        if not jpName: continue
        korName = NPCs.get(jpName)
        if korName is None:
            logging.critical(f"why? {jpName} is not key?")
        znd.Enemy.name_str[idx] = korName
        
    for idx, jpName in enumerate(znd.Enemy.weapon_str):
        if not jpName: continue
        korName = WEAPONs.get(jpName)
        if korName is None:
            logging.critical(f"why? {jpName} is not key?")
        znd.Enemy.weapon_str[idx] = korName
    '''
    for i0, drop_jp in enumerate(znd.Enemy.drops):
        if drop_jp.weapon != drops[i0].weapon:
            print(f"Drops diff, {znd.Enemy.name_str[idx]} weapon({znd.Enemy.weapon_str[i0]}), jp {drop_jp.weapon} != en {drops[i0].weapon}")
        if drop_jp.shield != drops[i0].shield:
            print(f"Drops diff, {znd.Enemy.name_str[idx]} shield, jp {drop_jp.shield} != en {drops[i0].shield}")
        if drop_jp.accessory != drops[i0].accessory:
            print(f"Drops diff, {znd.Enemy.name_str[idx]} accessory, jp {drop_jp.accessory} != en {drops[i0].accessory}")
        for i1 in range(6):
            if drop_jp.armor[i1] != drops[i0].armor[i1]:
                print(f"Drops diff, {znd.Enemy.name_str[idx]} armor, jp {drop_jp.armor[i1]} != en {drops[i0].armor[i1]}")
    '''
    znd.cvtStr2Byte(korTBL)
    znd.packData(f"{PATH_KOR_VARGRANTSTORY}/MAP/{filepath.stem}.ZND")
    
    return znd

def update_MAP_ZND(kor_strings: dict):
    print(f"update === ZND === ")
    
    dictTexts = kor_strings['MAP_ZND']
    
    with open('work/strings/MAP_ZND_ja.json', 'r', encoding='utf-8') as json_file:
        dictTexts_jp = json.load(json_file)['MAP_ZND']

    NPCs = {}
    WEAPONs = {}
    
    for k, v in dictTexts_jp['NPCs'].items():
        NPCs[v['Name']] = dictTexts['NPCs'][k]['Name']
    for k, v in dictTexts_jp['WEAPONs'].items():
        WEAPONs[v['Weapon']] = dictTexts['WEAPONs'][k]['Weapon']
    
    folder_path = Path(PATH_JPN_VARGRANTSTORY) / Path('MAP')
    file_list = [file for file in folder_path.rglob('*.ZND') if file.is_file()]
    file_list = sorted(file_list)
    
    for filepath in file_list:
        relative_path = filepath.relative_to(folder_path)
        logging.info(f"=== {relative_path.stem}.ARM packing ===")
        
        znd_en = ZNDstruct(str(Path(PATH_USA_VARGRANTSTORY) / Path(f'MAP/{relative_path}')))
        
        update_ZND(filepath, NPCs, WEAPONs, znd_en.Enemy.drops)

def rebuildNNclass(kor_strings: dict):
    print(f"update === rebuildNNclass === ")
    
    def replaceStr(strlist: List[str], texts: dict):
        if len(strlist) != len(texts):
            logging.info(f"why???")
        for k, v in texts.items():
            string = v.get('string')
            if string is not None:
                strlist[int(k)] = string
    
    for name in rN.FileLoadFuncNames:
        print(f"update {name}")
        if name== 'MENU3':
            print()
        ClassJp, ClassEn = rN.getNNClass(name)
        if name == 'TITLE':
            loadJp = ClassJp(PATH_KOR_VARGRANTSTORY)
        else:
            loadJp = ClassJp(PATH_JPN_VARGRANTSTORY)
        
        loadJp.cvtByte2Str(jpnTBL)
             
        if name in rN.FileLoad1Strs:
            texts = kor_strings[name]
            if loadJp.strings:
                replaceStr(loadJp.strings[0]._str, texts)
            elif loadJp.words:
                replaceStr(loadJp.words[0]._str, texts)
            else:
                logging.critical(f'not matched strings. {name}')
            
        if name == 'MENU9':
            replaceStr(loadJp.strings[1]._str, kor_strings['MENU9_1'])
            replaceStr(loadJp.strings[2]._str, kor_strings['MENU9_2'])
            replaceStr(loadJp.strings[0]._str, kor_strings['MENU9_3'])
            replaceStr(loadJp.strings[3]._str, kor_strings['MENU9_4'])
            replaceStr(loadJp.strings[4]._str, kor_strings['MENU9_5'])
            replaceStr(loadJp.strings[5]._str, kor_strings['MENU9_6'])
            replaceStr(loadJp.strings[6]._str, kor_strings['MENU9_7'])
            replaceStr(loadJp.strings[7]._str, kor_strings['MENU9_8'])
            replaceStr(loadJp.strings[8]._str, kor_strings['MENU9_9'])
        
        if name == 'BATTLE':
            replaceStr(loadJp.strings[0]._str, kor_strings['BATTLE_1'])
            replaceStr(loadJp.words[0]._str, kor_strings['BATTLE_2'])
            #replaceStr(loadJp.strings[1]._str, kor_strings['BATTLE_3'])
            replaceStr(loadJp.strings[1]._str, kor_strings['BATTLE_4'])
        
        if name == 'MENU5':
            replaceStr(loadJp.strings[0]._str, kor_strings['MENU5_1'])
            replaceStr(loadJp.strings[1]._str, kor_strings['MENU5_2'])
            replaceStr(loadJp.strings[2]._str, kor_strings['MENU5_3'])
            
        if name == 'INITBTL':
            loadJp.words[0]._str[0] = kor_strings['INITBTL']['000']['000']['string']
            loadJp.words[1]._str[0] = kor_strings['INITBTL']['001']['000']['string']
        
        if name == 'MON':
            monText = kor_strings.get('MON')
            for k, v in monText.items():
                monName = v.get('name')
                #monDesc = v.get('description')
                
                if monName is not None:
                    loadJp.words[0]._str[int(k)] = monName
                #if monDesc is not None:
                #    loadJp.strings[0]._str[int(k)] = monDesc
        
        if name == 'SL_Main':
            replaceStr(loadJp.words[0]._str, kor_strings['SL_Main'])
            replaceStr(loadJp.strings[0]._str, kor_strings['SL_Main_1'])
            
        loadJp.cvtStr2Byte(korTBL)
        loadJp.packData(PATH_KOR_VARGRANTSTORY)

def update_EVT(kor_strings: dict):
    print(f"update === EVT === ")
    
    evts_jp = EVENT_EVT(PATH_JPN_VARGRANTSTORY)
    evts_jp.cvtByte2Str(jpnTBL)
    
    texts = kor_strings['EVENT_EVT']
    for k0, v0 in texts.items():
        int_k0 = int(k0)

        #if 504 <= int_k0:   # after here, debug text
        #    break
        
        for k1, v1 in v0.items():
            int_k1 = int(k1)
            string = v1.get('string')
            if string is not None:
                evts_jp.evtFiles[int_k0].strings_str[int_k1] = string
        
        evts_jp.evtFiles[int_k0].strings.cvtStr2Byte(korTBL)
        evts_jp.evtFiles[int_k0].packData(f"{PATH_KOR_VARGRANTSTORY}/EVENT/{int_k0:04}.EVT")


def stringBIN_merge(kor_strings: dict):
    print(f"update === stringBIN_merge === ")
    for name in mS.FileLoadFuncNames:
        print(f"update {name}")
        Class_jp = mS.getNNClass(name)
            
        #Class_jp = globals()[f'mS.{name}']
        if name in ['BATTLE_3', 'MON', 'MENU2_1']:
            curr = Class_jp(PATH_KOR_VARGRANTSTORY)
        else:
            curr = Class_jp(PATH_JPN_VARGRANTSTORY)

        curr.cvtByte2Str(jpnTBL)    
        texts = kor_strings[name]
        if curr.itemNums != len(texts):
            logging.info(f"why???")
        for k, v in texts.items():
            idx = int(k)
            txt = v.get('string')
            if txt is None: continue
            curr.strings._str[idx] = txt

        if name == 'MON':
            for k, v in texts.items():
                idx = int(k)
                txt = v.get('description')
                if txt is None: continue
                curr.strings._str[idx] = txt
        
        curr.cvtStr2Byte(korTBL)
        #curr.checkPtrs()
        #if name in ['MCMAN', 'MENU12', 'ITEMHELP', 'NAMEDIC']:
        #    curr.setBlank(jpnTBL)
        curr.packData(PATH_KOR_VARGRANTSTORY)


def MAINMENU_merge(kor_strings: dict):
    print(f"update === MAINMENU === ")

    curr = MAINMENU_jp(PATH_JPN_VARGRANTSTORY)

    curr.cvtByte2Str(jpnTBL)    
    texts = kor_strings['MAINMENU']
    for k, v in texts.items():
        idx = int(k)
        curr.words[idx]._str = v['string']
    curr.cvtStr2Byte(korTBL)
    
    curr.packData(PATH_KOR_VARGRANTSTORY)

def getTextfromText():
    helpDict = {}
    for i in range(1, 15):
        lines = formatHelpText(f'work/help/help{i:02}.txt')
        
        helpsingle = {}
        for idx, line in enumerate(lines):
            helpsingle[f'{idx:03}'] = line
   
        helpDict[f'HELP_{i:02}'] = helpsingle
        
    with open('work/kor/HELP_ko.json', 'w', encoding='utf-8') as f:
        json.dump(helpDict, f, indent=2, ensure_ascii=False)
    
    return helpDict

def update_Help():
    print(f"update === HELP === ")
    
    #getTextfromText()
    
    with open('work/kor/HELP_ko.json', 'r', encoding='utf-8') as json_file:
        helpDict = json.load(json_file)
        
    for i in range(1, 15):
        print(f"HELP{i:02}")
        hlp = HELP_HF0(f'{PATH_JPN_VARGRANTSTORY}/SMALL/HELP{i:02}.HF0')
        hlp.cvtByte2Str(jpnTBL)

        lines = helpDict[f'HELP_{i:02}']
        hlp.strings._str.clear()
        for idx, line in lines.items():
            hlp.strings._str.append(line)
        hlp.strings.itemNums = len(hlp.strings._str)

        hlp.cvtStr2Byte(korTBL)
        hlp.strings.packData()
        hlp.packData(f'{PATH_KOR_VARGRANTSTORY}/SMALL/HELP{i:02}.HF0')

def updateButton():
    btn = ButtonSpecial(PATH_KOR_VARGRANTSTORY)
    btn.cvtByte2Str(jpnTBL)
    btn._str[0] = '결정'
    btn._str[1] = '←삭제'
    btn._str[2] = '삭제'
    btn._str[3] = '삽입'
    btn.cvtStr2Byte(korTBL)
    btn.packData(PATH_KOR_VARGRANTSTORY)
    
        
def rebuildKor():
    kor_strings = mergeKorString()
    
    insertTITLE_font(f'{PATH_JPN_VARGRANTSTORY}/TITLE/TITLE.PRG', 'font/font12kr.png', f'{PATH_KOR_VARGRANTSTORY}/TITLE/TITLE.PRG')
        
    MAINMENU_merge(kor_strings)
    rebuildNNclass(kor_strings)
    stringBIN_merge(kor_strings)

    updateMAP_MDP(kor_strings)
    update_SMALL_ARM(kor_strings)
    update_MAP_ZND(kor_strings)
    
    update_EVT(kor_strings)

    update_Help()

    gim = read_GIM(PATH_JPN_VARGRANTSTORY)
    gim.setImage()
    gim.pack(PATH_KOR_VARGRANTSTORY)

    updateButton()

#cvtKorFontImage()
#cvtKorFont14Image()
#exit()
#downlaod_localazy()

#korHisto = makeKorFontData()
#makeKorFont14(korHisto)
#update_Help()
#exit()
#applyKorFont()
rebuildKor()

def test1():
    system_dat = cvtFontBin.SYSTEM_DAT(f'{PATH_JPN_VARGRANTSTORY}')
    imgUI = Image.open('work/texture/system_dat_pack_1.png')
    system_dat.texture_ui.setImage(imgUI)
    system_dat.packData(f'{PATH_KOR_VARGRANTSTORY}/BATTLE/SYSTEM.DAT')


PATH_testMPD = "MAP/MAP001.MPD"
PATH_testZND = "MAP/ZONE009.ZND"
def test2():
    kor_strings = mergeKorString()
    mpd = update_MPD(1, kor_strings)
    
    print(mpd.scriptSection.scriptOpcodes)
    mpd.packData('work/test/MAP001.MPD')
    exit()

def test3():
    kor_strings = mergeKorString()
    update_MAP_ZND(kor_strings)

def test4():
    kor_strings = mergeKorString()
    itemhelp = rN.ITEMHELP(PATH_JPN_VARGRANTSTORY)
    itemhelp.cvtByte2Str(jpnTBL)
    
    for idx in range(itemhelp.strings[0].itemNums):
        print(f"{idx}({len(itemhelp.strings[0]._byte[idx])}): {itemhelp.strings[0]._str[idx]}")

    texts = kor_strings['ITEMHELP']
    for k, v in texts.items():
        idx = int(k)
        string = v.get('string')
        if string is not None:
            itemhelp.strings[0]._str[idx] = v['string']
    itemhelp.cvtStr2Byte(korTBL)
    for idx in range(itemhelp.strings[0].itemNums):
        print(f"{idx}({len(itemhelp.strings[0]._byte[idx])}): {itemhelp.strings[0]._str[idx]}")



def test6():
    def replaceStr(strlist: List[str], texts: dict):
        for k, v in texts.items():
            string = v.get('string')
            if string is not None:
                strlist[int(k)] = string
                
    kor_strings = mergeKorString()
    
    menu9 = rN.MENU9_jp(PATH_JPN_VARGRANTSTORY)
    menu9.cvtByte2Str(jpnTBL)
    
    replaceStr(menu9.strings[1]._str, kor_strings['MENU9_1'])
    replaceStr(menu9.strings[2]._str, kor_strings['MENU9_2'])
    replaceStr(menu9.strings[0]._str, kor_strings['MENU9_3'])
    replaceStr(menu9.strings[3]._str, kor_strings['MENU9_4'])
    replaceStr(menu9.strings[4]._str, kor_strings['MENU9_5'])
    replaceStr(menu9.strings[5]._str, kor_strings['MENU9_6'])
    replaceStr(menu9.strings[6]._str, kor_strings['MENU9_7'])
    replaceStr(menu9.strings[7]._str, kor_strings['MENU9_8'])
    replaceStr(menu9.strings[8]._str, kor_strings['MENU9_9'])

    menu9.cvtStr2Byte(korTBL)
    
    menu9.packData('work/test/PACKjp')

#test6()