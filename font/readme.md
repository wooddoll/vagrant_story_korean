### font 수정

/Vagrant Story (J)/BATTLE/SYSTEM.DAT
- 한 픽셀당 2bit인 가로 256크기의 이미지 파일, 
- 폰트 크기는 가로12x세로11
- font1; 0x1AA70부터 0x6E00
- font2; 0x2AA70부터 0x6E00
- font3; 0x28A70부터 0x3700
- 

/Vagrant Story (J)/MENU/FONT14.BIN
- 한 픽셀당 2bit인 가로 256크기의 이미지 파일, 
- 폰트 크기는 14x14
- 전체 폰트는 18x126, 2268개
- 한 바이트로 2b/2b/2b/2b, 4픽셀을 표현하는데, 짝수 번째는 왼쪽(<128px), 홀수 번째는 오른쪽(128px<)에 배치되고 한 라인은 64byte이다.
- Vagrant Story의 폰트는 흰색 배경에 검은색 폰트를 쓰기 때문에 폰트의 값 0은 투명, 1이 가장 밝은 색, 2이 중간 밝기, 3이 가장 어두운 밝기다.

# unpack / pack
- cvtFontBin.py를 사용해서 FONT14.BIN을 이미지로 변환할 수 있다.
- 폰트에 포함된 한자는 모두 1853자
![](https://github.com/wooddoll/vagrant_story_korean/blob/master/font/font14_2b_256.png)
