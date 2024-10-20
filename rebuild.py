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
from font.fontMaker import HistoKorLetters, font12slots, jpnTableslots, cvtKorFontImage
from PIL import Image, ImageDraw, ImageFont
import math
from font import dialog, cvtFontBin
from copy import deepcopy
import shutil
from fileStruct.structARM import ARMstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structMPD import MPDstruct
from fileStruct.read_EVT import EVENT_EVT
#from fileStruct.readStrFile import *
#from fileStruct.readWordFile import *
from fileStruct import read_Nstrings as rN
import subprocess

logging.info(f"loading; --- jpnTBL ---")
jpnTBL = dialog.convert_by_TBL("font/font12jp.tbl")
logging.info(f"loading; --- usaTBL ---")
usaTBL = dialog.convert_by_TBL("font/usa.tbl")
logging.info(f"loading; --- korTBL ---")
korTBL = dialog.convert_by_TBL("font/kor.tbl")

def downlaod_localazy():
    with open('work/kor/localzay_keys.json', 'r', encoding='utf-8') as json_file:
        localzay_keys = json.load(json_file)
        cmd = "localazy download"
        processes = []
        
        for k, v in localzay_keys.items():
            if k not in ['MPD', 'EVENT_EVT']:
                continue
            
            os.makedirs(f"work/kor/_{k}_", exist_ok=True)
            with open(f'work/kor/_{k}_/localazy.json', 'w', encoding='utf-8') as f:
                json.dump(v, f)
            
                process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=f'{os.getcwd()}/work/kor/_{k}_', shell=False )
                processes.append( process )
        
        for process in tqdm(processes, desc="Processing"):
            process.wait()        
        
        for k, v in localzay_keys.items():
            if k not in ['BATTLE', 'MPD', 'MENU9', 'EVENT_EVT']:
                continue
            
            shutil.copy(f"work/kor/_{k}_/{v['download']['files']}", 'work/kor')
            shutil.rmtree(f'work/kor/_{k}_')

#downlaod_localazy()        
#exit()
    
