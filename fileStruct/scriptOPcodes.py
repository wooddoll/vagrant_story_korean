from typing import Union, Dict, List
import os
import io
from utils import *
from font import dialog

_Opcode_ = {
    0x00: { 'Size': 0x01, 'Mnemonic': 'nop()' },
    0x01: { 'Size': 0x0a, 'Mnemonic': '' },
    0x02: { 'Size': 0x03, 'Mnemonic': '' },
    0x03: { 'Size': 0x03, 'Mnemonic': '' },
    0x04: { 'Size': 0x04, 'Mnemonic': '' },
    0x05: { 'Size': 0x12, 'Mnemonic': '' },
    0x06: { 'Size': 0x0b, 'Mnemonic': '' },
    0x07: { 'Size': 0x0b, 'Mnemonic': '' },
    0x08: { 'Size': 0x26, 'Mnemonic': '' },
    0x09: { 'Size': 0x00, 'Mnemonic': '' },
    0x0A: { 'Size': 0x01, 'Mnemonic': '' },
    0x0B: { 'Size': 0x01, 'Mnemonic': '' },
    0x0C: { 'Size': 0x01, 'Mnemonic': '' },
    0x0D: { 'Size': 0x03, 'Mnemonic': '' },
    0x0E: { 'Size': 0x03, 'Mnemonic': '' },
    0x0F: { 'Size': 0x01, 'Mnemonic': '' },
    0x10: { 'Size': 0x0b, 'Mnemonic': 'DialogShow(idDlg, Style, x,x, y, w, h, ?, ?, ?)' },
    0x11: { 'Size': 0x04, 'Mnemonic': 'DialogText(idDlg, idText, ?)' },
    0x12: { 'Size': 0x02, 'Mnemonic': 'DialogHide(idDlg)' },
    0x13: { 'Size': 0x09, 'Mnemonic': '' },
    0x14: { 'Size': 0x02, 'Mnemonic': '' },
    0x15: { 'Size': 0x02, 'Mnemonic': '' },
    0x16: { 'Size': 0x04, 'Mnemonic': 'SplashScreenChoose' },
    0x17: { 'Size': 0x06, 'Mnemonic': 'SplashScreenLoad' },
    0x18: { 'Size': 0x07, 'Mnemonic': 'SplashScreenShow' },
    0x19: { 'Size': 0x01, 'Mnemonic': 'SplashScreenHide' },
    0x1A: { 'Size': 0x01, 'Mnemonic': 'SplashScreenFadeIn' },
    0x1B: { 'Size': 0x04, 'Mnemonic': '' },
    0x1C: { 'Size': 0x02, 'Mnemonic': '' },
    0x1D: { 'Size': 0x02, 'Mnemonic': '' },
    0x1E: { 'Size': 0x04, 'Mnemonic': '' },
    0x1F: { 'Size': 0x05, 'Mnemonic': '' },
    0x20: { 'Size': 0x09, 'Mnemonic': 'ModelLoad(idChr, ?, idSHP, ?, ?, ?, ?, ?)' },
    0x21: { 'Size': 0x06, 'Mnemonic': '' },
    0x22: { 'Size': 0x06, 'Mnemonic': 'ModelAnimate(idChr, ?, idAnim, ?, ?)' },
    0x23: { 'Size': 0x05, 'Mnemonic': 'ModelSetAnimations' },
    0x24: { 'Size': 0x07, 'Mnemonic': '' },
    0x25: { 'Size': 0x09, 'Mnemonic': '' },
    0x26: { 'Size': 0x0c, 'Mnemonic': 'ModelPosition(idChr, ?, px,px, py,py, pz,pz, rx, ?, ?)' },
    0x27: { 'Size': 0x07, 'Mnemonic': '' },
    0x28: { 'Size': 0x0a, 'Mnemonic': 'ModelMoveTo(idChr, x,x,x,x, y,y,y,y)' },
    0x29: { 'Size': 0x07, 'Mnemonic': 'ModelMoveTo2' },
    0x2A: { 'Size': 0x07, 'Mnemonic': '' },
    0x2B: { 'Size': 0x06, 'Mnemonic': '' },
    0x2C: { 'Size': 0x06, 'Mnemonic': '' },
    0x2D: { 'Size': 0x07, 'Mnemonic': '' },
    0x2E: { 'Size': 0x0a, 'Mnemonic': '' },
    0x2F: { 'Size': 0x03, 'Mnemonic': 'ModeFree(idChr, ?)' },
    0x30: { 'Size': 0x06, 'Mnemonic': 'ModelLoadAnimationsEx' },
    0x31: { 'Size': 0x06, 'Mnemonic': '' },
    0x32: { 'Size': 0x06, 'Mnemonic': '' },
    0x33: { 'Size': 0x0b, 'Mnemonic': 'ModelRotate' },
    0x34: { 'Size': 0x08, 'Mnemonic': '' },
    0x35: { 'Size': 0x07, 'Mnemonic': '' },
    0x36: { 'Size': 0x07, 'Mnemonic': '' },
    0x37: { 'Size': 0x05, 'Mnemonic': '' },
    0x38: { 'Size': 0x06, 'Mnemonic': 'ModelLookAt' },
    0x39: { 'Size': 0x0a, 'Mnemonic': '' },
    0x3A: { 'Size': 0x04, 'Mnemonic': 'ModelLoadAnimations' },
    0x3B: { 'Size': 0x01, 'Mnemonic': 'WaitForFile' },
    0x3C: { 'Size': 0x02, 'Mnemonic': '' },
    0x3D: { 'Size': 0x02, 'Mnemonic': '' },
    0x3E: { 'Size': 0x0a, 'Mnemonic': 'ModelIlluminate' },
    0x3F: { 'Size': 0x04, 'Mnemonic': '' },
    0x40: { 'Size': 0x06, 'Mnemonic': '' },
    0x41: { 'Size': 0x06, 'Mnemonic': '' },
    0x42: { 'Size': 0x03, 'Mnemonic': 'ModelControlViaScript' },
    0x43: { 'Size': 0x01, 'Mnemonic': '' },
    0x44: { 'Size': 0x02, 'Mnemonic': 'SetEngineMode' },
    0x45: { 'Size': 0x03, 'Mnemonic': '' },
    0x46: { 'Size': 0x03, 'Mnemonic': '' },
    0x47: { 'Size': 0x04, 'Mnemonic': '' },
    0x48: { 'Size': 0x01, 'Mnemonic': '' },
    0x49: { 'Size': 0x03, 'Mnemonic': '' },
    0x4A: { 'Size': 0x04, 'Mnemonic': '' },
    0x4B: { 'Size': 0x03, 'Mnemonic': '' },
    0x4C: { 'Size': 0x03, 'Mnemonic': '' },
    0x4D: { 'Size': 0x02, 'Mnemonic': '' },
    0x4E: { 'Size': 0x01, 'Mnemonic': '' },
    0x4F: { 'Size': 0x01, 'Mnemonic': '' },
    0x50: { 'Size': 0x04, 'Mnemonic': 'ModelControlViaBattleMode' },
    0x51: { 'Size': 0x04, 'Mnemonic': '' },
    0x52: { 'Size': 0x05, 'Mnemonic': '' },
    0x53: { 'Size': 0x03, 'Mnemonic': '' },
    0x54: { 'Size': 0x04, 'Mnemonic': 'BattleOver' },
    0x55: { 'Size': 0x02, 'Mnemonic': '' },
    0x56: { 'Size': 0x03, 'Mnemonic': '' },
    0x57: { 'Size': 0x04, 'Mnemonic': '' },
    0x58: { 'Size': 0x02, 'Mnemonic': 'SetHeadsUpDisplayMode(idMode)' },
    0x59: { 'Size': 0x04, 'Mnemonic': '' },
    0x5A: { 'Size': 0x07, 'Mnemonic': '' },
    0x5B: { 'Size': 0x04, 'Mnemonic': '' },
    0x5C: { 'Size': 0x07, 'Mnemonic': '' },
    0x5D: { 'Size': 0x04, 'Mnemonic': '' },
    0x5E: { 'Size': 0x03, 'Mnemonic': '' },
    0x5F: { 'Size': 0x02, 'Mnemonic': '' },
    0x60: { 'Size': 0x03, 'Mnemonic': '' },
    0x61: { 'Size': 0x03, 'Mnemonic': '' },
    0x62: { 'Size': 0x02, 'Mnemonic': '' },
    0x63: { 'Size': 0x01, 'Mnemonic': '' },
    0x64: { 'Size': 0x02, 'Mnemonic': '' },
    0x65: { 'Size': 0x02, 'Mnemonic': '' },
    0x66: { 'Size': 0x03, 'Mnemonic': '' },
    0x67: { 'Size': 0x05, 'Mnemonic': '' },
    0x68: { 'Size': 0x0a, 'Mnemonic': 'LoadRoom(idZone, idRoom, ?, ?, ?, ?, ?, ?, ?)' },
    0x69: { 'Size': 0x04, 'Mnemonic': 'LoadScene' },
    0x6A: { 'Size': 0x04, 'Mnemonic': '' },
    0x6B: { 'Size': 0x02, 'Mnemonic': '' },
    0x6C: { 'Size': 0x04, 'Mnemonic': '' },
    0x6D: { 'Size': 0x02, 'Mnemonic': 'DisplayRoom' },
    0x6E: { 'Size': 0x01, 'Mnemonic': '' },
    0x6F: { 'Size': 0x02, 'Mnemonic': '' },
    0x70: { 'Size': 0x08, 'Mnemonic': 'ModelColor' },
    0x71: { 'Size': 0x04, 'Mnemonic': '' },
    0x72: { 'Size': 0x03, 'Mnemonic': '' },
    0x73: { 'Size': 0x02, 'Mnemonic': '' },
    0x74: { 'Size': 0x02, 'Mnemonic': '' },
    0x75: { 'Size': 0x01, 'Mnemonic': '' },
    0x76: { 'Size': 0x01, 'Mnemonic': '' },
    0x77: { 'Size': 0x05, 'Mnemonic': '' },
    0x78: { 'Size': 0x02, 'Mnemonic': '' },
    0x79: { 'Size': 0x03, 'Mnemonic': '' },
    0x7A: { 'Size': 0x02, 'Mnemonic': '' },
    0x7B: { 'Size': 0x05, 'Mnemonic': '' },
    0x7C: { 'Size': 0x02, 'Mnemonic': '' },
    0x7D: { 'Size': 0x03, 'Mnemonic': '' },
    0x7E: { 'Size': 0x04, 'Mnemonic': '' },
    0x7F: { 'Size': 0x01, 'Mnemonic': '' },
    0x80: { 'Size': 0x05, 'Mnemonic': 'SoundEffects0' },
    0x81: { 'Size': 0x04, 'Mnemonic': '' },
    0x82: { 'Size': 0x05, 'Mnemonic': '' },
    0x83: { 'Size': 0x01, 'Mnemonic': '' },
    0x84: { 'Size': 0x03, 'Mnemonic': '' },
    0x85: { 'Size': 0x03, 'Mnemonic': 'SoundEffects5' },
    0x86: { 'Size': 0x02, 'Mnemonic': 'SoundEffects6' },
    0x87: { 'Size': 0x02, 'Mnemonic': '' },
    0x88: { 'Size': 0x02, 'Mnemonic': 'SoundEffects8' },
    0x89: { 'Size': 0x01, 'Mnemonic': '' },
    0x8A: { 'Size': 0x00, 'Mnemonic': '' },
    0x8B: { 'Size': 0x00, 'Mnemonic': '' },
    0x8C: { 'Size': 0x00, 'Mnemonic': '' },
    0x8D: { 'Size': 0x00, 'Mnemonic': '' },
    0x8E: { 'Size': 0x00, 'Mnemonic': '' },
    0x8F: { 'Size': 0x05, 'Mnemonic': '' },
    0x90: { 'Size': 0x03, 'Mnemonic': 'MusicLoad' },
    0x91: { 'Size': 0x02, 'Mnemonic': '' },
    0x92: { 'Size': 0x04, 'Mnemonic': 'MusicPlay' },
    0x93: { 'Size': 0x03, 'Mnemonic': '' },
    0x94: { 'Size': 0x03, 'Mnemonic': '' },
    0x95: { 'Size': 0x03, 'Mnemonic': '' },
    0x96: { 'Size': 0x01, 'Mnemonic': '' },
    0x97: { 'Size': 0x02, 'Mnemonic': '' },
    0x98: { 'Size': 0x01, 'Mnemonic': '' },
    0x99: { 'Size': 0x02, 'Mnemonic': 'AudioUnknown1' },
    0x9A: { 'Size': 0x03, 'Mnemonic': '' },
    0x9B: { 'Size': 0x05, 'Mnemonic': '' },
    0x9C: { 'Size': 0x05, 'Mnemonic': '' },
    0x9D: { 'Size': 0x02, 'Mnemonic': 'AudioSetPitch' },
    0x9E: { 'Size': 0x01, 'Mnemonic': 'AudioUnknown2' },
    0x9F: { 'Size': 0x02, 'Mnemonic': '' },
    0xA0: { 'Size': 0x05, 'Mnemonic': '' },
    0xA1: { 'Size': 0x02, 'Mnemonic': 'SplashScreenEffects' },
    0xA2: { 'Size': 0x02, 'Mnemonic': 'CameraZoomIn' },
    0xA3: { 'Size': 0x01, 'Mnemonic': '' },
    0xA4: { 'Size': 0x01, 'Mnemonic': '' },
    0xA5: { 'Size': 0x01, 'Mnemonic': '' },
    0xA6: { 'Size': 0x02, 'Mnemonic': '' },
    0xA7: { 'Size': 0x00, 'Mnemonic': '' },
    0xA8: { 'Size': 0x02, 'Mnemonic': '' },
    0xA9: { 'Size': 0x02, 'Mnemonic': '' },
    0xAA: { 'Size': 0x05, 'Mnemonic': '' },
    0xAB: { 'Size': 0x00, 'Mnemonic': '' },
    0xAC: { 'Size': 0x00, 'Mnemonic': '' },
    0xAD: { 'Size': 0x00, 'Mnemonic': '' },
    0xAE: { 'Size': 0x00, 'Mnemonic': '' },
    0xAF: { 'Size': 0x00, 'Mnemonic': '' },
    0xB0: { 'Size': 0x00, 'Mnemonic': '' },
    0xB1: { 'Size': 0x02, 'Mnemonic': '' },
    0xB2: { 'Size': 0x08, 'Mnemonic': '' },
    0xB3: { 'Size': 0x04, 'Mnemonic': '' },
    0xB4: { 'Size': 0x07, 'Mnemonic': '' },
    0xB5: { 'Size': 0x03, 'Mnemonic': '' },
    0xB6: { 'Size': 0x07, 'Mnemonic': '' },
    0xB7: { 'Size': 0x06, 'Mnemonic': '' },
    0xB8: { 'Size': 0x01, 'Mnemonic': '' },
    0xB9: { 'Size': 0x03, 'Mnemonic': '' },
    0xBA: { 'Size': 0x02, 'Mnemonic': '' },
    0xBB: { 'Size': 0x03, 'Mnemonic': '' },
    0xBC: { 'Size': 0x01, 'Mnemonic': '' },
    0xBD: { 'Size': 0x02, 'Mnemonic': '' },
    0xBE: { 'Size': 0x01, 'Mnemonic': '' },
    0xBF: { 'Size': 0x03, 'Mnemonic': '' },
    0xC0: { 'Size': 0x07, 'Mnemonic': 'CameraDirection' },
    0xC1: { 'Size': 0x01, 'Mnemonic': 'CameraSetAngle' },
    0xC2: { 'Size': 0x03, 'Mnemonic': 'CameraLookAt' },
    0xC3: { 'Size': 0x03, 'Mnemonic': '' },
    0xC4: { 'Size': 0x04, 'Mnemonic': 'ModelAnimateObject' },
    0xC5: { 'Size': 0x09, 'Mnemonic': '' },
    0xC6: { 'Size': 0x00, 'Mnemonic': '' },
    0xC7: { 'Size': 0x0a, 'Mnemonic': '' },
    0xC8: { 'Size': 0x0b, 'Mnemonic': '' },
    0xC9: { 'Size': 0x02, 'Mnemonic': '' },
    0xCA: { 'Size': 0x0a, 'Mnemonic': '' },
    0xCB: { 'Size': 0x03, 'Mnemonic': '' },
    0xCC: { 'Size': 0x00, 'Mnemonic': '' },
    0xCD: { 'Size': 0x00, 'Mnemonic': '' },
    0xCE: { 'Size': 0x00, 'Mnemonic': '' },
    0xCF: { 'Size': 0x00, 'Mnemonic': '' },
    0xD0: { 'Size': 0x07, 'Mnemonic': 'CameraPosition' },
    0xD1: { 'Size': 0x01, 'Mnemonic': 'SetCameraPosition' },
    0xD2: { 'Size': 0x03, 'Mnemonic': '' },
    0xD3: { 'Size': 0x03, 'Mnemonic': '' },
    0xD4: { 'Size': 0x04, 'Mnemonic': 'CameraHeight' },
    0xD5: { 'Size': 0x09, 'Mnemonic': '' },
    0xD6: { 'Size': 0x00, 'Mnemonic': '' },
    0xD7: { 'Size': 0x0a, 'Mnemonic': '' },
    0xD8: { 'Size': 0x0b, 'Mnemonic': '' },
    0xD9: { 'Size': 0x02, 'Mnemonic': '' },
    0xDA: { 'Size': 0x0a, 'Mnemonic': '' },
    0xDB: { 'Size': 0x03, 'Mnemonic': '' },
    0xDC: { 'Size': 0x00, 'Mnemonic': '' },
    0xDD: { 'Size': 0x00, 'Mnemonic': '' },
    0xDE: { 'Size': 0x02, 'Mnemonic': '' },
    0xDF: { 'Size': 0x02, 'Mnemonic': '' },
    0xE0: { 'Size': 0x02, 'Mnemonic': 'CameraWait(?)' },
    0xE1: { 'Size': 0x02, 'Mnemonic': '' },
    0xE2: { 'Size': 0x06, 'Mnemonic': '' },
    0xE3: { 'Size': 0x06, 'Mnemonic': '' },
    0xE4: { 'Size': 0x05, 'Mnemonic': '' },
    0xE5: { 'Size': 0x06, 'Mnemonic': '' },
    0xE6: { 'Size': 0x05, 'Mnemonic': '' },
    0xE7: { 'Size': 0x02, 'Mnemonic': '' },
    0xE8: { 'Size': 0x03, 'Mnemonic': '' },
    0xE9: { 'Size': 0x03, 'Mnemonic': '' },
    0xEA: { 'Size': 0x04, 'Mnemonic': 'CameraZoom' },
    0xEB: { 'Size': 0x04, 'Mnemonic': '' },
    0xEC: { 'Size': 0x04, 'Mnemonic': 'CameraZoomScalar' },
    0xED: { 'Size': 0x05, 'Mnemonic': '' },
    0xEE: { 'Size': 0x00, 'Mnemonic': '' },
    0xEF: { 'Size': 0x06, 'Mnemonic': '' },
    0xF0: { 'Size': 0x02, 'Mnemonic': 'Wait(numFrames)' },
    0xF1: { 'Size': 0x02, 'Mnemonic': '' },
    0xF2: { 'Size': 0x05, 'Mnemonic': '' },
    0xF3: { 'Size': 0x02, 'Mnemonic': '' },
    0xF4: { 'Size': 0x02, 'Mnemonic': '' },
    0xF5: { 'Size': 0x04, 'Mnemonic': '' },
    0xF6: { 'Size': 0x02, 'Mnemonic': '' },
    0xF7: { 'Size': 0x03, 'Mnemonic': '' },
    0xF8: { 'Size': 0x01, 'Mnemonic': '' },
    0xF9: { 'Size': 0x01, 'Mnemonic': '' },
    0xFA: { 'Size': 0x01, 'Mnemonic': '' },
    0xFB: { 'Size': 0x01, 'Mnemonic': '' },
    0xFC: { 'Size': 0x01, 'Mnemonic': '' },
    0xFD: { 'Size': 0x01, 'Mnemonic': '' },
    0xFE: { 'Size': 0x01, 'Mnemonic': '' },
    0xFF: { 'Size': 0x01, 'Mnemonic': 'return()' },
}

