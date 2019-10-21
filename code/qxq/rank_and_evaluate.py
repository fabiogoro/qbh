import csv, argparse, glob, sys
import scipy.ndimage
import scipy.stats
import numpy as np
import librosa
import librosa.display
from matplotlib import pyplot as plt
csv.field_size_limit(sys.maxsize)

query = []
top = []
classes_rank = []
inter = []
mult = []
mult2 = []
with open('scores.csv', newline='') as o:
    reader = csv.reader(o, delimiter=' ')
    db_files = []
    query_files = []
    file_list = next(reader)
    part = {}
    top = []
    errors = 0
    for filename in file_list[1:-1]:
        db_files.append(filename)
    rrs = {}
    for row in reader:
        correct_values = []
        all_values = []
        incorrect_values = []
        itsy = []
        classes = [[] for i in range(50)]
        query_files.append(row[0])
        for i, db_file in zip(part.get(row[0], []) + row[1:-1], db_files):
            if not db_file in part:
                part[db_file] = []
            part[db_file].append(i)
            if float(i) > 0:
                classes[(int(db_file.split('/000')[1][:2]))].append(float(i))
            all_values.append(float(i))
        all_values = np.array(all_values)
        db_files = np.array(db_files)
        index_sorted = np.argsort(all_values)
        means = [np.mean(sorted(i)[:]) for i in classes]
        means = np.array(means)
        ranked_classes = np.argsort(means)

        mix_weights = []
        for i, val in enumerate(db_files):
            val = int(val[-11:-9])
            mix_weights.append(all_values[i]*means[val]*means[val])

        mix_weights = np.array(mix_weights)
        index = np.argsort(mix_weights)

        mix_weights = []
        for i, val in enumerate(db_files):
            val = int(val[-11:-9])
            mix_weights.append(all_values[i]*means[val])

        mix_weights = np.array(mix_weights)
        index2 = np.argsort(mix_weights)

        mixed_list = []
        for i in db_files[index_sorted][1:]:
            val = int(i[-11:-9])
            if val in ranked_classes[:2] and len(mixed_list)<5:
                mixed_list.append(val)

        query = int(row[0][-11:-9])
        rr = 0
        for i in range(5):
            if query == int(db_files[index_sorted][i+1][-11:-9]):
                rr = 1/(i+1)
                break
        top.append(rr)

        rr = 0
        for i in range(5):
            if query == ranked_classes[i]:
                rr = 1/(i+1)
                break
        classes_rank.append(rr)

        rr = 0
        for i in range(len(mixed_list)):
            if query == mixed_list[i]:
                rr = 1/(i+1)
                break
        inter.append(rr)

        rr = 0
        for i in range(5):
            if query == int(db_files[index][i+1][-11:-9]):
                rr = 1/(i+1)
                break
        mult.append(rr)

        rr = 0
        for i in range(5):
            if query == int(db_files[index2][i+1][-11:-9]):
                rr = 1/(i+1)
                break
        mult2.append(rr)

    print("Method", "Top", "Class", "Inter", "Mult", "Mult2", sep="\t")
    print("MRR", "%.2f" % np.mean(top), "%.2f" % np.mean(classes_rank), "%.2f" % np.mean(inter), "%.2f" % np.mean(mult), "%.2f" % np.mean(mult2), sep='\t') 
    print("Recall", "%.2f" % (100*(len(top)-np.count_nonzero(top))/len(top)), 
          "%.2f" % (100*(len(classes_rank)-np.count_nonzero(classes_rank))/len(classes_rank)), 
          "%.2f" % (100*(len(inter)-np.count_nonzero(inter))/len(inter)), 
          "%.2f" % (100*(len(mult)-np.count_nonzero(mult))/len(mult)), 
          "%.2f" % (100*(len(mult2)-np.count_nonzero(mult2))/len(mult2)), sep='\t')    
