#!/bin/zsh

for f in /app/dataset/**/*.pv
do
  python3 pv_to_mod12.py $f > $f.mod12
done
