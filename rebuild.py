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

from fileStruct.structARM import ARMstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structMPD import MPDstruct
from fileStruct.read_MON_BIN import MON_BIN
from fileStruct.read_SL_Main import SL_Main
from fileStruct.read_TITLE_PRG import TITLE_PRG_jp, TITLE_PRG_en
from fileStruct.read_BATTLE_PRG import *
from fileStruct.read_MENU9_PRG import *
from fileStruct.readStrFile import *
from fileStruct.readWordFile import *

logging.info(f"loading; --- jpnTBL ---")
jpnTBL = dialog.convert_by_TBL("font/font12jp.tbl")
logging.info(f"loading; --- korTBL ---")
korTBL = dialog.convert_by_TBL("font/kor.tbl")

def downlaod_localazy():
    BATTLE_localazy_json = { "readKey": "a7205313787754947305-fad6c10d4b491ecfc62c4a76a2cecbe93b629a62717ab14832253776186f82e0", "download": { "includeSourceLang": False, "files": "work/kor/BATTLE_BATTLE_PRG_ko.json" }, }
    MPD_localazy_json = { "readKey": "a7205311925551080161-cf83c3d0f6e1c828308d9fb5696d7a7367fe7c0de670ca8296819b39299a553a", "download": { "includeSourceLang": False, "files": "work/kor/MAP_MPD_ko.json" }, }    
    ZND_localazy_json = { "readKey": "a7205309380647382594-68e6fbe6a7dfbfd2e843d19bfd7164f77ee09faaf5336c8fad76362200db5b39", "download": { "includeSourceLang": False, "files": "work/kor/MAP_ZND_ko.json" }, }    
    ITEMHELP_localazy_json = { "readKey": "a7205301665476832814-8fb397b202a2aba4ee1a0e181d23c35da53f713a348711333dd8f578e9618089", "download": { "includeSourceLang": False, "files": "work/kor/MENU_ITEMHELP_BIN_ko.json" }, }
    ITEMNAME_localazy_json = { "readKey": "a7205303231664857791-1b6e180cfcb9022d6c6532ebe7001e0387fc5f538b6c3089cf51652da7a70faa", "download": { "includeSourceLang": False, "files": "work/kor/MENU_ITEMNAME_BIN_ko.json" }, }
    MCMAN_localazy_json = { "readKey": "a7205299939236881077-31affecb8bb508ce6f6b48d36807b0086195b422ba1999e276e69e7ae10121e4", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MCMAN_BIN_ko.json" }, }
    MENU0_localazy_json = { "readKey": "a7205298335803436561-7d8c4e720d0a3842d26452763ecd6404582c48539572dd7efb4724b1ed12524e", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU0_PRG_ko.json" }, }    
    MENU1_localazy_json = { "readKey": "a7205296916853616137-aefb62bd5be935d33143623a436a9796c2f457da629ad8585c0d134a84c56d3a", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU1_PRG_ko.json" }, }
    MENU2_localazy_json = { "readKey": "a7205295702117425824-b7a7c72a3127d65f27d5cb2ab15839fb08854644e1e5b333ed6f02198367c286", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU2_PRG_ko.json" }, }
    MENU3_localazy_json = { "readKey": "a7205293906217116304-8d54b0d7169237757e08e542abda8d2ec5532719461c68d64fa09a6be982ad1a", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU3_PRG_ko.json" }, }
    MENU4_localazy_json = { "readKey": "a7205292536658062761-dfdc048f38b30aee98fdadb46cd9c73bbfe999f4eeb3efd56bd22ae9d5028a5e", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU4_PRG_ko.json" }, }
    MENU5_localazy_json = { "readKey": "a7205291056841859706-2d681010b692fce2180ef48962c00cd9e18b9a336ff5551626fd8a987d85f4da", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU5_PRG_ko.json" }, }
    MENU7_localazy_json = { "readKey": "a7205289789690932642-44fd7c1203ebc011d03905a787bee047a552f92d85e8e125065e97ab57dd9cca", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU7_PRG_ko.json" }, }
    MENU8_localazy_json = { "readKey": "a7205285046100880714-507b1af40c101038ac02b03d92665e599005417c58b85ab285b6f5060836a389", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU8_PRG_ko.json" }, }
    MENU9_localazy_json = { "readKey": "a7205283653323517228-b76abe18a23038be5bf9eab1b3990bde1146507723a6807860c72b0ee72163d9", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU9_PRG_ko.json" }, }
    MENUB_localazy_json = { "readKey": "a7205273442980911826-dd2fcb296f0ca81ee26a77944688d724458befdc07f7aa37aa2a96c722e5f24d", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENUB_PRG_ko.json" }, }
    MENUD_localazy_json = { "readKey": "a7205272050337766045-58bbcc5a80e093b7eb4470be3eb63407ae73fb9e4f7ee4a5f302b1116767b142", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENUD_PRG_ko.json" }, }
    MENUE_localazy_json = { "readKey": "a7205270517034441357-47ed8268902a103bcb51a2043b168d2f4c9c16823d537a01ef303a0cfba75845", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENUE_PRG_ko.json" }, }    
    SLPS_localazy_json = { "readKey": "a7205317337411199727-ab57def3432797f3cd8e4c3af40b39511fd56f3b0802c88c413a060d5ea744a4", "download": { "includeSourceLang": False, "files": "work/kor/SLPS_main_ko.json" }, }    
    MENU12_localazy_json = { "readKey": "a7205274821933849323-9a6e3e0db7d164c2d47ec2408db462cc617549d7789e201faa13eae88004230a", "download": { "includeSourceLang": False, "files": "work/kor/MENU_MENU12_BIN_ko.json" }, }
    ARM_localazy_json = { "readKey": "a7205307301413449279-8f42e0957e7d5ac8b2cd1146934575fc5661b5d9c4a2ede677f1b202e3e618f8", "download": { "includeSourceLang": False, "files": "work/kor/SMALL_ARM_ko.json" }, }
    MON_localazy_json = { "readKey": "a7205304936295755322-34c4ee1d4d15d7746596d5ffe52761081e8e63480ce90d1a13a7413c9549d6a5", "download": { "includeSourceLang": False, "files": "work/kor/SMALL_MON_BIN_ko.json" }, }    
    TITLE_localazy_json = { "readKey": "a7201346093008773609-979b1d4a925ab840f6aba4046f243a3d4290727f73d429f6d8732a521c7f9a3d", "download": { "includeSourceLang": False, "files": "work/kor/TITLE_TITLE_PRG_ko.json" }, }
    
    localazy_downlist = [BATTLE_localazy_json, MPD_localazy_json, ZND_localazy_json, ITEMHELP_localazy_json, ITEMNAME_localazy_json, MCMAN_localazy_json,
                         MENU0_localazy_json, MENU1_localazy_json, MENU2_localazy_json, MENU3_localazy_json, MENU4_localazy_json, MENU5_localazy_json, 
                         MENU7_localazy_json, MENU8_localazy_json, MENU9_localazy_json, MENU12_localazy_json, MENUB_localazy_json, MENUD_localazy_json, MENUE_localazy_json,
                         MENUE_localazy_json, SLPS_localazy_json, ARM_localazy_json, MON_localazy_json, TITLE_localazy_json]
    
    os.makedirs("work/kor", exist_ok=True)
    for target in tqdm(localazy_downlist, desc="Processing"):
        with open('localazy.json', 'w', encoding='utf-8') as f:
            json.dump(target, f)
        cmd = "localazy download"
        run_cmd(cmd, os.getcwd())
    
    os.remove('localazy.json')
    
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

def update_MPD(index: int, kor_strings: dict):
    Name = f"MAP{index:03}"
    filepath = f"{PATH_JPN_VARGRANTSTORY}/MAP/{Name}.MPD"
    mpd = MPDstruct(str(filepath))
    mpd.scriptSection.dialogText.cvtByte2Str(jpnTBL)

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
    
    mpd.scriptSection.dialogText.cvtStr2Byte(korTBL)

    return mpd

def updateMAP_MDP(kor_strings: dict):
    for k, v in kor_strings.items():
        if str(k)[:3] == 'MAP' and str(k) != 'MAP_ZND':
            idx = int(str(k)[3:])
            
            if idx > 10:   # for test
                break
            
            print(f"=== MAP{idx:03}.MPD packing ===")
            mpd = update_MPD(idx, kor_strings)
            mpd.packData(f"{PATH_KOR_VARGRANTSTORY}/MAP/MAP{idx:03}.MPD")

def read_MENU_PRG_jp(name: str, suffix: str = 'PRG'):
    class_jp = None
    
    if f'{name}_{suffix}' in globals():
        class_jp = globals()[f'{name}_{suffix}']

    if class_jp is None:
        if f'{name}_{suffix}_jp' in globals():
            class_jp = globals()[f'{name}_{suffix}_jp']
        if class_jp is None:    
            logging.warning(f'wrong function name {name}')
            return
    
    inp_path = Path(PATH_USA_VARGRANTSTORY) / Path(f"MENU/{name}.{suffix}")
    inp_path = Path(PATH_JPN_VARGRANTSTORY) / Path(f"MENU/{name}.{suffix}")
    help_jp = class_jp(str(inp_path))
    
    return help_jp
  

def updateMENUstrings(Name: str, kor_strings: dict):
    words = Name.split('_')    
    classMENU = read_MENU_PRG_jp(words[0], words[1])
    classMENU.cvtByte2Str(jpnTBL)
    dictMENU = kor_strings[words[0]]
    len_dict = len(dictMENU)
    
    if len_dict > classMENU.strings.itemNums:
        logging.critical(f"why? {Name} string number differnt! {len_dict} != {classMENU.strings.itemNums}")
    
    for k, v in dictMENU.items():
        idx = int(k)
        classMENU.strings_str[idx] = v['string']

    classMENU.cvtStr2Byte(korTBL)
    
    return classMENU
    
def rebuildKor():
    kor_strings = mergeKorString()
    with open('work/kor/all_strins_kor.json', 'w', encoding='utf-8') as f:
        json.dump(kor_strings, f, indent=2, ensure_ascii=False)
    
    update_BATTLE(kor_strings)
    return
    
    #MENUs = [ 'MENU0_PRG', 'MENU1_PRG', 'MENU2_PRG', 'MENU3_PRG', 'MENU4_PRG_jp', 'MENU5_PRG_jp', 'MENU7_PRG_jp', 'MENU8_PRG_jp', 'MENUB_PRG', 'MENUD_PRG_jp', 'MENUE_PRG_jp', 'MENU12_BIN', 'MCMAN_BIN', 'ITEMHELP_BIN' ]
    MENUs = [ 'MENU0_PRG', 'MENU1_PRG', 'MENU2_PRG', 'MENU3_PRG', 'MENU4_PRG_jp', 'MENU5_PRG_jp', 'MENU7_PRG_jp', 'MENU8_PRG_jp', 'MENUB_PRG', 'MENUD_PRG_jp', 'MENUE_PRG_jp', 'MENU12_BIN', 'MCMAN_BIN' ]
    for Name in MENUs:
        print(f"=== {Name} packing ===")
        classMENU = updateMENUstrings(Name, kor_strings)
    #    
        words = Name.split('_')
        classMENU.packData(f"{PATH_KOR_VARGRANTSTORY}/MENU/{words[0]}.{words[1]}")
 
    
 
    updateMAP_MDP(kor_strings)

#cvtKorFontImage()
downlaod_localazy()
makeKorFont()
rebuildKor()

def test1():
    system_dat = cvtFontBin.SYSTEM_DAT(f'{PATH_JPN_VARGRANTSTORY}')
    imgUI = Image.open('work/texture/system_dat_pack_1.png')
    system_dat.texture_ui.setImage(imgUI)
    system_dat.packData(f'{PATH_KOR_VARGRANTSTORY}/BATTLE/SYSTEM.DAT')