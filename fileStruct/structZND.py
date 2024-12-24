from typing import Union, List
import io
import os
import logging
from pathlib import Path
from font.dialog import convert_by_TBL
from utils import *




class ZND_MPD_data:
    def __init__(self, LBApos = 0, File_size = 0, File_name = '') -> None:
        self.LBApos: int = LBApos        # LBA pos
        self.File_size: int = File_size     # bytes !!! not lba, rounded up to multiple of 2048
        self.File_name: str = File_name

class ZND_MPD:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.MPD: List[ZND_MPD_data] = []

        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)

        self.MPD.clear()

        numMPD = header[1] // 8
        byte_stream.seek(header[0])
        for _ in range(numMPD):
            LBApos = int4(byte_stream.read(4))
            File_size = int4(byte_stream.read(4))
            if File_size%0x800:
                logging.critical('why mpd file size is not $800?')
            self.MPD.append(ZND_MPD_data(LBApos, File_size))

    def packData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        if (header[1]//8) != len(self.MPD):
            logging.critical(f"check the number of MPD files, size different; privious({header[0]}) != current({len(self.MPD)})")
        self.MPD.clear()

        byte_stream.seek(header[0])
        for data in self.MPD:
            byte_stream.write(bytes4(data.LBApos))
            byte_stream.write(bytes4(data.File_size))
        
        return byte_stream.getvalue()

class Drops:
    def __init__(self) -> None:
        self.weapon = 0
        self.shield = 0
        self.accessory = 0
        self.armor: List[int] = []

    def multiply(self, scale) -> None:
        if scale < 0:
            return
        
        self.weapon = int(self.weapon * scale)
        if 0xFF < self.weapon:
            self.weapon = 0xFF
        self.shield = int(self.shield * scale)
        if 0xFF < self.shield:
            self.shield = 0xFF
        self.accessory = int(self.accessory * scale)
        if 0xFF < self.accessory:
            self.accessory = 0xFF
        for i in range(6):
            self.armor[i] = int(self.armor[i] * scale)
            if 0xFF < self.armor[i]:
                self.armor[i] = 0xFF
            

class EnemyStats:
    def __init__(self) -> None:
        self.name = ''
        self.HP = 0
        self.MP = 0
        self.STR = 0
        self.INT = 0
        self.AGI = 0

    def multiply(self, scale) -> None:
        if scale < 0:
            return

        self.HP = int(self.HP * scale)
        if 0xFFFF < self.HP:
            self.HP = 0xFFFF
        self.MP = int(self.MP * scale)
        if 0xFFFF < self.MP:
            self.MP = 0xFFFF
        self.STR = int(self.STR * scale)
        if 0xFF < self.STR:
            self.STR = 0xFF
        self.INT = int(self.INT * scale)
        if 0xFF < self.INT:
            self.INT = 0xFF
        self.AGI = int(self.AGI * scale)
        if 0xFF < self.AGI:
            self.AGI = 0xFF

class ZND_Enemy:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.num_enemies = 0
        self.name_byte: List[bytearray] = []
        self.weapon_byte: List[bytearray] = []

        self.name_str: List[str] = []
        self.weapon_str: List[str] = []

        self.enemyStats: List[EnemyStats] = []
        self.drops: List[Drops] = []
        
        if buffer is not None:
            self.unpackData(buffer)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.name_str.clear()
        for text in self.name_byte:
            self.name_str.append(table.cvtByte2Str(text))
        
        self.weapon_str.clear()
        for text in self.weapon_byte:
            self.weapon_str.append(table.cvtByte2Str(text))
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.name_byte.clear()
        for text in self.name_str:
            self.name_byte.append(table.cvtStr2Byte(text))
        
        self.weapon_byte.clear()
        for text in self.weapon_str:
            self.weapon_byte.append(table.cvtStr2Byte(text))

    def makeEasy(self):
        for i in range(self.num_enemies):
            self.enemyStats[i].multiply(0.5)
            self.drops[i].multiply(3)
 
     def unpackData(self, buffer: bytes):
        if buffer is None:
            return

        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)

        self.name_byte.clear()
        self.weapon_byte.clear()

        byte_stream.seek(header[2])
        self.num_enemies = int4(byte_stream.read(4))

        ptr_enemies = header[2] + 4 + 8*self.num_enemies
        byte_stream.seek(ptr_enemies)
        for idx in range(self.num_enemies):
            ptr_enemy_name = ptr_enemies + 0x464*idx + 4
            byte_stream.seek(ptr_enemy_name)
            byte_name = byte_stream.read(0x18)
            self.name_byte.append(bytearray(byte_name))
            
            ptr_weapon_name = ptr_enemies + 0x464*idx + 0x34 + 0xf4
            byte_stream.seek(ptr_weapon_name)
            byte_weapon = byte_stream.read(0x18)
            self.weapon_byte.append(bytearray(byte_weapon))

        self.enemyStats.clear()
        for idx in range(self.num_enemies):
            self.enemyStats.append(EnemyStats())
            ptr_enemy_stat = ptr_enemies + 0x464*idx + 0x1c
            byte_stream.seek(ptr_enemy_stat)
            self.enemyStats[-1].HP = int2(byte_stream.read(2))
            self.enemyStats[-1].MP = int2(byte_stream.read(2))
            self.enemyStats[-1].STR = int1(byte_stream.read(1))
            self.enemyStats[-1].INT = int1(byte_stream.read(1))
            self.enemyStats[-1].AGI = int1(byte_stream.read(1))

        self.drops.clear()
        for idx in range(self.num_enemies):
            self.drops.append(Drops())
            ptr_enemy_idx = ptr_enemies + 0x464*idx
            byte_stream.seek(ptr_enemy_idx + 0x34 + 0xf0 + 1)
            self.drops[-1].weapon = int1(byte_stream.read(1))
            byte_stream.seek(ptr_enemy_idx + 0x140 + 0xc0 + 1)
            self.drops[-1].shield = int1(byte_stream.read(1))
            byte_stream.seek(ptr_enemy_idx + 0x204 + 0x30)
            self.drops[-1].accessory = int1(byte_stream.read(1))
            for ibody in range(6):
                byte_stream.seek(ptr_enemy_idx + 0x238 + ibody*0x5c + 0x20 + 0x30 + 1)
                self.drops[-1].armor.append( int1(byte_stream.read(1)) )

    def packData(self, buffer: bytes):
        if buffer is None:
            return
    
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)

        byte_stream.seek(header[2])
        num_enemies = int4(byte_stream.read(4))

        if num_enemies != self.num_enemies or num_enemies != len(self.name_byte) or num_enemies != len(self.weapon_byte):
            logging.critical(f"check the number of enemies files, size different; privious({num_enemies}) != current({len(self.name_byte)}, {len(self.weapon_byte)})")

        for idx in range(num_enemies):
            len_name = len(self.name_byte[idx])
            if len_name > 0x18:
                if not all([b==0 for b in self.name_byte[idx][:4]]):
                    logging.critical(f"check the enemy name, size overflowed({0x18} < {len_name})")
                    self.name_byte[idx] = self.name_byte[idx][:0x17]
                    self.name_byte[idx].append(0xE7)
                else:
                    self.name_byte[idx] = bytearray()
            elif len_name < 0x18:
                self.name_byte[idx].extend(bytearray(0x18-len_name))
                
            len_weapon = len(self.weapon_byte[idx])
            if len_weapon > 0x18:
                if not all([b==0 for b in self.weapon_byte[idx][:4]]):
                    logging.critical(f"check the enemy weapon, size overflowed({0x18}) < {len_weapon}")
                    self.weapon_byte[idx] = self.weapon_byte[idx][:0x17]
                    self.weapon_byte[idx].append(0xE7)
                else:
                    self.weapon_byte[idx] = bytearray()
            elif len_weapon < 0x18:
                self.weapon_byte[idx].extend(bytearray(0x18-len_weapon))

        ptr_enemies = header[2] + 4 + 8*num_enemies
        byte_stream.seek(ptr_enemies)
        for idx in range(num_enemies):
            ptr_enemy_name = ptr_enemies + 0x464*idx + 4
            byte_stream.seek(ptr_enemy_name)
            if self.name_byte[idx] and self.name_byte[idx][0] != 0:
                byte_stream.write(self.name_byte[idx])
            #else:
            #    print(f'name: 0x00, {self.name_str[idx]}')
            ptr_weapon_name = ptr_enemies + 0x464*idx + 0x34 + 0xf4
            byte_stream.seek(ptr_weapon_name)
            if self.weapon_str[idx] and self.weapon_byte[idx][0] != 0:
                byte_stream.write(self.weapon_byte[idx])
            #else:
            #    print(f'weapon: 0x00, {self.weapon_str[idx]}')

        for idx in range(num_enemies):
            ptr_enemy_stat = ptr_enemies + 0x464*idx + 0x1c
            byte_stream.seek(ptr_enemy_stat)
            byte_stream.write(bytes2(self.enemyStats[idx].HP))
            byte_stream.write(bytes2(self.enemyStats[idx].MP))
            byte_stream.write(bytes1(self.enemyStats[idx].STR))
            byte_stream.write(bytes1(self.enemyStats[idx].INT))
            byte_stream.write(bytes1(self.enemyStats[idx].AGI))

        for idx in range(num_enemies):
            ptr_enemy_idx = ptr_enemies + 0x464*idx
            byte_stream.seek(ptr_enemy_idx + 0x34 + 0xf0 + 1)
            byte_stream.write(bytes1(self.drops[idx].weapon))
            byte_stream.seek(ptr_enemy_idx + 0x140 + 0xc0 + 1)
            byte_stream.write(bytes1(self.drops[idx].shield))
            byte_stream.seek(ptr_enemy_idx + 0x204 + 0x30)
            byte_stream.write(bytes1(self.drops[idx].accessory))
            
            for ibody in range(6):
                byte_stream.seek(ptr_enemy_idx + 0x238 + ibody*0x5c + 0x20 + 0x30 + 1)
                byte_stream.write(bytes1(self.drops[idx].armor[ibody]))

        return byte_stream.getvalue()
        
