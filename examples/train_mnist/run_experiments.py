import fire

from ilv.utils import run_experiments


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
    run_experiments(options, base_cmd, base_dir, gpu)


if __name__ == '__main__':
    fire.Fire(main)
