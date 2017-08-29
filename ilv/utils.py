from itertools import izip
from itertools import product
import os
import pandas as pd
import subprocess


def list_of_dict_to_dict_of_list(list_of_dict):
    # http://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    dict_of_list = {}
    for d in list_of_dict:
        for k, v in d.items():
            if k not in dict_of_list:
                dict_of_list[k] = [v]
            else:
                dict_of_list[k].append(v)
    return dict_of_list


def filter_dict(d, keys):
    filtered = {}
    for k in keys:
        filtered[k] = d[k]
    return filtered


def moving_average_1d(list_, window):
    series = pd.Series(list_)
    return series.rolling(window=window, center=True).mean().tolist()


def dict_of_list_to_list_of_dict(dicts):
    return list(dict(izip(dicts, x)) for x in product(*dicts.itervalues()))


def run_experiments(options, base_cmd, date_dir):
    options_list = dict_of_list_to_list_of_dict(options)
    for i, opts in enumerate(options_list):
        cmd = base_cmd
        out = os.path.join(date_dir, 'iter_{}'.format(i))
        cmd += ' --out {} '.format(out)

        for key, val in opts.items():
            cmd += ' --{} {} '.format(key, val)
        print(cmd)
        subprocess.call(cmd, shell=True)
