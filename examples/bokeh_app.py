import ilv
import os.path as osp


# run with ``bokeh serve --show bokeh_app.py``

result_base = osp.expanduser('~/libraries/chainer-tools/examples/train/result/')
dfs, args_list = ilv.collect_results.collect_results_chainer(result_base)
ilv.vis_log(dfs, 'iteration', ['main/loss'], args_list)
