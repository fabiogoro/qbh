#!/bin/zsh

for f in /app/dataset/**/*.mid
do
  if [ ! -f $f.int.npy ]; then
    python3 wav_to_int.py $f --mid
  fi
done
