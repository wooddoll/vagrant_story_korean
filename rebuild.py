import logging
from rich.logging import RichHandler
logging.basicConfig(
        level=logging.INFO, 
        format="[%(filename)s:%(lineno)s] >> %(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

import json
import os
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
from fileStruct.read_MON_BIN import MON_BIN
from fileStruct.read_BATTLE_PRG import BATTLE_PRG_en, BATTLE_PRG_jp
from fileStruct.read_MENU9_PRG import MENU9_PRG_jp, MENU9_PRG_en
from fileStruct.readStrFile import *
from fileStruct.readWordFile import *
import subprocess

logging.info(f"loading; --- jpnTBL ---")
jpnTBL = dialog.convert_by_TBL("font/font12jp.tbl")
logging.info(f"loading; --- korTBL ---")
korTBL = dialog.convert_by_TBL("font/kor.tbl")

def downlaod_localazy():
    with open('work/kor/localzay_keys.json', 'r', encoding='utf-8') as json_file:
        localzay_keys = json.load(json_file)
        cmd = "localazy download"
        processes = []
        for k, v in localzay_keys.items():
            os.makedirs(f"work/kor/_{k}_", exist_ok=True)
            with open(f'work/kor/_{k}_/localazy.json', 'w', encoding='utf-8') as f:
                json.dump(v, f)
            
                process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=f'{os.getcwd()}/work/kor/_{k}_', shell=False )
                processes.append( process )
        
        for process in tqdm(processes, desc="Processing"):
            process.wait()        
        
        for k, v in localzay_keys.items():
            shutil.copy(f"work/kor/_{k}_/{v['download']['files']}", 'work/kor')
            shutil.rmtree(f'work/kor/_{k}_')

#downlaod_localazy()        
#exit()
    
