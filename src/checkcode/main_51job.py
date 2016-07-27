import os
import util
import segment
from PIL import Image


def preprocess(im):
    util.convert2white(im, 560)
    util.convert2black(im)
    util.remove_down2up(im)
    util.denoise(im, cnt_threshold=3)
    return im


def get_result(fn):
    res = ""
    im = Image.open(fn).convert("RGB")
    im = preprocess(im)
    cmd = "tesseract " + fn + " out num_aA+"
    try:
        os.system(cmd)
        with open("out.txt", "r") as f:
            res = f.read()
            res = "".join(res.split())[:4]
    except:
        pass
    return res


def scores(samples):
    correct_cnt = 0
    total_cnt = len(samples)
    for idx, (fn, lb) in enumerate(samples):
        print "start processing:", idx
        im = Image.open(fn).convert("RGB")
        im = preprocess(im)
        f = fn.split(os.sep)[-1]
        fn_out = outDir + os.sep + f[:-4] + ".bmp"
        im.save(fn_out)
        res = get_result(fn_out)
        print res
        if lb == res.upper():
            correct_cnt += 1
    print "correct ratio:%d/%d=%.2f%%" % (correct_cnt, total_cnt, 100 * float(correct_cnt) / total_cnt)


if __name__ == "__main__":
    parentDir = "../imgs/51job"
    rootDir = parentDir + os.sep + "raw"
    outDir = parentDir + os.sep + "out"
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    samples = []
    for idx, f in enumerate(os.listdir(rootDir)):
        fn = rootDir + os.sep + f
        lb = f[5:9]
        samples.append((fn, lb))
    scores(samples)
