import os
import string

cwd = os.getcwd()
errors = dict()
err_codes = {'S001': 'Line too long.',
             'S002': 'Indentation is not a multiple of four',
             'S003': 'Unnecessary semicolon after a statement',
             'S004': 'Less than two spaces before inline comments',
             'S005': 'TODO found',
             'S006': 'More than two blank lines preceding a code line',
             'S007': "Too many spaces after '{}'",
             'S008': "Class name '{}' should use CamelCase",
             'S009': "Function name '{}' should use in snake_case",
             'S010': "Argument name '{}' should be snake_case",
             'S011': "Variable '{}' in function should be snake_case",
             'S012': "Default argument value is mutable"}


err_msg = string.Template('$path: Line $line: $code $msg')
msg_dir_or_file = 'Please enter a directory or the path to a .py file.'
msg_start = string.Template('Program start with $path')
msg_py_files = string.Template('Getting .py files: $path')
msg_debug = 'Debugger start for {}'


def pop_errors(f_name):
    errors[f_name] = dict()
    for n in range(sum(1 for line in open(f_name)) + 1):
        errors[f_name][n + 1] = []

