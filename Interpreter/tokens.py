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

    t_identifier = 'identifier'
    t_integer = 'int'
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
    t_key_value = 'k_val'
    t_index = '[]'


t_operator = [TokenType.t_comparison, TokenType.t_assignment, TokenType.t_inequality, TokenType.t_goe, TokenType.t_loe, TokenType.t_less, TokenType.t_greater, TokenType.t_output, TokenType.t_input, TokenType.t_addition, TokenType.t_division, TokenType.t_multiplication, TokenType.t_difference]
t_logical_operators = [TokenType.t_logical_and, TokenType.t_logical_or]
t_relational_operators = [TokenType.t_goe, TokenType.t_loe, TokenType.t_less, TokenType.t_greater, TokenType.t_comparison, TokenType.t_inequality]
t_multiplication_operators = [TokenType.t_multiplication, TokenType.t_division]
t_addition_operators = [TokenType.t_addition, TokenType.t_difference]
