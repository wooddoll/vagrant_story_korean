# Vagrant Story 한글화 
- 일어판을 한글화

## 진행상황
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
   - 대부분의 파일 크기가 LBA경계 보다 작아서 대사길이가 좀 늘어도 여유가 있음
- 2024-9-19: 일본어 폰트 추출; MENU/FONT14.BIN
   - 참고 <https://github.com/HilltopWorks/VagrantStory-Font/tree/main>
   - 영문폰트는 4b texture, 일문폰트는 2b임
## 
  
## 참고
- <https://datacrystal.tcrf.net/wiki/Vagrant_Story> 
  * <https://datacrystal.tcrf.net/wiki/Vagrant_Story/File_formats>
  * <https://datacrystal.tcrf.net/wiki/Vagrant_Story/Script_Opcodes>
  * <https://datacrystal.tcrf.net/wiki/Vagrant_Story/TBL>
