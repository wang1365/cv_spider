from PIL import Image
import numpy as np

white = (255, 255, 255)
black = (0, 0, 0)


def convert2white(im, white_threshold=470):
    w = im.size[1];
    h = im.size[0]
    pixdata = im.load()
    for i in xrange(h):
        for j in xrange(w):
            if RGBSum(pixdata, i, j) > white_threshold:
                pixdata[i, j] = white


def convert2black(im):
    w = im.size[1];
    h = im.size[0]
    pixdata = im.load()
    for i in xrange(h):
        for j in xrange(w):
            if pixdata[i, j] != white:
                pixdata[i, j] = black


def RGBSum(pix, x, y):
    return pix[x, y][0] + pix[x, y][1] + pix[x, y][2]


def remove_down2up(im, topmost=5):
    w = im.size[1]
    h = im.size[0]
    pixdata = im.load()
    for j in xrange(0, topmost):
        for i in xrange(0, h):
            pixdata[i, w - 1 - j] = white


def denoise(im, cnt_threshold=3):
    w = im.size[1];
    h = im.size[0]
    ret_img = Image.new("RGB", im.size)
    pixdata = im.load()
    tagdata = ret_img.load()
    for i in xrange(h):
        for j in xrange(w):
            up = i - 1 if i > 0 else i
            do = i + 1 if i < h - 1 else i
            le = j - 1 if j > 0 else j
            ri = j + 1 if j < w - 1 else j
            cnt = 0
            cnt += 1 if pixdata[up, j] != white else 0
            cnt += 1 if pixdata[do, j] != white else 0
            cnt += 1 if pixdata[i, le] != white else 0
            cnt += 1 if pixdata[i, ri] != white else 0
            cnt += 1 if pixdata[up, le] != white else 0
            cnt += 1 if pixdata[up, ri] != white else 0
            cnt += 1 if pixdata[do, le] != white else 0
            cnt += 1 if pixdata[do, ri] != white else 0

            if cnt < cnt_threshold:
                pixdata[i, j] = white


def get_box(im):
    h = im.size[1];
    w = im.size[0]
    pixdata = im.load()
    l_ = w - 1;
    r_ = 0;
    u_ = h - 1;
    d_ = 0
    for j in xrange(0, w):
        for i in xrange(0, h):
            if pixdata[j, i] == white:
                continue
            l_ = l_ if l_ < j else j
            r_ = r_ if r_ > j else j
            u_ = u_ if u_ < i else i
            d_ = d_ if d_ > i else i
    return l_, r_, u_, d_


def get_init_point(im, x_init):
    x = 0
    y = 0
    h = im.size[1]
    w = im.size[0]
    pixdata = im.load()
    flag_black = False
    for i in xrange(0, h):
        pixdata[x_init - 1, i] = (255, 0, 0)
        if not flag_black:
            if pixdata[x_init, i] != white:
                flag_black = True
            continue

        if pixdata[x_init, i] == white:
            cnt = 0
            cnt += 1 if pixdata[x_init, i + 1] == white else 0
            cnt += 1 if pixdata[x_init - 1, i] == white else 0
            cnt += 1 if pixdata[x_init + 1, i] == white else 0
            cnt += 1 if pixdata[x_init + 1, i + 1] == white else 0
            cnt += 1 if pixdata[x_init - 1, i + 1] == white else 0
            if cnt >= 2:
                y = i
                x = x_init
                break
    return x, y


def fix_shape(reg):
    h = reg.size[1]
    w = reg.size[0]
    regdata = reg.load()
    s_idx = 0
    f_idx = 0
    for j in xrange(0, w):
        cnt = 0
        for i in xrange(0, h):
            if regdata[j, i] != 1:
                cnt += 1
        if s_idx == 0:
            if cnt != 0:
                s_idx = j
            continue
        if cnt == 0:
            f_idx = j
            break
    f_idx = w - 1 if f_idx == 0 else f_idx
    ret_img = reg.crop((s_idx, 0, f_idx, h))
    return ret_img


def getArrayData(im):
    h = im.size[1]
    w = im.size[0]
    d_arr = np.zeros(w * h)
    pixdata = im.load()
    for i in xrange(h):
        for j in xrange(w):
            e = pixdata[j, i]
            d_arr[i * w + j] = e
    return d_arr
