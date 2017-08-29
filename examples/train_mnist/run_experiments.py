import fire

from datetime import datetime
import os

from ilv.utils import dict_of_list_to_list_of_dict
from ilv.utils import run_experiments
from ilv.utils import run_experiments_multiprocess


def main(gpu=-1):
    ##########################################################################
    # User settings
    ##########################################################################
    base_cmd = 'python train.py'
    options = {
        'unit': [500, 1000],
    }
    base_dir = 'result'
    ##########################################################################
    dt = datetime.now()
    date = dt.strftime('%Y_%m_%d_%H_%M')
    date_dir = os.path.join(base_dir, date)
    options_list = dict_of_list_to_list_of_dict(options)

    if isinstance(gpu, (tuple, list)):
        run_experiments_multiprocess(options_list, base_cmd, date_dir, gpu)
    elif isinstance(gpu, int):
        for options in options_list:
            options.update({'gpu': gpu})
        run_experiments(options_list, base_cmd, date_dir)


if __name__ == '__main__':
    fire.Fire(main)
