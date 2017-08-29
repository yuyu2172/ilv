import fire

from datetime import datetime
from itertools import product
from itertools import izip
import os
import subprocess


# Dictionary of lists to list of dictionaries
def dl_to_ld(dicts):
    return list(dict(izip(dicts, x)) for x in product(*dicts.itervalues()))


def main(gpu=-1):
    ##########################################################################
    # User settings
    ##########################################################################
    base_cmd = 'python train_mnist.py'
    options = {
        'gpu': [gpu],
        'unit': [500, 1000],
    }
    base_dir = 'result'
    ##########################################################################

    options_list = dl_to_ld(options)
    dt = datetime.now()
    date = dt.strftime('%Y_%m_%d_%H_%M')

    for i, opts in enumerate(options_list):
        cmd = base_cmd
        out = os.path.join(base_dir, date, 'iter_{}'.format(i))
        cmd += ' --out {} '.format(out)

        for key, val in opts.items():
            cmd += ' --{} {} '.format(key, val)
        print(cmd)
        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    fire.Fire(main)

