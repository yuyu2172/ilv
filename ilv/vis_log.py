import pandas as pd
import bokeh.charts
import bokeh.models.layouts
import os
import os.path as osp
from ilv.utils import filter_dict, list_of_dict_to_dict_of_list
import numpy as np


def find_valid_keys(args_list):
    keys = args_list[0].keys()
    valid_keys = []
    for key in keys:
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
def vis_log_single(dfs, args_list, y, x):
    """Merge all results on values ys 

    Args:
        dfs
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.
        y (string)
        x (string)
    """
    dict_args = list_of_dict_to_dict_of_list(args_list)
    valid_keys = find_valid_keys(args_list)
    dict_args = filter_dict(dict_args, valid_keys)
    labels = find_labels(args_list, valid_keys)

    hover = bokeh.models.HoverTool(
            tooltips=[
                ("y", "$y"),
                ("label", "@desc"),
            ])
    p = bokeh.plotting.figure(tools=[hover])
    ls = []
    off_props = dict(line_width=2, line_alpha=0.2)
    on_props = dict(line_width=2, line_alpha=0.7)
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
        l = p.line('x', 'y', source=source, legend=label,
                   color=bokeh.palettes.Category20_10[i], **on_props)
        ls.append(l)

    sliders_dict = {}
    sliders = []
    for key in valid_keys:
        # add two sliders for each key
        max_value = np.max(dict_args[key])
        min_value = np.min(dict_args[key])
        offset = (max_value - min_value) * 0.05
        min_slider = bokeh.models.widgets.Slider(
            title=key + '_min',
            value=min_value - offset,
            start=min_value - offset,
            end=max_value + offset)
        max_slider = bokeh.models.widgets.Slider(
            title=key + '_max',
            value=max_value + offset,
            start=min_value - offset,
            end=max_value + offset)
        sliders += [min_slider, max_slider]
        sliders_dict[key] = {}
        sliders_dict[key]['min'] = min_slider
        sliders_dict[key]['max'] = max_slider

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

    inputs = bokeh.layouts.widgetbox(*sliders)
    layout = bokeh.layouts.row(inputs, p)
    bokeh.io.curdoc().add_root(layout)
    bokeh.charts.save(layout)
    return ls


def vis_log(dfs, x, ys, args_list):
    # visualization
    for y in ys:
        vis_log_single(dfs, args_list, y, x)