def mergeKorString():
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
    PrimeKeys = ['MENU7']
    MenuKeys = ['BATTLE_1', 'BATTLE_3', 'BATTLE_4', 'MENU0', 'MENU1', 'MENU2', 'MENU3', 'MENU4', 'MENU5', 'MENU8', 
                'MENU9_1', 'MENU9_2', 'MENU9_3', 'MENU9_4', 'MENU9_5', 'MENU9_6', 'MENU9_7', 'MENU9_8', 'MENU9_9'
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

def makeKorFont():
    jpnIndexes, jpnLetters = jpnTableslots(jpnTBL)
    korTBL = deepcopy(jpnTBL)
    korKeys = list(korTBL.fwd_tbl.keys())
    korValues = list(korTBL.fwd_tbl.values())
    
    slots = font12slots()
    slotPos = 0
    kor_strings = mergeKorString()
    korHisto = collectKorLetters(kor_strings)
    
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

    
    korTBL = dialog.convert_by_TBL("font/kor.tbl")

    system_dat = cvtFontBin.SYSTEM_DAT(f'{PATH_JPN_VARGRANTSTORY}')
    system_dat.fontData.setImage(imgJpKr)
    #imgUI = Image.open('work/texture/system_dat_pack_1.png')
    #system_dat.texture_ui.setImage(imgUI)
    #system_dat.texture_ui.image.save('work/texture/test_2.png')
    system_dat.packData(f'{PATH_KOR_VARGRANTSTORY}/BATTLE/SYSTEM.DAT')

def fixMPD(idx: int, mpd: MPDstruct):
    if idx == 1:
        mpd.scriptSection.scriptOpcodes.opcodes[51].pos(y=66, h=12)

def update_MPD(index: int, kor_strings: dict):
    Name = f"MAP{index:03}"
    filepath = f"{PATH_JPN_VARGRANTSTORY}/MAP/{Name}.MPD"
    mpd = MPDstruct(str(filepath))
    mpd.cvtByte2Str(jpnTBL)

    dictTexts = kor_strings[Name]
    len_dict = len(dictTexts)
    len_string = len(mpd.scriptSection.dialogText.strings_str)
    if len_dict > len_string:
        logging.critical(f"why? {Name} string number differnt! {len_dict} != {len_string}")
    
    for k, v in dictTexts.items():
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
    for key in kor_strings.keys():
        if str(key)[:3] == 'MAP' and str(key) != 'MAP_ZND':
            idx = int(str(key)[3:])
            
            if idx > 137:   # for test
                break
            
            logging.info(f"=== MAP{idx:03}.MPD packing ===")
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
    dictTexts = kor_strings['SMALL_ARM']
    for k, v in dictTexts.items():
        Name = str(k)
        logging.info(f"=== {Name}.ARM packing ===")
        update_ARM(Name, v)

def update_ZND(filepath: Path, NPCs: dict, WEAPONs: dict):
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
    
    znd.cvtStr2Byte(korTBL)
    znd.packData(f"{PATH_KOR_VARGRANTSTORY}/MAP/{filepath.stem}.ZND")
    
    return znd

def update_MAP_ZND(kor_strings: dict):
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
        update_ZND(filepath, NPCs, WEAPONs)
        

def rebuildNNclass(kor_strings: dict):
    def replaceStr(strlist: List[str], texts: dict):
        for k, v in texts.items():
            string = v.get('string')
            if string is not None:
                strlist[int(k)] = string
    
    for name in rN.FileLoadFuncNames:
        print(f"update {name}")
        
        ClassJp, ClassEn = rN.getNNClass(name)        
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
            replaceStr(loadJp.strings[1]._str, kor_strings['BATTLE_3'])
            replaceStr(loadJp.strings[2]._str, kor_strings['BATTLE_4'])
        
        if name == 'MON':
            monText = kor_strings.get('MON')
            for k, v in monText.items():
                monName = v.get('name')
                monDesc = v.get('description')
                
                if monName is not None:
                    loadJp.words[0]._str[int(k)] = monName
                if monDesc is not None:
                    loadJp.strings[0]._str[int(k)] = monDesc
        
        loadJp.cvtStr2Byte(korTBL)
        loadJp.packData(PATH_KOR_VARGRANTSTORY)

def update_EVT(kor_strings: dict):
    evts_jp = EVENT_EVT(PATH_JPN_VARGRANTSTORY)
    evts_jp.cvtByte2Str(jpnTBL)
    
    texts = kor_strings['EVENT_EVT']
    for k0, v0 in texts.items():
        int_k0 = int(k0)
        if 15 < int_k0:
            break
        
        if 504 <= int_k0:   # after here, debug text
            break
        
        for k1, v1 in v0.items():
            int_k1 = int(k1)
            string = v1.get('string')
            if string is not None:
                evts_jp.evtFiles[int_k0].strings_str[int_k1] = string
        
        evts_jp.evtFiles[int_k0].cvtStr2Byte(korTBL)
    
    #evts_jp.cvtStr2Byte(korTBL)
    evts_jp.packData(PATH_KOR_VARGRANTSTORY)

        
def rebuildKor():
    kor_strings = mergeKorString()
    
    rebuildNNclass(kor_strings)
    updateMAP_MDP(kor_strings)
    update_SMALL_ARM(kor_strings)
    update_MAP_ZND(kor_strings)
    update_EVT(kor_strings)

#cvtKorFontImage()
#downlaod_localazy()
#makeKorFont()
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

def test5():
    kor_strings = mergeKorString()
    classhelp = rN.MCMAN(PATH_KOR_VARGRANTSTORY)
    classhelp.cvtByte2Str(korTBL)
    
    for idx in range(classhelp.strings[0].itemNums):
        print(f"{idx}({len(classhelp.strings[0]._byte[idx])}): {classhelp.strings[0]._str[idx]}")

    return
    texts = kor_strings['ITEMHELP']
    for k, v in texts.items():
        idx = int(k)
        string = v.get('string')
        if string is not None:
            itemhelp.strings[0]._str[idx] = string
    itemhelp.cvtStr2Byte(korTBL)
    for idx in range(itemhelp.strings[0].itemNums):
        print(f"{idx}({len(itemhelp.strings[0]._byte[idx])}): {itemhelp.strings[0]._str[idx]}")
#test5()
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