#!/usr/bin/env bash

python train_mnist.py --gpu 0 --outdir result/unit1000 --unit 1000
python train_mnist.py --gpu 0 --outdir result/unit500 --unit 500
python train_mnist.py --gpu 0 --outdir result/unit200 --unit 200
