import unittest
from io import StringIO
import source
import lexer
import tokens


class LexerTest(unittest.TestCase):

    def manage_source(self, data):
        self.code.write(data)
        self.code.seek(0)
        self.src.set_data(self.code)

    def setUp(self):
        self.code = StringIO()
        self.src = source.Source()
        self.lex = lexer.Lexer(self.src)

    def test_check_if_returns_when_token(self):
        code = "when"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_when)

    def test_check_if_returns_else_token(self):
        code = "else"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_else)

    def test_check_if_unknown_token(self):
        code = "&"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_unknown)

    def test_check_if_loop_token(self):
        code = "loop"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_loop)

    def test_check_sequence_of_tokens(self):
        code = "in out none"
        self.manage_source(code)
        token = [self.lex.get_token().token_type for _ in range(3)]
        self.assertEqual(token, [tokens.TokenType.t_in, tokens.TokenType.t_out, tokens.TokenType.t_none])

    def test_check_value_of_int_token(self):
        code = "123"
        self.manage_source(code)
        self.assertEqual(123, self.lex.get_token().value)

    def test_check_type_of_value(self):
        code = "asdf 123"
        self.manage_source(code)
        self.assertEqual(type(""), type(self.lex.get_token().value))
        self.assertEqual(type(0), type(self.lex.get_token().value))
