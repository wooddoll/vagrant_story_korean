# Vagrant Story 한글화 
- 일어판을 한글화

## 문자열 추출 파일
- SLPS_023.77         ; skill name x256
- MENU/ITEMNAME.BIN   ; item name  x512
- MENU/MCMAN.BIN      ; ui 
- MENU/ITEMHELP.BIN   ; item text
- MAP/*.MPD           ; dialog!!, treasure weapon name
- MAP/*.ZND           ; NPC name, weapone name
- SMALL/*.ARM         ; room names

## 진행상황
- 2024-10-1: font table 수정
   - font image를 OCR로 읽었는데, 다시 확인해보니 잘못읽어서 중복된 한자로 된게 여러개 있다. 해상도가 너무 낮아서 대충 비슷하게 생긴 한자로 수정함. 어째 번역이 좀 이상하더라...
- 2024-9-30:
   - 아이템이름 추출; MENU/ITEMNAME.BIN
      - 24바이트씩 이름이 512개가 연속으로 있음 
   - 아이템설명 추출; MENU/ITEMHELP.BIN
      - 2바이트 주소가 679개 연이어 있음. 실제 주소값은 읽은 값의 2배임
   - 참고 <https://gamefaqs.gamespot.com/ps/914326-vagrant-story/faqs/8485>
- 2024-9-29: 기술이름 추출; SLPS_023.77
   - 참고 <https://datacrystal.tcrf.net/wiki/Vagrant_Story/Main_exe>, <https://datacrystal.tcrf.net/wiki/Vagrant_Story/skills>
- 2024-9-27: 일어판 LBA table 확인
   - 참고 <https://github.com/cebix/psximager>
   - MPD파일 크기가 LBA 경계를 넘으면 psximager의 .cat을 이용해서 이미지를 다시 빌드할 것
   - MPD의 LBA 위치는 .ZND에 있음, debug MPD를 몇개 비우고 LBA를 확보할 것
- 2024-9-25: 방이름 추출; SMALL/*.ARM
   - 참고 <https://datacrystal.tcrf.net/wiki/Vagrant_Story/ARM_files>
- 2024-9-24: 지역별 NPC이름, 무기이름 추출; MAP/*.ZND
   - 참고 <https://datacrystal.tcrf.net/wiki/Vagrant_Story/ZND_files>
- 2024-9-23: 대사 추출; MAP/*.MPD
   - 참고 <https://datacrystal.tcrf.net/wiki/Vagrant_Story/MPD_files>
   - 보물상자에 있는 무기의 이름도 있음 - 몇개만 확인해봤는데, 전부 빈칸이다. 나중에 다시 확인
   - 대부분의 파일 크기가 LBA경계 보다 작아서 대사길이가 좀 늘어도 여유가 있음
- 2024-9-19: 일본어 폰트 추출; MENU/FONT14.BIN
   - 참고 <https://github.com/HilltopWorks/VagrantStory-Font/tree/main>
   - 영문폰트는 4b texture, 일문폰트는 2b임
## 
  
## 참고
- 나중에 확인 <https://archaic-ruins.lngn.net/utils/translte.htm>
