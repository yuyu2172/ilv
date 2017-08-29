import os
import pickle
import re
import subprocess
import warnings


def count_directories(base):
    return sum([os.path.isdir(os.path.join(base, dir_)) for dir_ in os.listdir(base)])


def interactive(result_base, selected_option=None):
    print('============= Set Result Base ==============')
    print('0:   set result_base as current directory')

    options = []  # List[(string, dict)]
    for dir_ in os.listdir(result_base):
        child_dir = os.path.join(result_base, dir_)
        if os.path.isdir(child_dir):
            pkl_fn = os.path.join(child_dir, 'settings.pkl')
            if os.path.exists(pkl_fn):
                with open(pkl_fn, 'rb') as f:
                    logs = pickle.load(f)
                if 'create_time' not in logs:
                    logs['create_time'] = None
                    warnings.warn('create_time not in settings.pkl')
                if 'message' not in logs:
                    logs['message'] = None
                options.append((child_dir, logs))
            else:
                empty_logs = {
                    'create_time': None,
                    'message': None}
                options.append((child_dir, empty_logs))

    # sort (from the newest to the oldest)
    options = sorted(sorted(options), key=lambda x: x[1]['create_time'], reverse=True)

    for i, option in enumerate(options):
        print('{}: {}  create_time={}  message={}  n_data={}'.format(
            i + 1 ,
            os.path.split(option[0])[1],
            option[1]['create_time'],
            option[1]['message'],
            count_directories(option[0])
        ))

    if selected_option is None:
        selected_option = int(raw_input("Please enter something: "))

    if selected_option == 0:
        return result_base
    elif 1 <= selected_option <= len(options):
        return options[selected_option - 1][0]
    else:
        raise ValueError('invalid input')
