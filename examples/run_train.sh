#!/usr/bin/env bash

python train_mnist.py --gpu 0 --out result/unit1000 --unit 1000
python train_mnist.py --gpu 0 --out result/unit500 --unit 500
python train_mnist.py --gpu 0 --out result/unit200 --unit 200
