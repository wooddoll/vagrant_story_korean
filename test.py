
from font import makeTBL, cvtFontBin
from dialog import dialog, scripts
import utils
from VS_pathes import *
import pandas as pd
import os
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format="[%(filename)s:%(lineno)s] >> %(message)s"
)



PATH_testMPD = "MAP/MAP001.MPD"
def test1():
    jpnTBL = dialog.convert_by_TBL("font/jpn.tbl")

    mpd = scripts.MPDstruct()
    mpd_path = Path(PATH_TEMP_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))

    dialogLists = dialog.exportTextFromMPD(mpd, jpnTBL)
    df = pd.DataFrame(dialogLists, columns=['Index', 'rows', 'cols', 'Original'])
    out_path = os.path.join(PATH_TEMP, f'{Path(PATH_testMPD).stem}.csv')
    df.to_csv(out_path, index=False, encoding='utf-8')

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
    
    mpd = scripts.MPDstruct()
    mpd_path = Path(PATH_TEMP_VARGRANTSTORY) / Path(PATH_testMPD)
    mpd.unpackData(str(mpd_path))
    
    out_path = Path(PATH_TEMP) / Path(f'{Path(PATH_testMPD).stem}.csv')
    dialogLists = readExelDialog(out_path)
    
    for idx in range(len(mpd.scriptSection.dialogText.dialogBytes)):
        text = dialogLists[idx]
        byteText = jpnTBL.cvtStr_Bytes(text)
        mpd.scriptSection.dialogText.dialogBytes[idx] = byteText
    
    outpath = Path(PATH_TEMP) / Path(PATH_testMPD)
    mpd.packData(outpath)

def test3():
    mpd_path = f'{PATH_TEMP}/{PATH_testMPD}'
    cmd = f'{PATH_psxinject} "{PATH_TEMP_VARGRANTSTORY_IMAGE}" {PATH_testMPD} {str(mpd_path)}'
    utils.run_cmd(cmd, PATH_TEMP)

#jpnTBL = makeTBL.makeTable("font/font14_table.txt", "font/jpn.tbl")
#test1()
#test2()
#test3()

findword = dialog.Find_Word()
findword.find_in_folder("C:/TEMP/Vagrant Story (J)/", "find_in_folder.yaml")