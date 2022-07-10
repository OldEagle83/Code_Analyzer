import logging
import re
import variables
import time
import ast
# File
import ast_expl

class Code:
    # Code class, requires path/filename

    def __init__(self, f_name):
        self.f_name = f_name
        self.args = dict()
        self.vars = dict()
        self.defaults = []


    def gen_err(self, line_no, code, level, issue=''):
        """
        Logs and prints a message with the appropriate level
        :param line_no: int: Line in which the error is found, starts from 0
        :param code: The error code as in the err_codes dictionary
        :param level: The level to log
        :param issue: The name of the obj that generated the error, defaults to ''
        :return: Nothing
        """
        if issue != '':
            error = variables.err_msg.substitute(path=self.f_name, line=line_no + 1, code=code,
                                                 msg=variables.err_codes[code].format(issue))
            variables.errors[self.f_name][line_no + 1].append(code + ' ' + variables.err_codes[code].format(issue))
        else:
            error = variables.err_msg.substitute(path=self.f_name, line=line_no + 1, code=code,
                                                 msg=variables.err_codes[code])
            variables.errors[self.f_name][line_no + 1].append(code + ' ' + variables.err_codes[code])
        if level == 'warning':
            logging.warning(error)
        elif level == 'info':
            logging.info(error)
        elif level == 'debug':
            logging.debug(error)
        elif level == 'error':
            logging.error(error)
        elif level == 'critical':
            logging.critical(error)
        return error

    def check_line_length(self, line):
        # Checks if the length of the line is 79 or less (True/False)
        return len(line.rstrip('\n')) <= 79

    def check_indent(self, line):
        # Checks if the line has standard indentation, 4 spaces. (True/False)
        spaces = re.findall(r'^ +\b', line)
        if len(spaces) != 0:
            for space in spaces:
                if len(space) % 4 != 0:
                    return False
        return True

    def check_semicolon(self, line):
        # Check if a semicolon is used in the line of code outside a comment
        results = re.findall(r'^[\w\s\W]*?;', line)
        if len(results) == 0:
            return True
        for result in results:
            if '#' in result or re.match(r"[\w\W\s=]+?'[\w; ]*?;", result) is not None:
                return True
        return False

    def check_inline(self, line):
        # Checks spacing of inline comments (True/False)
        try:
            assert line.index('#') == 0
        except ValueError:
            return True
        except AssertionError:
            try:
                assert re.match(r'^[\w\W]+?[^ ][ ][ ]#', line) is not None
            except AssertionError:
                return False
        return True

    def check_todo(self, line):
        # Checks if there are to-dos left in the comments (True/False)
        match = re.match(r'^[\w\W\s]*?#[\w\W\s]*?[Tt][Oo][Dd][Oo]', line)
        if match is not None:
            return False
        match = re.match(r'^[\w\W\s]*?\'\'\'[\w\W\s]*?[Tt][Oo][Dd][Oo]', line)
        if match is not None:
            return False
        return True

    def check_blank(self, text):
        # Checks if there are more than 3 empty lines before any code
        matches = []
        for match in re.findall(r'\n\n\n[\w\W]', text.decode()):
            matches.append(match.end())
        return [*matches]

    def check_construction(self, text):
        # Checks for no more than 1 space after class or def declaration, also returns the name if not
        if re.match(r'^class  +[\w][(]?[\w]*[)]?:', text) is not None:
            return False, 'class'
        if re.match(r'^ *def  +[\w\W]+:', text) is not None:
            return False, 'def'
        return True, ''

    def check_class(self, text):  # Pending deprecation
        # Checks if a class name is CamelCase, also returns the name if not
        match = re.match(r'^class  *[\w][(]?[\w]*[)]?:', text)
        try:
            class_name = re.match(r'[a-zA-Z_]+', match[0].lstrip('class').strip())
        except TypeError:
            return True, ''
        if not self.is_camel(class_name.group()):
            return False, class_name.group()
        return True, ''

    def check_def(self, text):  # Pending deprecation
        # Checks if a method/function is snake_case, also returns the name if not.
        def_name = re.match(r'^ *def [\w\W ]+:', text)
        if def_name is None:
            return True, ''
        def_name = def_name[0].strip().lstrip('def').strip().rstrip(':')
        if not self.is_snake(def_name):
            return False, def_name
        return True, ''

    def is_camel(self, word):
        # Checks if a word is CamelCase
        if word != word.title() or '_' in word:
            return False
        return True

    def is_snake(self, word):
        # Checks if a word is snake_case
        if word != word.lower():
            return False
        return True

    def ast_explore(self, code):
        """
        Fetches the following from code:
        - Argument names
        - Function names
        - Variable names
        - Argument default types
        :param code: Code to be checked.
        :return:
        """
        logging.debug(f'ast_explore started. Length of code: {len(code)}')
        get_defs = ast_expl.FunctionDef()
        get_vars = ast_expl.Assign()
        tree = ast.parse(code)
        get_defs.visit(tree)
        get_vars.visit(tree)
        self.args = get_defs.dict_of_args
        self.defs = get_defs.dict_of_defs
        self.vars = get_vars.dict_of_vars
        self.defaults = get_defs.list_of_defaults
        logging.debug(f'args: {self.args}')
        logging.debug(f'defs: {self.defs}')
        logging.debug(f'vars: {self.vars}')
        logging.debug(f'defaults: {self.defaults}')

    def debug(self):
        """
        Base debug method, handles and calls all other checks.
        Currently checks for:
        - S001 Line is too long (79 characters without \n)
        - S002 Indentation is not a multiple of 4
        - S003 Unnecessary semicolon after a statement
        - S004 Less than two spaces before inline comments
        - S005 Finds 'Todos' in the comments
        - S006 More than two blank lines preceding a code line
        - S007 Construction names
        - S008 Class names are CamelCase
        - S009 Method names are snake_case
        - S010 Argument names should be snake_case
        - S011 Variable names should be snake_case
        - S012 Default arguments must be immutable
        :return: Nothing
        """
        logging.debug(variables.msg_debug.format(self.f_name))
        variables.pop_errors(self.f_name)
        error_level = 'info'
        empty_line_counter = 0

        with open(self.f_name, 'r') as f:
            code = f.read()
            # Check code with ast
            self.ast_explore(code)
            f.seek(0)
            # Check code line by line for styling errors
            for number, line in enumerate(f):
                logging.debug(str(number + 1) + ': ' + line)
                try:
                    assert self.check_line_length(line)
                except AssertionError:
                    self.gen_err(number, 'S001', error_level)
                try:
                    assert self.check_indent(line)
                except AssertionError:
                    self.gen_err(number, 'S002', error_level)
                try:
                    assert self.check_semicolon(line)
                except AssertionError:
                    self.gen_err(number, 'S003', error_level)
                try:
                    assert self.check_inline(line)
                except AssertionError:
                    self.gen_err(number, 'S004', error_level)
                try:
                    assert self.check_todo(line)
                except AssertionError:
                    self.gen_err(number, 'S005', error_level)
                check, construction = self.check_construction(line)
                if check is False:
                    self.gen_err(number, 'S007', error_level, issue=construction)
                check, class_name = self.check_class(line)
                if check is False:
                    self.gen_err(number, 'S008', error_level, issue=class_name)
                if line == '\n':
                    empty_line_counter += 1
                elif empty_line_counter >= 3:
                    self.gen_err(number, 'S006', error_level)
                    empty_line_counter = 0
                else:
                    empty_line_counter = 0
        # Populate errors from ast
        for arg, line_no in self.args.items():
            if not self.is_snake(arg):
                self.gen_err(line_no - 1, 'S010', error_level, issue=arg)
        for definition, line_no in self.defs.items():
            if not self.is_snake(definition):
                self.gen_err(line_no - 1, 'S009', error_level, issue=definition)
        for var, line_no in self.vars.items():
            if not self.is_snake(var):
                self.gen_err(line_no - 1, 'S011', error_level, issue=var)
        for line_no in self.defaults:
            self.gen_err(line_no - 1, 'S012', error_level)
        time.sleep(1)
        logging.debug('Debugger done.')
        return