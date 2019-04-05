import enum


class Token:
    def __init__(self, value, identifier, line, column, pos_in_file):
        self.value = value
        self.token_type = TokenType(identifier)
        self.line = line
        self.column = column
        self.position_in_file = pos_in_file

    def __str__(self):
        return f"{self.line}:{self.column} {self.position_in_file} {self.value} {type(self.value)} {self.token_type}"

    def __repr__(self):
        return self.__str__()


class TokenType(enum.Enum):
    t_this = 'this'
    t_when = 'when'
    t_else = 'else'
    t_loop = 'loop'
    t_operator = 'operator'
    t_identifier = 'identifier'
    t_integer = 'int'
    t_in = 'in'
    t_out = 'out'
    t_extends = 'extends'
    t_none = 'none'
    t_character_constant = 'char_const'
    t_negation = '!'
    t_logical_and = '&&'
    t_logical_or = '||'
    t_unknown = 'unknown'
    t_eof = 'eof'
    t_left_parenthesis = '('
    t_right_parenthesis = ')'
    t_semicolon = ';'
    t_dot = '.'
    t_left_brace = '{'
    t_right_brace = '}'
    t_comment = '#'
    t_comma = ','
    t_colon = ':'
    t_comparison = '=='
    t_assignment = '='
    t_inequality = '!='
    t_goe = '>='
    t_loe = '<='
    t_less = '<'
    t_greater = '>'
    t_output = '<<'
    t_input = '>>'
    t_addition = '+'
    t_division = '/'
    t_multiplication = '*'
    t_difference = '-'
    t_get = 'get'
    t_set = 'set'
