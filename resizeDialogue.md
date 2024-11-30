대화창이 나오는 파일은 2종류 입니다.
1. MAP/MAP???.MPD
2. EVENT/????.EVT

MPD파일의 구조는 https://datacrystal.tcrf.net/wiki/Vagrant_Story/MPD_files 를 참고하면 됩니다.
EVT파일은 MPD파일의 ScriptSection 부분만 잘라낸 형식으로 4KB 크기로 zero padding되어 있습니다.

대화문은 DialogText 부분이고, 말풍선은 Opcodes(https://datacrystal.tcrf.net/wiki/Vagrant_Story/Script_Opcodes)에 있습니다.

말풍선 관련 op는 0x10, 0x11, 0x12 입니다.
말풍선 크기는 0x10(DialogShow(idDlg, Style, x,x, y, w, h, ?, ?, ?) 의 w, h 로 지정됩니다.

- 지문이 가로 12칸, 세로 3줄 이라면 말풍선은 보통 w=14, h=5 로 정해져서 바깥쪽은 한 칸씩 비우도록 만들어 집니다.
- 대체로 이런 크기로 정해지기는 하지만, 반드시 그런건 아니고, 딱 맞는 크기를 사용하는 Style도 있습니다. 
-   1) DialogShow 로 말풍선 생성, 2) DialogText 대화문 쓰기, ... 3) DialogHide 말풍선 지우기 이런 순서로 사용되는데, 동시에 말풍선이 2개 생성되는 경우도 종종 있습니다.
- 
       
