import os
import time
import sys
import pyperclip
import pytesseract
import configparser
from PIL import Image

def recogn(im, cn = '--psm 8'):
    tn = pytesseract.image_to_string(im, config=cn)
    symbs = ''
    if len(tn) > 0:
        for s in tn:
            if s.isalpha() or s.isdigit():
                symbs = symbs + s.lower()
    return symbs

if __name__ == '__main__':
    if len (sys.argv) > 1 :
        in_file = sys.argv[1]
    else:
        if os.path.exists('turbobit_net_v50_GDL_03.png'):
            in_file = 'turbobit_net_v50_GDL_03.png'
        else:
            sys.exit()

    path = "ocrimg.ini"
    if os.path.exists(path):
        config = configparser.ConfigParser()
        config.read(path)
        tdir = config.get("Tesseract", "dir")
        opt = config.get("Tesseract", "opt")
        mask = int(config.get("Image", "mask"), 2)
        save_img = int(config.get("Image", "save_img"))
        save_parts = int(config.get("Image", "save_parts"))
        if save_img + save_parts > 0:
            save_dir = config.get("Image", "save_dir")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            basename = str(int(time.time()))
        start = int(config.get("Angle", "start"))
        finish = int(config.get("Angle", "finish"))
        step = int(config.get("Angle", "step"))
        mode = config.get("Output", "mode")
        if mode == 'file':
            out_name = config.get("Output", "filename")
        parts = []
        for option in config.options("Parts"):
            parts.append([int(option), int(config.get("Parts", option))])
    else:
        tdir = '.\\Tesseract\\'
        opt = '--psm 10 turbobit'
        mask = 192
        save_img, save_parts = 0, 0
        start, finish, step = -30, 31, 5
        mode = 'file'
        out_name = 'rezocr.txt'
        parts = [[0,40], [35,72], [70,103], [102, 148]]

    tess_cmd = tdir + 'tesseract.exe'
    tessdata = tdir.replace('\\', '/') + 'tessdata'
    pytesseract.pytesseract.tesseract_cmd = tess_cmd

    rez = ''
    img = Image.open(in_file)
    (width, height) = img.size
    pix = img.load()
    for x0, x1 in parts:
        img0 = Image.new("RGB", (x1-x0+1, height), "#ffffff")
        pixels0 = img0.load()
        for i in range(height):
            for j in range(x0, x1+1):
                color = pix[j,i]
                color0 = (mask&color[0], mask&color[1], mask&color[2])
                pixels0[j-x0, i] = color0
        symbs = {}
        for angle in range(start, finish, step):
            tn = recogn(img0.rotate(angle), '--tessdata-dir ' + tessdata + ' ' + opt) 
            if len(tn) > 0:
                for k in tn:
                    if symbs.get(k) == None:
                        symbs.update({k:1})
                    else:
                        symbs.update({k:symbs.get(k)+1})
        if len(symbs):
            symb = max(symbs.items(), key = lambda x: x[1])[0]
            rez += symb
        if save_parts > 0:
            img0.save(save_dir + basename + '_' + symb + '.bmp')
    if mode == 'file':
        fout = open(out_name, 'w')
        fout.write(rez)
        fout.close()
    elif mode == 'clipboard':
        pyperclip.copy(rez)
    elif mode == 'print':
        print(rez)
    elif mode == 'stdout':
        sys.stdout.write(rez)
    if save_img > 0:
#        sys.stdout = open(os.devnull, 'w')
        os.system('copy ' + str(in_file) + ' ' + save_dir + basename + '_' + rez + '.png > nul')
