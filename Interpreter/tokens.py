import enum


class Token:
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.token_type = TokenType(value)


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
    t_character_constant = 'char_const'
    t_assignment_operator = 'a_op'
    t_negation_operator = 'n_op'
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