class ScriptOpcode:
    def __init__(self, op = 0, args = [], mnemonic = '', note = '') -> None:
        self.Op = op
        self.Args = args
        self.Mnemonic = mnemonic
        self.Note = note
    
    @property
    def Size(self):
        return _Opcode_[self.Op]['Size']

    def addMnemonic(self):
        arg = self.Args
        if self.Op == 0x10:
            hl = (arg[3] << 8) + arg[2]
            #if (arg[0]>>4) != (arg[0]&0xF):
            #    logging.critical('idDlg diff !!')  # evt 88 has diff id, why? , ({[(hex(hl)), (hl&0xFFF), (hl>>12)]})
            self.Mnemonic = f"DialogShow(idDlg={(arg[0]&0xF)}, Style={arg[1]>>4, arg[1]&0xF}, x={[arg[2], arg[3]]}, y={arg[4]}, w={arg[5]}, h={arg[6]}, {arg[7]}, {arg[8]}, {arg[9]})"
        if self.Op == 0x11:
            self.Mnemonic = f"DialogText(idDlg={arg[0]}, idText={arg[1]}, {arg[2]})"
        if self.Op == 0x12:
            self.Mnemonic = f"DialogHide(idDlg={arg[0]})"

    def pos(self, x=-1, y=-1, w=-1, h=-1):
        if self.Op == 0x10:
            if 0 <= x:
                logging.critical(f'What can I do for x?')
            if 0 <= y:
                self.Args[4] = y
            if 0 <= w:
                self.Args[5] = w
            if 0 <= h:
                self.Args[6] = h
        else:
            logging.critical(f'It is not DialogShow!!')
        
        self.addMnemonic()
        
