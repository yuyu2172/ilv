import ilv
import os.path as osp
from ilv import collect_results


# run with ``bokeh serve --show bokeh_app.py``

result_base = osp.expanduser('~/libraries/ilv/examples/train_mnist/result/')
dfs, args_list = collect_results.collect_results_chainer(result_base)
ilv.vis_log(
    dfs,
    'iteration',
    ['main/loss', 'validation/main/loss', 'main/accuracy', 'validation/main/accuracy'],
    ['min/main/loss'], args_list)
