import os
import util
import segment
import ml
from PIL import Image
import numpy as np


def preprocess(im):
    util.convert2white(im, 470)
    util.convert2black(im)
    util.denoise(im)
    return im


def get_result(fn):
    im = Image.open(fn).convert("RGB")
    im = preprocess(im)
    regs = segment.segment(im)
    clr = ml.get_clr()
    data = []
    for _, reg in enumerate(regs):
        imgData = util.getArrayData(reg)
        data.append(imgData)
    res = clr.predict(data).tostring()
    return res


def scores(samples, outDir=None):
    data = []
    label = []
    for idx, (fn, lb) in enumerate(samples):
        print "start processing:", idx
        im = Image.open(fn).convert("RGB")
        im = preprocess(im)
        regs = segment.segment(im)
        f = fn.split(os.sep)[-1]
        for ix, reg in enumerate(regs):
            # reg.save("./imgs/liepin/out/"+f[:-4]+"_"+str(ix)+f[5+ix]+".bmp")
            imgData = util.getArrayData(reg)
            data.append(imgData)
            label.append(lb[ix])
            # print lb[ix],f[5+ix]
    clr = ml.get_clr()
    clr.train(data, label)


def test_get_result(src_dir):
    correct_cnt = 0
    for idx, (fn, lb) in enumerate(samples):
        res = get_result(fn)
        if lb == res:
            correct_cnt += 1
        print "processing[%d]:%s == %s" % (idx, lb, res)
    print correct_cnt, len(samples)


if __name__ == "__main__":
    parentDir = "../imgs/liepin"
    rootDir = parentDir + os.sep + "raw1"
    rootDir1 = parentDir + os.sep + "raw1"
    if not os.path.exists(rootDir1):
        os.mkdir(rootDir1)

    samples = []
    for idx, f in enumerate(os.listdir(rootDir)):
        fn = rootDir + os.sep + f
        # if f[-4:] == ".jpg":
        #     Image.open(fn).save(rootDir1+os.sep+f[:-4]+".gif")
        lb = f[5:9]
        samples.append((fn, lb))
    test_get_result(samples)
    # scores(samples)
