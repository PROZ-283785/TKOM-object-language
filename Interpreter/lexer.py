import tokens
from string import ascii_letters, digits, whitespace
import copy


class Lexer:
    key_values = ['when', 'else', 'loop', 'object', 'fun', 'operator', 'main', 'int']

    def __init__(self, source):
        self.source = source
        self.function_map = self.create_dict()
        self.string = ''

    def get_token(self):

        self.string = ''
        last_char = self.source.last_symbol
        if not self.is_white_character(last_char):
            symbol = last_char
        else:
            symbol = self.source.next_symbol()

        while self.is_white_character(symbol) or symbol == tokens.TokenType.t_comment.value:
            if symbol == 'EOF':
                return tokens.Token(identifier=copy.copy(self.string), value=tokens.TokenType.t_eof)
            if symbol == tokens.TokenType.t_comment.value:
                self.escape_comment()
            symbol = self.source.next_symbol()

        self.string += symbol
        token_type = self.function_map[symbol]()
        token = tokens.Token(identifier=copy.copy(self.string), value=token_type)

        return token

    def find_identifier(self):
        symbol = self.source.next_symbol()
        while self.is_letter(symbol) or self.is_number(symbol):
            self.string += symbol
            symbol = self.source.next_symbol()
        if self.string in self.key_values:
            return self.key_val_token(self.string)

        return tokens.TokenType.t_identifier

    def find_int(self):
        symbol = self.source.next_symbol()
        while self.is_number(symbol):
            self.string += symbol
            symbol = self.source.next_symbol()

        return tokens.TokenType.t_integer

    @staticmethod
    def is_white_character(symbol):
        if symbol in whitespace or symbol == 'EOF' or symbol == 'EOT':
            return True
        else:
            return False

    @staticmethod
    def is_letter(symbol):
        if symbol in ascii_letters:
            return True
        else:
            return False

    @staticmethod
    def is_number(symbol):
        if symbol in digits:
            return True
        else:
            return False

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

    def create_dict(self):
        d = dict()
        d.update(d.fromkeys(ascii_letters, self.find_identifier))
        d.update(d.fromkeys(digits, self.find_int))
        d['.'] = self.dot_token
        d[','] = self.comma_token
        d[';'] = self.semicolon_token
        d[':'] = self.colon_token
        d['{'] = self.left_brace_token
        d['}'] = self.right_brace_token
        d['('] = self.left_parenthesis_token
        d[')'] = self.right_parenthesis_token
        return d
