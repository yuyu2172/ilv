from ilv import vis_log
import os.path as osp
from ilv import collect_results


# run with ``bokeh serve --show bokeh_app.py``

table_ys = {'validation/main/loss': 'min', 'validation/main/accuracy': 'max'}
result_base = osp.expanduser('~/libraries/ilv/examples/train_mnist/result/')
dfs, args_list = collect_results.collect_results_chainer(result_base, table_ys)
vis_log.vis_log(
    dfs,
    ['iteration', 'epoch'],
    ['main/loss', 'validation/main/loss', 'main/accuracy', 'validation/main/accuracy'],
    table_ys, args_list)
