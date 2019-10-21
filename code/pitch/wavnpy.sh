#!/bin/zsh

for f in /app/dataset/**/*.wav
do
  python3 wav_to_int.py $f
done
