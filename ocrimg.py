import os
import time
import sys
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '.\\Tesseract\\tesseract.exe'

def recogn(im, cn = '--psm 8'):
    tn = pytesseract.image_to_string(im, config=cn)
    symbs = ''
    if len(tn) > 0:
        for s in tn:
            if s.isalpha() or s.isdigit():
                symbs = symbs + s.lower()
    return symbs

if len (sys.argv) > 1 :
    in_file = sys.argv[1]
else:
    if os.path.exists('turbobit_net_v50_GDL_03.png'):
        in_file = 'turbobit_net_v50_GDL_03.png'
    else:
        sys.exit()

f = 64
rez = ''
img = Image.open(in_file)
(width, height) = img.size
parts = [[0,40], [35,72], [70,103], [102, width-2]]
pix = img.load()
for x0, x1 in parts:
    img0 = Image.new("RGB", (x1-x0+1, height), "#ffffff")
    pixels0 = img0.load()
    for i in range(height):
        for j in range(x0, x1+1):
            color = pix[j,i]
            color0 = (f*(color[0]//f), f*(color[1]//f), f*(color[2]//f))# cut little 6 bit of colors
            pixels0[j-x0, i] = color0
    symbs = {}
    for angle in range(-30, 31, 5):# 13 tryes for every symbol 
        tn = recogn(img0.rotate(angle), '--tessdata-dir ./Tesseract/tessdata --psm 10 turbobit') 
        if len(tn) > 0:
            for k in tn:
                if symbs.get(k) == None:
                    symbs.update({k:1})
                else:
                    symbs.update({k:symbs.get(k)+1})
    if len(symbs):
        rez += max(symbs.items(), key = lambda x: x[1])[0]
fout = open('rezocr.txt', 'w')
fout.write(rez)
fout.close()
