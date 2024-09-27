
from font import makeTBL, cvtFontBin
from font.dialog import Find_Word
from fileStruct.structMPD import MPDstruct
from fileStruct.structZND import ZNDstruct
from fileStruct.structARM import ARMstruct

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



PATH_testMPD = "MAP/MAP001.MPD"
PATH_testZND = "MAP/ZONE009.ZND"



def test1():
    jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")

    mpd = MPDstruct()
    mpd_path = Path(PATH_TEMP_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))

    dialogLists = dialog.exportTextFromMPD(mpd, jpnTBL)
    df = pd.DataFrame(dialogLists, columns=['Index', 'rows', 'cols', 'Original'])
    #out_path = os.path.join(PATH_TEMP, f'{Path(PATH_testMPD).stem}.csv')
    outpath = Path(PATH_TEMP) / Path(f'Test/{Path(PATH_testMPD).stem}.csv')
    df.to_csv(outpath, index=False, encoding='utf-8')

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
    jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")
    
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

#jpnTBL = makeTBL.makeTable("font/font14_table.txt", "font/jpn.tbl")
#test1()
#test2()
#test3()

#findword = dialog.Find_Word()
#findword.find_in_folder("C:/TEMP/Vagrant Story (J)/", "find_in_folder.yaml")

def test4():
    jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")

    znd_path = f'{PATH_TEMP_VARGRANTSTORY}/{PATH_testZND}'
    znd = ZNDstruct(znd_path)

    znd.Enemy.convertName(jpnTBL)

    outpath = Path(PATH_TEMP) / Path('Test') / Path(PATH_testZND)
    znd.packData(str(outpath))


def extractZNDnames():
    jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")

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
    
    usaTBL = dialog.convert_by_TBL("font/usa.tbl")

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
    
    for i in range(len(namesInfiles)):
        namesInfiles[i] = f"{namesInfiles[i]}={_namesInfiles[i]}"
        weaponesInfiles[i] = f"{weaponesInfiles[i]}={_weaponesInfiles[i]}"
    ###
    
    words = set()
    for name in namesInfiles:
        if name:
            words.add(name)
    namesInfiles = sorted(list(words))

    words = set()
    for name in weaponesInfiles:
        if name:
            words.add(name)
    weaponesInfiles = sorted(list(words))


    outpath = Path('work/ZNDnames.txt')
    with open(outpath, 'wt', encoding='utf-8') as file:
        file.write(f"#Enemies Names\n")
        for name in namesInfiles:
            file.write(name + '\n')

        file.write(f"\n#Enemies Weapons\n")
        for name in weaponesInfiles:
            file.write(name + '\n')

extractZNDnames()            
    
def extractARMnames():
    jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")

    namesInfiles = []
    folder_path = Path(PATH_TEMP_VARGRANTSTORY) / Path('SMALL')
    file_list = [file for file in folder_path.rglob('*.ARM') if file.is_file()]
    for filepath in tqdm(file_list, desc="Processing"):
        relative_path = filepath.relative_to(folder_path)

        arm = ARMstruct(str(filepath))
        arm.convertName(jpnTBL)

        namesInfiles.extend(arm.names_str)

    ####

    usaTBL = dialog.convert_by_TBL("font/usa.tbl")

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
        wordInfiles.append(f"{jpn}={eng}")

    outpath = Path('work/ARMnames.txt')
    with open(outpath, 'wt', encoding='utf-8') as file:
        file.write(f"#Area Names\n")
        for name in wordInfiles:
            file.write(name + '\n')

#extractARMnames()

#makeTBL.makeTable("font/font12_table.txt", "font/usa.tbl", 21)

def check1():
    mpd = MPDstruct()
    mpd_path = Path(PATH_TEMP) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))

    print(mpd)
#check1()


findword = Find_Word()
findword.find_in_folder(PATH_TEMP_VARGRANTSTORY, "find_in_folder.yaml")