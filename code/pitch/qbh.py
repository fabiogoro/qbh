import argparse
import qbhlib as ql
import glob
from multiprocessing import Pool
import time
from math import ceil

import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.signal import convolve
import random as r
from librosa.sequence import dtw

query_files = glob.glob("/app/dataset/wav/**/**/*.int.npy")
db_files = "/app/dataset/mid/*.mid.int.npy"
outfile = "log"
K = 10
mode = ''
queries = []
DB = []

def updatequeue(S, best, K, track):
    for i in range(K):
        if S[i]['score'] < best:
            S.insert(i,{'score': best, 'track': track})
            S.pop()
            return


def search_query(query):
    Q = query[0]
    best = 0
    if len(Q)>0:
        S = []
        for pos in range(K):
            S.append({'score':-10,'track': [[],'0']})
        for song in DB:
            best = 0
            X = song[0]
            if mode == 'smbgt':
                best = ql.smbgt(Q, X, 0, 0, 99.0, 0.3, 0.2, 0.0, 0, 1)
            if mode == 'dtw':
                D, wp = dtw(Q, X, subseq=False)

                W = np.zeros((len(Q),len(X)))
                for i in range(len(Q)):
                    for j in range(len(X)):
                        W[i,j] = 1/((max(i,j)+1)/max(len(Q), len(X)))
                E = D*W
                best = np.min(E[round(len(Q)/2):,:])
            updatequeue(S, best, K, song[1])
        res = list(filter(lambda e: e['track'] == query[1], S))
        if len(res)<1:
            return 0
        else:
            return 1.0/(S.index(res[0])+1.0)
    return 0

def qbh():
    print('\nLoading queries...')
    for i in range(len(query_files)):
        queries.append([np.load(query_files[i]), query_files[i][-17:-12]])

    print('Loading db...')
    for file in glob.glob(db_files):
        DB.append([np.load(file), file[-17:-12]])

    f = open(outfile, 'a')
    f.write(' '.join([db_files, str(K), '\n']))

    with Pool(processes=10) as pool:
        res = pool.map(search_query, queries)
        mrr = sum(res)/len(queries)
        recall = sum(map(ceil,res))/len(queries)
    a = '\t'.join(('Recall: '+str(recall),'MRR: '+str(mrr),'\n'))
    print(a)
    f.write(a)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Match a given query dataset to a midi dataset using smbgt or dtw. The query dataset should be in "queries" folder and should already be transcribed to npy. The midi dataset should also be transcribed to npy and should be located in "db" directory.')
    parser.add_argument("mode", help="Matching strategy. Might be 'smbgt' or 'dtw'", choices=['smbgt', 'dtw'])
    args = parser.parse_args()
    mode = args.mode

    qbh()
