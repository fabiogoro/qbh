import csv, argparse
import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    path = parser.parse_args().path
    with open(path) as f:
        for row in csv.reader(f):
            v = float(row[0])
            if v:
                print(np.mod(v, 12))
