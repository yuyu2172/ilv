from __future__ import division

from datetime import datetime
import fire
import os

from ilv.utils import run_experiments_multiprocess


def main(gpus=[0, 0]):
    ##########################################################################
    # User settings
    ##########################################################################
    base_cmd = 'python train.py'
    options = {
        'unit': [500, 1000, 1500, 2000, 2500],
    }
    base_dir = 'result'
    gpus = [0, 0]
    ##########################################################################

    dt = datetime.now()
    date = dt.strftime('%Y_%m_%d_%H_%M')
    date_dir = os.path.join(base_dir, date)

    run_experiments_multiprocess(
        options, base_cmd, date_dir, gpus)


if __name__ == '__main__':
    fire.Fire(main)
