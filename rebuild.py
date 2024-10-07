import json
import os
from utils import *
from tqdm import tqdm

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

    localazy_downlist = [BATTLE_localazy_json, MPD_localazy_json, ZND_localazy_json, ITEMHELP_localazy_json, ITEMNAME_localazy_json, MCMAN_localazy_json,
                         MENU0_localazy_json, MENU1_localazy_json, MENU2_localazy_json, MENU3_localazy_json, MENU4_localazy_json, MENU5_localazy_json, 
                         MENU7_localazy_json, MENU8_localazy_json, MENU9_localazy_json, MENU12_localazy_json, MENUB_localazy_json, MENUD_localazy_json, MENUE_localazy_json,
                         MENUE_localazy_json, SLPS_localazy_json, ARM_localazy_json, MON_localazy_json]
    
    for target in tqdm(localazy_downlist, desc="Processing"):
        with open('localazy.json', 'w') as f:
            json.dump(target, f)
        cmd = "localazy download"
        run_cmd(cmd, os.getcwd())
    
    os.remove('localazy.json')
    
downlaod_localazy()