import pandas as pd
import bokeh.charts
import bokeh.models.layouts
import os
import os.path as osp
from ilv.utils import filter_dict, list_of_dict_to_dict_of_list, moving_average_1d
import numpy as np


np.random.seed(1)


def find_valid_keys(args_list, black_list=['outdir', 'gpu']):
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
    # prepare and preprocess dataframes
    dict_args = list_of_dict_to_dict_of_list(args_list)
    valid_keys = find_valid_keys(args_list)
    dict_args = filter_dict(dict_args, valid_keys)
    labels = find_labels(args_list, valid_keys)

    # add hover functionality
    hover = bokeh.models.HoverTool(
            tooltips=[
                ("y", "$y"),
                ("label", "@legend"),
            ])
    p = bokeh.plotting.figure(tools=[hover], plot_width=1200, plot_height=850)

    table_y_values = []
    xs = []
    ys = []
    descs = []
    for i, (args, label) in enumerate(zip(args_list, labels)):
        # get df from a result
        tmp = dfs
        for key, val in args.items():
            tmp = tmp[tmp[key] == val]

        xs.append(tmp[x].values.tolist())
        ys.append(tmp[y].values.tolist())
        descs.append([label] * len(tmp))
        table_y_values.append(tmp[table_y].values.tolist()[0])
    
    # build empty multi line graph
    multi_l_source = bokeh.plotting.ColumnDataSource(
        {'xs': [], 'ys': [], 'descs': [], 'legend': []})
    multi_l = p.multi_line(
        xs='xs', ys='ys', source=multi_l_source, legend='legend')

    # build datatable
    # build columns
    columns = []
    for key in valid_keys + [table_y]:
        columns.append(
            bokeh.models.widgets.TableColumn(field=key, title=key))
    # build data for the table
    data = {}
    for args in args_list:
        for key in valid_keys:
            if key not in data:
                data[key] = []
            data[key].append(args[key])
    data[table_y] = table_y_values
    data['index'] = range(len(args_list))
    data_table_source = bokeh.models.ColumnDataSource(data)
    data_table = bokeh.models.widgets.DataTable(
        source=data_table_source, columns=columns,
        width=600, height=850)

    # NOTE: callback_policy, callback_throttle are not supported for
    # callbacks written in Python.
    window_slider = bokeh.models.Slider(
        start=1, end=100, value=1, step=1,
        title='window size')

    ids = np.random.permutation(256)
    def update(attr, old, new):
        raw_indices = data_table_source.selected['1d']['indices']

        # after sorting, the order of index changes
        reordered_keys = data_table_source.data['index']
        selected_indices = []
        for idx in raw_indices:
            selected_indices.append(reordered_keys[idx])
        
        # get list of selected line data
        selected_xs = []
        selected_ys = []
        selected_descs = []
        selected_labels = []
        for idx in selected_indices:
            selected_xs.append(xs[idx])
            selected_ys.append(
                moving_average_1d(ys[idx], window_slider.value))
            selected_descs.append(descs[idx])
            selected_labels.append(labels[idx])
        
        # get colors
        selected_colors = []
        colors = bokeh.palettes.Inferno256
        for i in range(len(selected_indices)):
            selected_colors.append(colors[ids[i]])

        # set data dict
        data = dict(xs=selected_xs, ys=selected_ys, descs=selected_descs,
                    line_color=selected_colors,
                    legend=selected_labels)
        multi_l.data_source.data = data

        # set color 
        # https://groups.google.com/a/continuum.io/forum/#!topic/bokeh/MMxjMK84n5M
        multi_l.glyph.line_color = 'line_color'

    data_table_source.on_change('selected', update)
    window_slider.on_change('value', update)

    # add tools
    p.add_tools(bokeh.models.BoxZoomTool())
    p.add_tools(bokeh.models.ResizeTool())
    p.add_tools(bokeh.models.SaveTool())
    p.add_tools(bokeh.models.WheelZoomTool())
    #p.add_tools(bokeh.models.WheelPanTool())
    p.add_tools(bokeh.models.RedoTool())
    p.add_tools(bokeh.models.ResetTool())
    p.add_tools(bokeh.models.UndoTool())
    p.add_tools(bokeh.models.ZoomOutTool())
    p.add_tools(bokeh.models.ZoomInTool())

    # build layout
    sliders = bokeh.layouts.widgetbox(window_slider)
    layout = bokeh.layouts.gridplot(
        [[data_table, p],
         [sliders]], sizing_mode='fixed')
    bokeh.io.curdoc().add_root(layout)


def vis_log(dfs, x, ys, table_ys, args_list):
    # visualization
    for y, table_y in zip(ys, table_ys):
        vis_log_single(dfs, args_list, y, table_y, x)
