import pandas as pd
import bokeh.charts
import bokeh.models.layouts
import os
import os.path as osp
from ilv.utils import filter_dict, list_of_dict_to_dict_of_list
import numpy as np


def find_valid_keys(args_list, black_list=['outdir']):
    keys = args_list[0].keys()
    valid_keys = []
    for key in keys:
        if key not in black_list:
            cur = None
            for args in args_list:
                if cur is None:
                    cur = args[key]
                if cur != args[key]:
                    valid_keys.append(key)
                    break
    return valid_keys


def find_labels(args_list, valid_keys):
    """
    Args:
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.

    Returns:
        labels (list of strings)
    """
    # ignore keys which have no variation among results
    labels = []
    for args in args_list:
        label = ''
        valid_args = {}
        for key in valid_keys:
            label += '{}={},'.format(key, args[key])
        labels.append(label)
    return labels


# this code is based on bokeh/examples/app/line_on_off.py
def vis_log_single(dfs, args_list, y, table_y, x):
    """Merge all results on values ys 

    Args:
        dfs
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.
        y (string)
        x (string)
    """
    # TODO: use multiple lines instead of line
    # https://github.com/bokeh/bokeh/issues/2682
    # update graph property in callback
    dict_args = list_of_dict_to_dict_of_list(args_list)
    valid_keys = find_valid_keys(args_list)
    dict_args = filter_dict(dict_args, valid_keys)
    labels = find_labels(args_list, valid_keys)


    # add hover functionality
    hover = bokeh.models.HoverTool(
            tooltips=[
                ("y", "$y"),
                ("label", "@desc"),
            ])
    p = bokeh.plotting.figure(tools=[hover])

    ls = []
    off_props = dict(line_width=2, line_alpha=0.2)
    on_props = dict(line_width=2, line_alpha=0.7)
    ids = np.random.permutation(256)
    table_y_values = []
    for i, (args, label) in enumerate(zip(args_list, labels)):
        # get df from a result
        tmp = dfs
        for key, val in args.items():
            tmp = tmp[tmp[key] == val]

        # this is necessary to make hover visualization
        source = bokeh.plotting.ColumnDataSource(
            {'x': tmp[x].values.tolist(),
             'y': tmp[y].values.tolist(),
             'desc': [label] * len(tmp)})
        legend = None
        l = p.line('x', 'y', source=source, legend=legend,
                   color=bokeh.palettes.Inferno256[ids[i]], **on_props)
        table_y_values.append(tmp[table_y].values.tolist()[0])
        ls.append(l)

    # build datatable
    columns = [
        bokeh.models.widgets.TableColumn(field='label', title='label'),
        bokeh.models.widgets.TableColumn(field=table_y, title=table_y)]
    checks = [0] * len(labels)
    source = bokeh.models.ColumnDataSource(
        {'label': labels, table_y: table_y_values, 'check': checks})
    source.callback = bokeh.models.CustomJS(
        args=dict(source=source),
        code="""
                var indices = source.selected["1d"].indices
                var checks = source.get('data')['check'];
                for (var i = 0; i < checks.length; i++) {
                    checks[i] = 0;
                }
                for (var i = 0; i < indices.length; i++) {
                    checks[i] = 1;
                }
        """)
    data_table = bokeh.models.widgets.DataTable(
        source=source, columns=columns,
        width=400, height=200, editable=True)

    def update(attr, old, new):
        for i, l in enumerate(ls):
            for key in sliders_dict.keys():
                min_value = sliders_dict[key]['min'].value
                max_value = sliders_dict[key]['max'].value
                if (min_value <= args_list[i][key] and
                        max_value >= args_list[i][key]):
                    l.glyph.line_alpha = on_props['line_alpha']
                else:
                    ls[i].glyph.line_alpha = off_props['line_alpha']
    for slider in sliders:
        slider.on_change('value', update)

    # add tools
    p.add_tools(bokeh.models.SaveTool())
    p.add_tools(bokeh.models.WheelZoomTool())

    # add widgets
    inputs = bokeh.layouts.widgetbox(*sliders)


    # build layout
    layout = bokeh.layouts.row(data_table, p)
    bokeh.io.curdoc().add_root(layout)
    #bokeh.charts.save(layout)
    return ls


def vis_log(dfs, x, ys, table_ys, args_list):
    # visualization
    for y, table_y in zip(ys, table_ys):
        vis_log_single(dfs, args_list, y, table_y, x)
