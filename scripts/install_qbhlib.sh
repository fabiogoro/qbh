#!/bin/bash

cd extra/qbhlib/
python3 setup.py build_ext
python3 setup.py install
cd ../..
