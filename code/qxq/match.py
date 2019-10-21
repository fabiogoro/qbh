import csv, argparse, glob, sys, os
import librosa as l
import librosa.sequence
import scipy.ndimage
import scipy.stats
import numpy as np
import thread
import time
csv.field_size_limit(sys.maxsize)

out = []
db = []
thread_count = [0]
lock = thread.allocate_lock()
X = np.zeros((40,40))
for i in range(40):
    for j in range(40):
        X[i,j] = 1/((max(i,j)+1)/40.0)

def process_multithread(thread, q, db):
    lock.acquire()
    out[thread].append(q[1])
    lock.release()
    i=0
    res = []
    for d in db:
        i+=1
        score_vector = []
        for s in d:
            D = l.sequence.dtw(q[0], s, subseq=False, backtrack=False, metric=lambda u, v: (min(np.mod(u-v,12), np.mod(v-u,12))/6)**2)
            E = D*X
            score = np.min(E[-10:,-10:])
            score_vector.append(score)
        out[thread].append(min(score_vector))
        res.append(min(score_vector))
    lock.acquire()
    thread_count[0] -= 1
    lock.release()

def run_multithread(query, db):
    while len(query) > 0:
        if thread_count[0] == 0:
            for i in out:
                print ''
                for j in i:
                    print j,
            out = []
            for i in range(12):
                if len(query) > 0:
                    try:
                        q = query.pop(0)
                        out.append([])
                        thread_count[0] += 1
                        thread.start_new_thread(process_multithread,(i, q, list(db)))
                        db.pop(0)
                    except:
                        pass


    while thread_count[0] > 0:
        pass

    for i in out:
        print ''
        for j in i:
            print j,

def process(q, db):
    res = []
    print q[1],
    for d in db:
        score_vector = []
        pos_vector = []
        for s in d:
            D = l.sequence.dtw(q[0], s, subseq=False, backtrack=False, metric=lambda u, v: (min(np.mod(u-v,12), np.mod(v-u,12))/6)**2)
            E = D*X
            score = np.min(E[-10:,-10:])
            score_vector.append(score)
        print min(score_vector),
    print ''

def run(query, db):
    while len(query) > 0:
        q = query.pop(0)
        process(q, list(db))
        db.pop(0)
    


def load_dataset():
    query = []
    os.system('touch temp_scores.csv')
    with open('temp_scores.csv') as o:
        reader = csv.reader(o, delimiter=' ')
        files = []
        length = 0
        for filename in reader:
            length += 1
        i = 0
        for filename in glob.iglob('/app/dataset/pv/**/**/*.mod12'):
            i += 1
            if i >= length:
                files.append(filename)
        if length <= 1:
            print '.',
        for filename in files:
            with open(filename) as f:
                s = []
                for row in csv.reader(f):
                    s.append(float(row[0]))
                if len(s)>10:
                    if length <= 1:
                        print filename,
                    s = np.array(s)
                    factor = 40.0/len(s)
                    s = scipy.ndimage.zoom(s, factor, order=0)

                    a = 0
                    for ii in s:
                        a += ii-int(ii)
                    media = a/len(s) # Media dos residuos
                    s = np.mod(s-media,12) # Retira residuos para tentar aproximar queries com tons 'muito' proximos
                    
                    query.append([s, filename])
                    d = []
                    for i in range(12):
                        d.append(np.mod(s+i,12))
                    db.append(d)
        if length <= 1:
            print ''
        return (query, db)

if __name__ == '__main__':
    query, db = load_dataset()
    threads = 1
    if threads>1:
        run_multithread(query, db)
    else:
        run(query, db)
