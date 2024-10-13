from PIL import Image, ImageDraw, ImageFont

'''
texture 위치
배틀모드 64,0 (47x11)

y52
위험 152,52 (24x11)
공격 176,52 (31x11)
파리 208,52 (24x11)
침묵 232,52 (20x11)

y64
이동불가 (36)
업 (25)
다운 (26)
슬로우 (26)
퀵 (22)30?
사일런트 (41)

y76
마히 
독 
저주
리제네
마법무효
아이템

y88
어태치
레지스트
디스펠
에어
파이어
어스
워터
워록

y100
아르지
소서리
인챈트
아이템
브레이크
아트

체인A
디펜스A
'''


def test1():
    img_ui = Image.open('work/texture/system_dat_unpack_1.png')
    width, height = img_ui.size
    
    img12 = Image.new('RGBA', (width, height), (0, 0, 0, 0))