class ScriptOpcodes:
    def __init__(self, buffer: Union[bytes, None] = None) -> None:
        self.opcodes: List[ScriptOpcode] = []
        
        if buffer is not None:
            self.unpackData(buffer)

    def __len__(self):
        if not self.opcodes:
            return 0
        
        len_opcodes = 0
        for code in self.opcodes:
            len_opcodes += code.Size
        return len_opcodes
   
    def __repr__(self) -> str:
        reprTexts = ''
        for idx, code in enumerate(self.opcodes):
            arg = code.Args
            if code.Op == 0x10:
                reprTexts += f"{idx}: {code.Mnemonic}\n"
            if code.Op == 0x11:
                reprTexts += f"{idx}: {code.Mnemonic}"
                if code.Note:
                    first = dialog.checkFirst(code.Note)
                    if len(first) != 1:
                        logging.critical(f'why? {first}')
                    rows, cols = dialog.checkSize(code.Note)
                    reprTexts += f'; w={cols}, h={rows} {first} "{code.Note}"'
                reprTexts += '\n'
            if code.Op == 0x12:
                reprTexts += f"{idx}: {code.Mnemonic}\n"
        return reprTexts
    
    def unpackData(self, buffer: bytes):
        byte_stream = io.BytesIO(buffer)
        len_buffer = len(buffer)
        pos = 0
        
        self.opcodes.clear()
        while pos < len_buffer:
            op = int.from_bytes(byte_stream.read(1), 'little')
            pos += 1
            code = ScriptOpcode(op)
            #code = { 'Op': op, 'Size': self.Opcode[op]['Size'], 'Args': [] }
            argSize = code.Size - 1
            if argSize:
                code.Args = list(byte_stream.read(argSize))
                pos += argSize
            code.addMnemonic()

            self.opcodes.append(code)

    def packData(self):
        byte_stream = io.BytesIO()
        
        for code in self.opcodes:
            byte_stream.write(bytes1(code.Op))
            argSize = code.Size - 1
            if argSize:
                byte_stream.write(bytes(code.Args))
        
        data = byte_stream.getvalue()
        len_data = len(data)
        len_data_pad = ((len_data+3)//4)*4
        padding = len_data_pad - len_data
        if padding:
            pass
        return data + b'\x00'*padding
