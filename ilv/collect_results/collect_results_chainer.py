import json
import os
import pandas as pd
import pickle

from ilv.collect_results.interactive import interactive


def read_json(path):
    with open(path, 'r') as f:
        j = json.load(f)
    return pd.DataFrame(j)


def collect_results_chainer(result_base, table_ys):
    """Gather multiple time series result data and concatenate them
    """
    dfs = []
    args_list = []
    count = 0
    for root, dirs, files in os.walk(result_base):
        if 'settings.pkl' in files:
            logs = [file_ for file_ in files if 'log' in file_]
            if len(logs) != 1:
                continue
            log = logs[0]
            df = read_json(os.path.join(root, log))
            df = df.interpolate()
            with open(os.path.join(root, 'settings.pkl'), 'rb') as f:
                logs = pickle.load(f)
            for key, val in logs.items():
                df[key] = val
            df['count'] = count
            dfs.append(df)
            args_list.append(logs)
            count += 1
    dfs = pd.concat(dfs)
    print('finished collecting')
    return dfs, args_list


def collect_results_chainer_interactive(result_base, table_ys):
    result_base = interactive(result_base)
    return collect_results_chainer(result_base, table_ys)