class psxTIM:
    def __init__(self, buffer: bytes = bytes()):
        self.buffer = buffer
        byte_stream = io.BytesIO(self.buffer)
        
        Magic = int1(byte_stream.read(4))  # 16
        self.BPP = int1(byte_stream.read(4))
        DataLen = int4(byte_stream.read(4))
        self.Image_length = DataLen - 12
        self.Image_x = int2(byte_stream.read(2))
        self.Image_y = int2(byte_stream.read(2))
        self.Image_width = int2(byte_stream.read(2))
        self.Image_height = int2(byte_stream.read(2))
        self.Image_data = byte_stream.read(self.Image_length)
        
        #print(f"{self.Image_width}x{self.Image_height}, {2*self.Image_width*self.Image_height == self.Image_length}")
            
        
class ZND_TIM:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.TIM: List[psxTIM] = []
        self.header: List[int] = []
        if buffer is not None:
            self.unpackData(buffer)

    def unpackData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        
        TIM_ptr = header[4]
        TIM_size = header[5]
        byte_stream.seek(TIM_ptr)
        
        header = readHeader(byte_stream, 5, 4)
        numTIM = header[4]
        self.TIM.clear()        
        for idx in range(numTIM):
            TIM_size = int4(byte_stream.read(4))
            TIM_data = byte_stream.read(TIM_size)
            self.TIM.append(psxTIM(TIM_data))
        
        #for idx in range(numTIM):
        #    with open(f'work/test/{idx:03}.TIM', 'wb') as f:
        #        f.write(self.TIM[idx].buffer)
        #print()

    def packData(self, buffer: bytes):
        if buffer is None:
            return
        
        byte_stream = io.BytesIO(buffer)
        header = readHeader(byte_stream, 6, 4)
        if (header[1]//8) != len(self.TIM):
            logging.critical(f"check the number of MPD files, size different; privious({header[0]}) != current({len(self.TIM)})")
        self.TIM.clear()

        byte_stream.seek(header[0])
        for data in self.TIM:
            byte_stream.write(bytes4(data.File_size))   

class ZNDstruct:
    def __init__(self, input_path:str = '') -> None:
        self.buffer = None

        self.MPD = ZND_MPD()
        self.Enemy = ZND_Enemy()
        self.TIM = ZND_TIM()
        
        if input_path:
            self.unpackData(input_path)

    def cvtByte2Str(self, table: convert_by_TBL):
        self.Enemy.cvtByte2Str(table)
    
    def cvtStr2Byte(self, table: convert_by_TBL):
        self.Enemy.cvtStr2Byte(table)
    
    def unpackData(self, input_path:str):
        with open(input_path, 'rb') as file:
            self.buffer = file.read()

            #self.MPD.unpackData(self.buffer)
            self.Enemy.unpackData(self.buffer)
            #self.TIM.unpackData(self.buffer)

    def packData(self, output_path:str):
        if self.buffer is None:
            return

        #self.buffer = self.MPD.packData(self.buffer)
        self.buffer = self.Enemy.packData(self.buffer)

        with open(output_path, 'wb') as file:
            file.write(self.buffer)