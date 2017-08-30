import bokeh.charts
import bokeh.models.layouts
import collections
import numpy as np
import warnings

from ilv.utils import filter_dict
from ilv.utils import list_of_dict_to_dict_of_list
from ilv.utils import moving_average_1d


np.random.seed(1)
colors_10_indices = np.random.permutation(10)
colors_255_indices = np.random.permutation(255)


def get_valid_keys(args_list, black_list=['out', 'gpu']):
    """Get list of keys that are going to be used.

    We define "valid" in the following sense:
        1. There need to be variations in the values of keys
            among the experiments.
        2. The key is not included in the black_list

    Returns:
        List of strings

    """
    keys = args_list[0].keys()
    valid_keys = []
    for key in keys:
        if key not in black_list:
            cur = None
            for args in args_list:
                if cur is None:
                    cur = args[key]
                if key not in args:
                    warnings.warn('{} not in args={}'.format(key, args))
                    continue
                if cur != args[key]:
                    valid_keys.append(key)
                    break
    return valid_keys


def get_identifiers(args_list, valid_keys):
    """Find string identifiers for each experiment. Used by pop-ups.

    Args:
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.

    Returns:
        identifiers (list of strings)

    """
    # ignore keys which have no variation among results
    identifiers = []
    for args in args_list:
        identifier = ''
        for key in valid_keys:
            if key in args:
                identifier += '{}={},'.format(key, args[key])
        identifiers.append(identifier)
    return identifiers


def filter_dataframes(dfs, xs, ys, table_ys, args_list, valid_keys):
    """Process necessary information from dataframes in the Bokeh format.

    In the following explanation, N is assumed to be the number of experiments.

    For xs_dict and ys_dict:
        These are dictionary of list of list.
        To make it simple, we focus on particular `x` in `xs`. Everything is
        the same for `ys_dict`.
        `x` is usually a timescale values such as iteration or epoch.
        Here are some characteristics:

            1. xs_dict[x] is list of list
            2. len(xs_dict[x]) == N
            3. xs_dict[x][i] is list. For example, if log is recorded every
                epoch and `x` is epoch, xs_dict[x][i] == [1, 2, 3, 4, ...].

    For tables:
        This is a dictionary of list of scalars or strings.
        The keys correspond to the column keys of the data table.
        The keys are the combination of all `valid_keys` and `table_ys`.
        tables[key][i] is `key` value recorded in the i-th experiment.
        For example, if key=='main/loss', this is the minimum loss value during
        training time recorded for the i-th experiment.

    Args:
        dfs (list of pd.DataFrame)
        xs (list of strings)
        ys (list of strings)
        table_ys (dictionary)
        args_list (list of dictionaries)
        valid_keys (list of strings)

    """
    # Descs:  descriptions
    # ys_dict == {string (y): List(Serial Data)}
    xs_dict = {x: [] for x in xs}
    ys_dict = {y: [] for y in ys}
    tables = collections.OrderedDict(
        [(key, []) for key in ['index'] + valid_keys + list(table_ys.keys())])
    for i, args in enumerate(args_list):
        # get df from a result
        tmp = dfs
        for key, val in args.items():
            if val is None:
                tmp = tmp[tmp[key].isnull()]
            else:
                tmp = tmp[tmp[key] == val]

        for x in xs:
            xs_dict[x].append(tmp[x].values.tolist())
        for y in ys:
            ys_dict[y].append(tmp[y].values.tolist())

        for table_y, value_type in table_ys.items():
            if value_type == 'min':
                tables[table_y].append(tmp[table_y].min())
            elif value_type == 'max':
                tables[table_y].append(tmp[table_y].max())
            else:
                raise ValueError
        for key in valid_keys:
            if key in args:
                tables[key].append(args[key])
            else:
                tables[key].append(None)

    tables['index'] = list(range(len(args_list)))
    return xs_dict, ys_dict, tables


