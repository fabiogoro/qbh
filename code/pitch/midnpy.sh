#!/bin/zsh

for f in /app/dataset/**/*.mid
do
  python3 wav_to_int.py $f --mid
done
