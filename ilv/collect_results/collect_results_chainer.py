import pandas as pd
import os
import os.path as osp


def collect_results_chainer(result_base):
    """Gather multiple time series result data and concatenate them
    """
    dfs = []
    args_list = []
    count = 0
    for root, dirs, files in os.walk(result_base):
        if 'log' in files and 'args' in files:
            df = pd.read_json(osp.join(root, 'log'))
            df = df.interpolate()
            with open(osp.join(root, 'args'), 'r') as f:
                l = f.read()
                args = eval(l)
            for key, val in args.items():
                df[key] = val
            df['count'] = count
            dfs.append(df)
            args_list.append(args)
            count += 1
    dfs = pd.concat(dfs)
    return dfs, args_list
