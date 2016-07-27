import util
from PIL import Image


def get_sub_img(im, x_init, color):
    h = im.size[1]
    w = im.size[0]
    pix_buffer = []
    out_buffer = []
    x, y = util.get_init_point(im, x_init)
    pix_buffer.append((x, y))
    op_img = im.copy()
    pixdata = op_img.load()

    while len(pix_buffer) != 0:
        (x, y) = p = pix_buffer.pop()
        out_buffer.append(p)
        if len(out_buffer) > 500:
            return None
        pixdata[x, y] = util.black
        le = x - 1 if x > 0 else x
        re = x + 1 if x < w - 1 else x
        up = y - 1 if y > 0 else y
        do = y + 1 if y < h - 1 else y
        if pixdata[x, up] == color:
            pix_buffer.append((x, up))
        if pixdata[x, do] == color:
            pix_buffer.append((x, do))
        if pixdata[le, y] == color:
            pix_buffer.append((le, y))
        if pixdata[re, y] == color:
            pix_buffer.append((re, y))

    if len(out_buffer) < 100:
        return None
    reg = Image.new("1", (100, h), 1)
    regdata = reg.load()
    for x, y in out_buffer:
        try:
            regdata[x, y] = 0
        except Exception as e:
            return None
    return reg


def segment(im):
    h = im.size[1]
    w = im.size[0]
    pixdata = im.load()
    w_l, w_r, h_t, h_d = util.get_box(im)
    in_w = int(float(w_r - w_l) / 4)
    regs = []
    for i in range(0, 4):
        box = (w_l + 1 + i * in_w, 5, w_l + 1 + (i + 1) * in_w, h)
        reg = Image.new("1", (25, h - 5), 0)
        regData = reg.load()
        for ri in xrange(box[0] + 2, box[2] - 2):
            for rj in xrange(5, h):
                regData[ri - box[0], rj - 5] = 1 if pixdata[ri, rj] == util.white else 0
        # reg = get_sub_img(im,w_l+in_w/2+i*in_w,white)
        regs.append(reg)
    return regs
