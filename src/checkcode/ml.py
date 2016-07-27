from sklearn import svm
import numpy as np
from sklearn.utils import check_random_state

try:
    import cPickle as pk
except:
    import pickle as pk
import time
import os


class CCheckCodeML(object):
    def __init__(self, modelfile=None):

        fn = "liepin_model_win.pkl" if os.name == "nt" else "liepin_model_linux.pkl"
        self.init_model_file = "./checkcode/model/" + fn
        self.current_mode = modelfile if modelfile else self.init_model_file
        self._load_mode()

    def set_mode_file(self, path):
        self.current_mode = path
        self._load_mode()

    def _load_mode(self):
        try:
            with open(self.current_mode, 'rb') as f:
                self.clf_linear = pk.load(f)
                print "%s load modelfile %s OK." % (time.ctime(), self.current_mode)
        except:
            print("%s load model file:%s failed." % (time.ctime(), self.current_mode))
            with open(self.init_model_file, 'rb') as f:
                self.clf_linear = pk.load(f)

    def predict(self, data):
        if not self.clf_linear:
            self._load_mode()
        if not self.clf_linear:
            return ""
        return self.clf_linear.predict(data)

    def train(self, data, label, num=1):
        ratio = 0.0
        for i in xrange(num):
            random_state = check_random_state(i)
            indices = np.arange(len(data))
            random_state.shuffle(indices)
            data = [data[i] for i in indices]
            label = [label[i] for i in indices]
            ratio += self._train(data, label)
        print("final ration:%.2f%%" % (ratio / num))

    def _train(self, data, label, gamma=0.008, C=2):
        sp = int(len(data) * 0.8)
        d_train = np.asarray(data[:sp])
        l_train = label[:sp]
        d_test = np.asarray(data[sp:])
        l_test = label[sp:]
        print "start training"
        self.clf_linear = svm.SVC(kernel='rbf', gamma=gamma, C=C).fit(d_train, l_train)
        print "finish training"

        print "start validation"
        result = self.clf_linear.predict(d_test)
        print "finish prediction"
        length = len(l_test)
        cnt = 0
        single_cnt = 0
        correct = 0
        for i in xrange(0, length):
            if result[i].upper() == l_test[i].upper():
                cnt += 1
                single_cnt += 1
            if (i + 1) % 4 == 0:
                if cnt == 4:
                    correct += 1
                cnt = 0
        ratio = 100 * float(correct) / (length / 4)
        res_str = "single:%.2f%%,%d/%d=%.2f%%" % (100 * float(single_cnt) / length, correct, length / 4, ratio)
        print res_str
        with open(self.init_model_file, 'wb') as f:
            pk.dump(self.clf_linear, f, protocol=1)
        return ratio

    def grid_search(self, data, label):
        for g in xrange(1, 10):
            for c in xrange(1, 10):
                res = self._test(data, label, 0.01 * g, 1 * c)
                print g, c, res


clr = None


def get_clr(model_file=None):
    global clr
    if not clr:
        clr = CCheckCodeML(model_file)
    return clr


if __name__ == "__main__":
    print time.ctime()
