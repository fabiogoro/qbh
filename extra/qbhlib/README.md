# QBH

Work repository of ongoing research on query-by-humming.

Folder `lib` contains the sequence matching library, having only SMBGT implemented still. It can be installed by running 
```
python3 setup.py build_ext --inplace
```

It'll create a file inplace that allows the use of qbhlib's function in Python.
Meanwhile it has only the function qbhlib.smbgt(), that takes 10 arguments:

* first sequency: a list of numbers.
* second sequency: a list of numbers.
* alpha: integer.
* beta: integer.
* next 4 args are floats.
* 9th arg is boolean for debug.
* 10th arg is optional integer for dimension (default is 2).

File `qbh.py` is a script that loads database in bd folder and show and log recall and MRR values obtained from running SMBGT over the whole database.

A run script, `run.sh`, installs the lib (if not yet installed) and execute the `qbh.py` script. So
```
bash run.sh
```

will install and run everything. Output will be saved in a file called `log`.

Tests can be run in `tests.py`.
