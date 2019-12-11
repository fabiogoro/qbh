## Introduction

This github was created to make reproducible the experiments from the research on query-by-humming that led to the work "Strategies for Matching in Query-by-Humming". Throughout the work, 3 approaches are presented, and there are codes, results and tutorials for each of them in this repository.

The first approach evaluated the recall and MRR from Soundhound for QBH, the results can be seen in [this file](../blob/master/soundhound.xlsx).

The second approach used a condensed representation, abstracting and discarding most of the information from the hummed record, balancing what was necessary to find target results, mostly pitch information or rhythm information from the record. This approach is under the name of `pitch` in the folders `code` and `notebooks`.

The third and last approach followed query against query strategy, which means that a query is compared to a dataset of previously classified queries. The name of the folder for this approach is `qxq`, and can also be seen in `code` and `notebooks`.

The folder `code` contains full code for reproducing the experiments. There are instructions bellow for building and running they using Docker.

The folder `notebooks` contains tutorials for following step-by-step the methodology of the experiment. The tutorials can be read directly from github, but they also can be run inside the docker.

## Installing dependencies

This project requires Docker, pip and docker-compose. One could install it in linux by running the following:

```
apt install docker python-pip
pip install docker-compose
```

## Building

All building needed for the project is defined in the Dockerfile. For preparing it for running, build it using docker-compose.

```
docker-compose build
```

## Running

The project contains scripts for running specific tasks:

* `docker-compose run qbh transcribe`: Transcribe every .wav file in `datasets` folder to a npy containing an interval array representing the audio.
* `docker-compose run qbh smbgt`: Match every query in npy format from `dataset/wav/` to every melody in npy format from `dataset/mid` using smbgt algorithm.
* docker-compose run qbh dtw: This is going to match every query in npy format from `dataset/wav/` to every melody in npy format from `dataset/mid` using dtw algorithm.
* `docker-compose run qbh prepare_pv`: Convert pv from mid scale to mod12
* `docker-compose run qbh match`: Match every query in mod12 format from `dataset/pv/` to every other query using dtw algorithm and output the scores into `scores.csv`. This script can take weeks to run, so it might be a good idea to use docker-compose run -d qbh match, this will run the container in the background and thus will keep running even if a ssh session is ended. A temporary file is created when running this script, so, if needed, it is possible to stop
  and restart it at any moment.
* `docker-compose run qbh rank_and_evaluate`: Rank and evaluate the score file.
