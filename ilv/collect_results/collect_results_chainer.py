import pandas as pd
import os
import os.path as osp


def collect_results_chainer(result_base, table_ys):
    """Gather multiple time series result data and concatenate them
    """
    dfs = []
    args_list = []
    count = 0
    for root, dirs, files in os.walk(result_base):
        if 'log_0' in files or 'log' in files and 'args' in files:
            if 'args' in files:
                logs = [file_ for file_ in files if 'log' in file_]
                if len(logs) != 1:
                    continue
                log = logs[0]
                df = pd.read_json(osp.join(root, log))
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
    print('finished collecting')
    return dfs, args_list
