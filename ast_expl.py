import ast
import logging


class FunctionDef(ast.NodeVisitor):

    def __init__(self):
        self.dict_of_defs = dict()
        self.dict_of_args = dict()
        self.list_of_defaults = []

    def visit_FunctionDef(self, node):
        # Fetches functions, arguments and checks argument default types
        logging.debug(f'Visiting function {node}')
        self.dict_of_defs[node.name] = node.lineno
        for arg_name in node.args.args:
            self.dict_of_args[arg_name.arg] = arg_name.lineno
        for default in node.args.defaults:
            try:
                if isinstance(ast.literal_eval(default), (dict, set, list)):
                    self.list_of_defaults.append(default.lineno)
            except ValueError:
                self.list_of_defaults.append(default.lineno)
        logging.debug(f'{self.dict_of_defs}')


class Assign(ast.NodeVisitor):

    def __init__(self):
        self.dict_of_vars = dict()

    def visit_Assign(self, node):
        # Fetches all variable names
        logging.debug(f'Visiting var assignment {node}')
        try:
            self.dict_of_vars[node.targets[0].id] = node.targets[0].lineno
        except AttributeError:
            self.dict_of_vars[node.targets[0].attr] = node.targets[0].lineno
        logging.debug(f'{self.dict_of_vars}')
