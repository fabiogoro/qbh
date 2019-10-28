FROM i386/ubuntu:latest

WORKDIR /app

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
locales \
wget \
git \
vim \
zsh \
python \
python-pip \
python-tk \
python3 \
python3-pip \
python3-tk \
libsndfile1 \
midicsv \
libfreetype6-dev \
pkg-config \
python-cffi \ 
libffi-dev \
&& rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

COPY scripts /app/scripts
COPY extra /app/extra
RUN /bin/bash scripts/install_asymut.sh

RUN pip install numpy
RUN pip install --no-cache-dir matplotlib midiutil vamp librosa
RUN pip3 install --no-cache-dir librosa matplotlib numpy
RUN pip3 install midiutil vamp jupyter

RUN /bin/bash scripts/install_qbhlib.sh
COPY scripts/smbgt /bin
RUN chmod +x /bin/smbgt
COPY scripts/dtw /bin
RUN chmod +x /bin/dtw
COPY scripts/transcribe /bin
RUN chmod +x /bin/transcribe
RUN /bin/bash scripts/install_qbhlib.sh
COPY scripts/prepare_pv /bin
RUN chmod +x /bin/prepare_pv
COPY scripts/match /bin
RUN chmod +x /bin/match
COPY scripts/rank_and_evaluate /bin
RUN chmod +x /bin/rank_and_evaluate
