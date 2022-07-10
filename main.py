import logging
import os
import argparse
# Files
import code_check
import variables


parser = argparse.ArgumentParser(description='A static code analyzer')
parser.add_argument('-p', '--path', nargs='?', default='./test', help='Path', type=str)
args = parser.parse_args()
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def report():
    # Prints out the error messages found in errors dict (sorted)
    for file_name, line_no in sorted(variables.errors.items()):
        for line, err in sorted(line_no.items()):
            for msg in sorted(err):
                print('{}: Line {}: {}'.format(file_name, line, msg))


def get_pys(dirpath, cwd=variables.cwd):
    # Given a directory path yields all .py file names (recursively)
    for dir_, dirs, files in os.walk(dirpath):
        for name in files:
            if name.endswith('.py'):
                rel_dir = os.path.relpath(dir_, cwd)
                yield rel_dir + '\\' + name
            os.path.join(dir_, name)


def start(path):
    # Starts the debugger for the file/path given, recursively
    logging.debug(variables.msg_start.substitute(path=path))
    if os.path.isdir(path):
        gen = get_pys(path)
        logging.debug(variables.msg_py_files.substitute(path=path))
        while True:
            try:
                code01 = code_check.Code(next(gen))
            except StopIteration:
                break
            code01.debug()
    elif path.endswith('.py'):
        code01 = code_check.Code(path)
        code01.debug()
    else:
        logging.error(variables.msg_dir_or_file)
    report()


if __name__ == "__main__":
    start(args.path)
