import fire

from datetime import datetime
import os

from ilv.utils import run_experiments
from ilv.utils import dict_of_list_to_list_of_dict


def main(gpu=-1):
    ##########################################################################
    # User settings
    ##########################################################################
    base_cmd = 'python train.py'
    options = {
        'gpu': [gpu],
        'unit': [500, 1000],
    }
    base_dir = 'result'
    ##########################################################################
    dt = datetime.now()
    date = dt.strftime('%Y_%m_%d_%H_%M')
    date_dir = os.path.join(base_dir, date)

    options_list = dict_of_list_to_list_of_dict(options)
    run_experiments(options_list, base_cmd, date_dir)


if __name__ == '__main__':
    fire.Fire(main)
