대화창이 나오는 파일은 2종류 입니다.
1. MAP/MAP???.MPD
2. EVENT/????.EVT

- MPD파일의 구조는 https://datacrystal.tcrf.net/wiki/Vagrant_Story/MPD_files 를 참고하면 됩니다.
- EVT파일은 MPD파일의 ScriptSection 부분만 잘라낸 형식으로 4KB 크기로 zero padding되어 있습니다.

       + ScriptSection =====================================
       +$00	2	lenScriptSection
       +$02	2	ptrDialogText
       +$04	2	ptrUnknown1
       +$06	2	ptrUnknown2
       +$08	2	Unknown1 (Always == 0?)
       +$0A	2	Unknown2 (Always == 0?)
       +$0C	2	Unknown3 (Always == 0?)
       +$0E	2	Unknown4 (Always == 0?)
       +$10 ScriptOpcodes
               +$00	?	Opcodes (as per Script Opcodes)
       +(ptrDialogText) DialogText
               +$00	2	numDialogs/ptrDialogText[0]
               for (numDialogs-1)
                       +$00	2	ptrDialogText
               for (numDialogs-1)
                       +$00	$	Dialog Text (as per VS Character Set)
       +(ptrUnknown1) Unknown1
               +$00	?	Unknown data
       +(ptrUnknown2) Unknown2
               +$00	2	Unknown data


대화문은 DialogText 부분이고, 말풍선은 Opcodes( https://datacrystal.tcrf.net/wiki/Vagrant_Story/Script_Opcodes )에 있습니다.
말풍선 관련 op는 0x10, 0x11, 0x12 입니다.
말풍선 크기는 0x10(DialogShow(idDlg, Style, x,x, y, w, h, ?, ?, ?) 의 w, h 로 지정됩니다.

지문이 가로 12칸, 세로 3줄 이라면 말풍선은 보통 w=14, h=5 로 정해져서 바깥쪽은 한 칸씩 비우도록 만들어 집니다.
대체로 이런 크기로 정해지기는 하지만, 반드시 그런건 아니고, 딱 맞는 크기를 사용하는 Style도 있습니다. 

       1) DialogShow 로 말풍선 생성
       2) DialogText 대화문 쓰기, 
              ... 
       3) DialogHide 말풍선 지우기 
이런 순서로 사용되는데, 동시에 말풍선이 2개 생성되는 경우도 종종 있습니다.
그래서 idDlg를 확인해야 합니다. (idDlg는 하위 4b만 사용합니다.)

말풍선이 바깥쪽을 비우고 쓰도록 크게 만들어 지면 지문을 안에 써야 되는데, 지문을 가로로 띄우는 건 그냥 빈칸을 추가하면 되고, 세로로 한줄 띄우는건 줄바꿈을 하나 추가하면 됩니다.
문제는 3줄용으로 만든 말풍선에 2줄 대화문을 넣을 때 반줄 띄우는 건데, 보통 대화문 제일 앞에 0xFB98, 0xFB68 이런 control word가 그 역활을 합니다. 정확한 사용법은 저도 잘 모르고 비슷하게 사용되는 경우를 찾아서 붙여넣기하고 있습니다.

## 참고(git code)
- vagrant_story_korean/work/kor/MAP_MPD_ko.json, vagrant_story_korean/work\kor\EVENT_EVT_ko.json
- vagrant_story_korean/fileStruct/scriptOPcodes.py
- vagrant_story_korean/rebuild.py, adjustSpaceMPD(), update_MPD(), adjustSpaceEVT(), update_EVT()

       
