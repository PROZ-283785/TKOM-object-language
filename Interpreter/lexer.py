import tokens
from string import ascii_letters, digits, whitespace


class Lexer:
    """
        Pytania: co powinien zrobić lexer gdy dostanie nieznany token
    """

    def __init__(self, source):
        self.source = source
        self.function_map = self.create_dict()
        self.value = None
        self.token = tokens.Token(None, 'unknown', None, None, None)

    def get_token(self):

        self.value = ''
        last_char = self.source.last_symbol

        if self.is_white_character(last_char):
            symbol = self.source.next_symbol()
        else:
            symbol = last_char

        while self.is_white_character(symbol) or symbol == tokens.TokenType.t_comment.value:

            if symbol == tokens.TokenType.t_comment.value:
                self.escape_comment()
            symbol = self.source.next_symbol()

        if symbol == 'EOF':
            line, column = self.source.line, self.source.column
            return tokens.Token(value=self.value, identifier=tokens.TokenType.t_eof, line=line, column=column,
                                pos_in_file=None)

        self.token.line, self.token.column, self.token.position_in_file = self.source.line, self.source.column, self.source.data_position - 1
        self.value += symbol
        token_type = self.function_map[symbol]()
        self.token.value = self.value
        self.token.token_type = token_type

        return self.token

    def find_identifier_or_keyword(self):
        symbol = self.source.next_symbol()
        while self.is_letter(symbol) or self.is_number(symbol):
            self.value += symbol
            symbol = self.source.next_symbol()
            if len(self.value) > 30:
                wrong_data = self.source.get_data_range(self.token.position_in_file, 40)
                raise NameError(
                    f"Error in line:{self.token.line} column:{self.token.column} {wrong_data} "
                    f"-> Identifier cannot have more than 30 characters!")
        if self.value in self.function_map.keys():
            return self.function_map[self.value]()
        return tokens.TokenType.t_identifier

    def find_int(self):
        integer = (ord(self.source.get_last_symbol()) - 48)
        symbol = self.source.next_symbol()
        while self.is_number(symbol):
            integer = integer * 10 + ord(symbol) - 48
            symbol = self.source.next_symbol()
        self.value = integer
        return tokens.TokenType.t_integer

    @staticmethod
    def is_white_character(symbol):
        return symbol in whitespace or symbol == 'EOT'

    @staticmethod
    def is_letter(symbol):
        return symbol in ascii_letters

    @staticmethod
    def is_number(symbol):
        return symbol in digits

    @staticmethod
    def key_val_token(string):
        for token in tokens.TokenType:
            if token.value == string:
                return token

    def escape_comment(self):
        symbol = self.source.next_symbol()
        while symbol != 'EOT':
            symbol = self.source.next_symbol()

    def dot_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_dot

    def comma_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_comma

    def semicolon_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_semicolon

    def colon_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_colon

    def left_brace_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_left_brace

    def right_brace_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_right_brace

    def left_parenthesis_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_left_parenthesis

    def right_parenthesis_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_right_parenthesis

    def check_if_assignment_or_comparison(self):
        symbol = self.source.next_symbol()

        if symbol == '=':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_comparison
        else:
            return tokens.TokenType.t_assignment

    def check_if_logical_and(self):
        symbol = self.source.next_symbol()

        if symbol == '&':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_logical_and
        else:
            return tokens.TokenType.t_unknown

    def check_if_logical_or(self):
        symbol = self.source.next_symbol()

        if symbol == '|':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_logical_or
        else:
            return tokens.TokenType.t_unknown

    def check_if_negation_or_inequality(self):
        symbol = self.source.next_symbol()

        if symbol == '=':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_inequality
        else:
            return tokens.TokenType.t_negation_operator

    def check_if_logical_or_output(self):
        symbol = self.source.next_symbol()

        if symbol == '=':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_loe
        elif symbol == '<':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_output
        else:
            return tokens.TokenType.t_less

    def check_if_logical_or_input(self):
        symbol = self.source.next_symbol()

        if symbol == '=':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_goe
        elif symbol == '>':
            self.value += symbol
            self.source.next_symbol()
            return tokens.TokenType.t_input
        else:
            return tokens.TokenType.t_greater

    def addition_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_addition

    def multiplication_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_multiplication

    def division_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_division

    def when_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_when

    def else_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_else

    def loop_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_loop

    def operator_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_operator

    def in_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_in

    def out_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_out

    def extends_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_extends

    def none_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_none

    def get_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_get

    def set_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_set

    def this_keyword_token(self):
        self.source.next_symbol()
        return tokens.TokenType.t_this

    def check_if_number_or_difference_token(self):
        symbol = self.source.next_symbol()

        if symbol in digits:
            self.value += symbol
            self.find_int()
            return
        else:
            return tokens.TokenType.t_difference

    def create_dict(self):

        d = dict()
        d.update(d.fromkeys(ascii_letters, self.find_identifier_or_keyword))
        d.update(d.fromkeys(digits, self.find_int))
        d['.'] = self.dot_token
        d[','] = self.comma_token
        d[';'] = self.semicolon_token
        d[':'] = self.colon_token
        d['{'] = self.left_brace_token
        d['}'] = self.right_brace_token
        d['('] = self.left_parenthesis_token
        d[')'] = self.right_parenthesis_token
        d['='] = self.check_if_assignment_or_comparison
        d['&'] = self.check_if_logical_and
        d['|'] = self.check_if_logical_or
        d['!'] = self.check_if_negation_or_inequality
        d['<'] = self.check_if_logical_or_output
        d['>'] = self.check_if_logical_or_input
        d['+'] = self.addition_token
        d['*'] = self.multiplication_token
        d['-'] = self.check_if_number_or_difference_token
        d['/'] = self.division_token
        d['when'] = self.when_keyword_token
        d['else'] = self.else_keyword_token
        d['loop'] = self.loop_keyword_token
        d['operator'] = self.operator_keyword_token
        d['in'] = self.in_keyword_token
        d['out'] = self.out_keyword_token
        d['extends'] = self.extends_keyword_token
        d['none'] = self.none_keyword_token
        d['get'] = self.get_keyword_token
        d['set'] = self.set_keyword_token
        d['this'] = self.this_keyword_token
        return d
