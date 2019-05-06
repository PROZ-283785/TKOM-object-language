
class Error:

    def __init__(self, source):
        self.source = source

    def get_error(self, token, message):
        return f"Error in line:{token.line} column:{token.column} \"{self.source.get_data_range(token.position_in_file - 5, 10)}\"  -> {message}"


semicolon_message = "Missing semicolon"
left_parenthesis_message = "Missing left parenthesis"
right_parenthesis_message = "Missing right parenthesis"
left_brace_message = "Missing left brace"
right_brace_message = "Missing right brace"
identifier_message = "Missing identifier"
invalid_syntax_message = "Invalid syntax"
dot_message = "Missing dot"
assignment_operator_message = "Missing assignment operator"