def mergeKorString():
    kor_strings = {}
    
    json_list = list(Path('work/kor').glob('*.json'))
    for filepath in tqdm(json_list, desc="Processing"):
        with open(filepath, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            kor_strings.update(json_data)
    
    return kor_strings


def collectKorLetters(kor_strings: dict):
    PrimeKeys = ['MENU7']
    MenuKeys = ['BATTLE_1', 'BATTLE_3', 'MENU0', 'MENU1', 'MENU2', 'MENU3', 'MENU4', 'MENU5', 'MENU8', 'MENU9_1', 'MENU9_2', 'MENUB', 'MENUD', 'MENUE', 'SL_Main']
    
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
                                    print('why l3?')
                        else:
                            print('why l2?')
                else:
                    print('why l1?')
        else:
            print('why l0?')

    
    histoKor.sort()
    
    countPrime = 0
    countAll = 0
    for k, v in histoKor.histo.items():
        if v['count'] >= 1000:
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
    imgUI = Image.open('work/texture/system_dat_pack_1.png')
    system_dat.texture_ui.setImage(imgUI)
    system_dat.texture_ui.image.save('work/texture/test_2.png')
    system_dat.packData(f'{PATH_KOR_VARGRANTSTORY}/BATTLE/SYSTEM.DAT')

def update_BATTLE(kor_strings: dict):
    battle = BATTLE_PRG_jp(PATH_JPN_VARGRANTSTORY)
    battle.cvtByte2Str(jpnTBL)

    textKeys = { 'BATTLE_1': 'strings_str', 'BATTLE_2': 'words_str', 'BATTLE_3': 'strings2_str' }
    for key, attr in textKeys.items():
        dictTexts = kor_strings[key]
        len_dict = len(dictTexts)
        texts = getattr(battle, attr)
        len_string = len(texts)
        if len_dict != len_string:
            logging.info(f"why? {str(key)} string number differnt! {len_dict} != {len_string}")
        for k, v in dictTexts.items():
            idx = int(k)
            texts[idx] = v['string']

    battle.cvtStr2Byte(korTBL)
    battle.packData(f"{PATH_KOR_VARGRANTSTORY}/BATTLE/BATTLE.PRG")
    
    return battle

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
        mpd.scriptSection.dialogText.strings_str[idx] = v['string']
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
            
            if idx > 10:   # for test
                break
            
            print(f"=== MAP{idx:03}.MPD packing ===")
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
        arm.names_str[idx] = v['string']
   
    arm.cvtStr2Byte(korTBL)
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
    
    znd.cvtStr2Byte(jpnTBL)
    znd.packData(f"work/test/MAP/{filepath.stem}.ZND")
    return
    znd.cvtStr2Byte(korTBL)
    znd.packData(f"{PATH_KOR_VARGRANTSTORY}/MAP/{filepath.stem}.ZND")
    
    return znd

def update_MAP_ZND(kor_strings: dict):
    dictTexts = kor_strings['MAP_ZND']
    
    with open('work/strings/MAP_ZND_ja.json', 'r', encoding='utf-8') as json_file:
        dictTexts_jp = json.load(json_file)['MAP_ZND']
    dictTexts = dictTexts_jp
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
        

def read_MENU_PRG_jp(name: str, suffix: str = 'PRG'):
    class_jp = None
    
    if f'{name}_{suffix}' in globals():
        class_jp = globals()[f'{name}_{suffix}']

    if class_jp is None:
        if f'{name}_{suffix}_jp' in globals():
            class_jp = globals()[f'{name}_{suffix}_jp']
        if class_jp is None:    
            logging.critical(f'wrong function name {name}')
            return None

    return class_jp(PATH_JPN_VARGRANTSTORY)

def updateMENUstrings(Name: str, kor_strings: dict):
    words = Name.split('_')    
    classMENU = read_MENU_PRG_jp(words[0], words[1])
    classMENU.cvtByte2Str(jpnTBL)
    
    #return classMENU
    
    dictMENU = kor_strings[words[0]]
    len_dict = len(dictMENU)
    
    if len_dict > classMENU.strings.itemNums:
        logging.critical(f"why? {Name} string number differnt! {len_dict} != {classMENU.strings.itemNums}")
    
    for k, v in dictMENU.items():
        idx = int(k)
        classMENU.strings_str[idx] = v['string']

    classMENU.cvtStr2Byte(korTBL)
    classMENU.packData(f"{PATH_KOR_VARGRANTSTORY}/MENU/{words[0]}.{words[1]}")
    
    return classMENU

def update_SMALL_MON(kor_strings: dict):
    filepath = f"{PATH_JPN_VARGRANTSTORY}/SMALL/MON.BIN"
    mon = MON_BIN(str(filepath))
    mon.cvtByte2Str(jpnTBL)

    #return mon

    dictTexts = kor_strings['MON']
    len_dict = len(dictTexts)
    if len_dict > 2*mon.ItemNumber:
        logging.critical(f"why? {'MON'} string number differnt! {len_dict} > 2*{mon.ItemNumber}")
    
    for k, v in dictTexts.items():
        idx = int(k)
        mon.name_str[idx] = v['name']
        mon.strings_str[idx] = v['description']
    
    mon.cvtStr2Byte(korTBL)    
    mon.packData(f"{PATH_KOR_VARGRANTSTORY}/SMALL/MON.BIN")
    
    return mon

def update_TITLE(kor_strings: dict):
    filepath = f"{PATH_JPN_VARGRANTSTORY}/TITLE/TITLE.PRG"
    title = TITLE_PRG_jp(str(filepath))
    title.cvtByte2Str(jpnTBL)

    #return title

    dictTexts = kor_strings['TITLE']
    len_dict = len(dictTexts)
    len_words = len(title.strings_str)
    if len_dict > len_words:
        logging.critical(f"why? {'TITLE'} string number differnt! {len_dict} > {len_words}")
    
    for k, v in dictTexts.items():
        idx = int(k)
        title.strings_str[idx] = v['string']
    
    title.cvtStr2Byte(korTBL)    
    title.packData(f"{PATH_KOR_VARGRANTSTORY}/TITLE/TITLE.PRG")

    return title

def update_SL_Main(kor_strings: dict):
    sl_main = SL_Main_jp(PATH_JPN_VARGRANTSTORY)
    sl_main.cvtByte2Str(jpnTBL)

    #return sl_main

    dictTexts = kor_strings['SL_Main']
    len_dict = len(dictTexts)
    len_words = len(sl_main.strings_str)
    if len_dict > len_words:
        logging.critical(f"why? {'SL_Main'} string number differnt! {len_dict} > {len_words}")
    
    for k, v in dictTexts.items():
        idx = int(k)
        sl_main.strings_str[idx] = v['string']
    
    sl_main.cvtStr2Byte(korTBL)    
    sl_main.packData(f"{PATH_KOR_VARGRANTSTORY}/SLPS_023.77")

    return sl_main

def update_MENU9(kor_strings: dict):
    MENU9 = MENU9_PRG_jp(PATH_JPN_VARGRANTSTORY)
    MENU9.cvtByte2Str(jpnTBL)

    #return MENU9

    dictTexts1 = kor_strings['MENU9_1']
    dictTexts2 = kor_strings['MENU9_2']
    len_dict1 = len(dictTexts1)
    len_dict2 = len(dictTexts2)
    len_words1 = len(MENU9.strings1_str)
    len_words2 = len(MENU9.strings2_str)
    if len_dict1 > len_words1:
        logging.critical(f"why? {'MENU9_1'} string number differnt! {len_dict1} > {len_words1}")
    if len_dict2 > len_words2:
        logging.critical(f"why? {'MENU9_2'} string number differnt! {len_dict2} > {len_words2}")
    
    for k, v in dictTexts1.items():
        idx = int(k)
        MENU9.strings1_str[idx] = v['string']
    for k, v in dictTexts2.items():
        idx = int(k)
        MENU9.strings2_str[idx] = v['string']
    
    MENU9.cvtStr2Byte(korTBL)    
    MENU9.packData(f"{PATH_KOR_VARGRANTSTORY}/MENU/MENU9.PRG")

    return MENU9

def rebuildKor():
    kor_strings = mergeKorString()
    with open('work/kor/all_strins_kor.json', 'w', encoding='utf-8') as f:
        json.dump(kor_strings, f, indent=2, ensure_ascii=False)
    
    update_SL_Main(kor_strings)
    update_TITLE(kor_strings)
    update_BATTLE(kor_strings)
    update_MENU9(kor_strings)
    update_SMALL_MON(kor_strings)
 
    #MENUs = [ 'MENU0_PRG', 'MENU1_PRG', 'MENU2_PRG', 'MENU3_PRG', 'MENU4_PRG_jp', 'MENU5_PRG_jp', 'MENU7_PRG_jp', 'MENU8_PRG_jp', 'MENUB_PRG', 'MENUD_PRG_jp', 'MENUE_PRG_jp', 'MENU12_BIN', 'MCMAN_BIN', 'ITEMHELP_BIN' ]
    MENUs = [ 'MENU0_PRG', 'MENU1_PRG', 'MENU2_PRG', 'MENU3_PRG', 'MENU4_PRG_jp', 'MENU5_PRG_jp', 'MENU7_PRG_jp', 'MENU8_PRG_jp', 'MENUB_PRG', 'MENUD_PRG_jp', 'MENUE_PRG_jp', 'MENU12_BIN', 'MCMAN_BIN' ]
    for Name in MENUs:
        logging.info(f"=== {Name} packing ===")
        updateMENUstrings(Name, kor_strings)

    updateMAP_MDP(kor_strings)
    update_SMALL_ARM(kor_strings)

#cvtKorFontImage()
#downlaod_localazy()
#makeKorFont()
#rebuildKor()

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

test3()