import enum


class Token:
    def __init__(self, identifier, value, line, column):
        self.identifier = identifier
        self.token_type = TokenType(value)
        self.line = line
        self.column = column

    def __str__(self):
        return "{}:{} {} {}".format(self.line, self.column, self.identifier, self.token_type)

    def __repr__(self):
        return self.__str__()


class NoValue(enum.Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class TokenType(enum.Enum):
    t_when = 'when'
    t_else = 'else'
    t_loop = 'loop'
    t_object = 'object'
    t_fun = 'fun'
    t_operator = 'operator'
    t_main = 'main'
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
    t_logical_operator = 'l_op'
    t_mathematical_operator = 'm_op'
    t_input_function = 'in_fun'
    t_output_function = 'out_fun'
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
