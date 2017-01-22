import ilv
import os.path as osp


# run with ``bokeh serve --show bokeh_app.py``

result_base = osp.expanduser('~/libraries/ilv/examples/result/')
dfs, args_list = ilv.collect_results.collect_results_chainer(result_base)
ilv.vis_log(dfs, 'iteration', ['main/loss'], ['min/main/loss'], args_list)