# this code is based on bokeh/examples/app/line_on_off.py
def vis_log(dfs, xs, ys=None, table_ys=None, args_list=None,
            ignore_keys=[], table_width=600):
    """Merge all results on values ys

    Args:
        dfs (list of pd.DataFrame)
        xs (list of strings)
        ys (list of strings)
        table_ys (dictionary of strings): key is name of y to display on
            dictionary. The value is how to turn the vector value into
            scalar ({'min', 'max'}).
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.
        ignore_kes (list of strings): Keys to stop showing on table.
        table_width (int): Width of table. The default value is 600.

    """
    # This function can be divided into five parts.
    # 1. Process necessary information from given dataframes.
    # 2. Initialize the components (Static part of the visualization)
    #     This includes setting up the figure size,
    #     creating data tables and buttons.
    # 3. Confiure dynamic part.
    #     This function contains an element of user-interaction.
    #     User can click buttons and slides to configure what and how to
    #     visualize.
    # 4. Add tools
    # 5. Organize how different elements can be put together in a screen.

    if ys is None:
        ys = table_ys.keys()
    ignore_keys += ['index']

    # 1. prepare and preprocess dataframes
    dict_args = list_of_dict_to_dict_of_list(args_list)
    valid_keys = get_valid_keys(args_list)
    dict_args = filter_dict(dict_args, valid_keys)
    identifiers = get_identifiers(args_list, valid_keys)
    xs_dict, ys_dict, tables = filter_dataframes(
        dfs, xs, ys, table_ys, args_list, valid_keys)

    # 2. Construct elements
    p = bokeh.plotting.figure(plot_width=1800 - table_width, plot_height=825)
    # build empty multi line graph
    multi_l_source = bokeh.plotting.ColumnDataSource(
        {'xs': [], 'ys': [], 'descs': [], 'legend': []})
    multi_l = p.multi_line(
        xs='xs', ys='ys', source=multi_l_source, legend='legend')
    # build datatable
    columns = [bokeh.models.widgets.TableColumn(field=key, title=key) for
               key in tables.keys() if key not in ignore_keys]
    data_table_source = bokeh.models.ColumnDataSource(tables)
    data_table = bokeh.models.widgets.DataTable(
        source=data_table_source,
        columns=columns,
        width=table_width, height=825)
    # Sliders, buttons, menus, legends
    window_slider = bokeh.models.Slider(
        start=1, end=101, value=1, step=10,
        title='window size')
    xs_button = bokeh.models.widgets.RadioButtonGroup(
        labels=xs, active=0, width=600)
    ys_button = bokeh.models.widgets.RadioButtonGroup(
        labels=ys, active=0, width=600)
    menu = ['top_right', 'top_left', 'bottom_right', 'bottom_left']
    legend_button = bokeh.models.widgets.RadioButtonGroup(
        labels=menu, active=0, width=600)

    # 3. Start configuring user-interaction
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
        selected_identifiers = []
        for idx in selected_indices:
            x = xs[xs_button.active]
            y = ys[ys_button.active]
            selected_xs.append(xs_dict[x][idx])
            selected_ys.append(
                moving_average_1d(ys_dict[y][idx], window_slider.value))
            selected_identifiers.append(identifiers[idx])
            selected_descs.append([identifiers[idx]] * len(xs_dict[x][idx]))
        # get colors
        selected_colors = []
        if len(selected_indices) < 10:
            colors = bokeh.palettes.Category10_10
            color_indices = colors_10_indices
        else:
            colors = bokeh.palettes.Inferno256
            color_indices = colors_255_indices
        for i in range(len(selected_indices)):
            selected_colors.append(colors[color_indices[i]])
        # set data dict
        multi_l.data_source.data = dict(
            xs=selected_xs, ys=selected_ys,
            descs=selected_descs,
            line_color=selected_colors,
            legend=selected_identifiers)
        # set color
        # https://groups.google.com/a/continuum.io/forum/#!topic/bokeh/MMxjMK84n5M
        multi_l.glyph.line_color = 'line_color'
        p.legend.location = menu[legend_button.active]
    data_table_source.on_change('selected', update)
    window_slider.on_change('value', update)
    ys_button.on_change('active', update)
    xs_button.on_change('active', update)
    legend_button.on_change('active', update)

    # 4. add tools
    p.add_tools(bokeh.models.BoxZoomTool())
    p.add_tools(bokeh.models.ResizeTool())
    p.add_tools(bokeh.models.SaveTool())
    p.add_tools(bokeh.models.WheelZoomTool())
    p.add_tools(bokeh.models.RedoTool())
    p.add_tools(bokeh.models.ResetTool())
    p.add_tools(bokeh.models.UndoTool())
    p.add_tools(bokeh.models.ZoomOutTool())
    p.add_tools(bokeh.models.ZoomInTool())
    p.add_tools(
        bokeh.models.HoverTool(
            tooltips=[("y", "$y"), ("label", "@legend")])
    )

    # 5. build layout
    sliders = bokeh.layouts.widgetbox(window_slider)
    xs_ys_widgets = bokeh.layouts.widgetbox(
        xs_button, ys_button)
    legend_widget = bokeh.layouts.widgetbox(legend_button)
    layout = bokeh.layouts.gridplot(
        [[data_table, p],
         [sliders, xs_ys_widgets, legend_widget]], sizing_mode='fixed')
    bokeh.io.curdoc().add_root(layout)
