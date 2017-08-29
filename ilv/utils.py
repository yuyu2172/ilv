from itertools import izip
from itertools import product
import math
import multiprocessing
import os
import pandas as pd
import subprocess


def list_of_dict_to_dict_of_list(list_of_dict):
    # http://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    dict_of_list = dict()
    for d in list_of_dict:
        for k, v in d.items():
            if k not in dict_of_list:
                dict_of_list[k] = [v]
            else:
                dict_of_list[k].append(v)
    return dict_of_list


def filter_dict(d, keys):
    filtered = dict()
    for k in keys:
        filtered[k] = d[k]
    return filtered


def moving_average_1d(list_, window):
    series = pd.Series(list_)
    return series.rolling(window=window, center=True).mean().tolist()


def dict_of_list_to_list_of_dict(dicts):
    ld = list()
    for x in product(*dicts.itervalues()):
        ld.append(dict(izip(dicts, x)))
    return ld

    return list(dict(izip(dicts, x)) for x in product(*dicts.itervalues()))


def split_list_equally(l, n):
    """
    Length of each chunk is at maximum n.

    """
    size = int(math.ceil(len(l) / n))
    return [l[i:i+size] for i in range(0, len(l), size)]


def run_experiments(options_list, base_cmd, date_dir, indices=None):
    for i, opts in enumerate(options_list):
        if indices is None:
            index = i
        else:
            index = indices[i]
        cmd = base_cmd
        out = os.path.join(date_dir, 'iter_{}'.format(index))
        cmd += ' --out {} '.format(out)

        for key, val in opts.items():
            cmd += ' --{} {} '.format(key, val)
        print(cmd)
        subprocess.call(cmd, shell=True)


def run_experiments_multiprocess(options, base_cmd,
                                 date_dir, gpus):
    options_list_all = dict_of_list_to_list_of_dict(options)
    indices = list(range(len(options_list_all)))
    options_list_split = split_list_equally(options_list_all, len(gpus))
    indices_split = split_list_equally(indices, len(gpus))
    for options_list, gpu in zip(options_list_split, gpus):
        for options in options_list:
            options.update({'gpu': gpu})

    ps = list()
    for gpu, options_list, indices in zip(
            gpus, options_list_split, indices_split):
        p = multiprocessing.Process(
            target=run_experiments,
            args=(options_list, base_cmd, date_dir, indices))
        p.start()
        ps.append(p)

    for p in ps:
        p.join()
