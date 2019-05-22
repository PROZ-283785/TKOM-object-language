import unittest
import source
import lexer
import tokens


class LexerTest(unittest.TestCase):

    def manage_source(self, code):
        self.src.set_data(code)

    def setUp(self):
        self.src = source.StringSource()
        self.lex = lexer.Lexer(self.src)

    def test_check_if_returns_when_token(self):
        code = "when \0"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_key_value)

    def test_check_if_returns_else_token(self):
        code = "else \0"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_key_value)

    def test_check_if_unknown_token(self):
        code = "& \0"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_unknown)

    def test_check_if_loop_token(self):
        code = "loop \0"
        self.manage_source(code)
        self.assertEqual(self.lex.get_token().token_type, tokens.TokenType.t_key_value)

    def test_check_sequence_of_tokens(self):
        code = "in out None \0"
        self.manage_source(code)
        token = [self.lex.get_token().token_type for _ in range(3)]
        self.assertEqual(token, [tokens.TokenType.t_key_value, tokens.TokenType.t_key_value, tokens.TokenType.t_key_value])

    def test_check_value_of_int_token(self):
        code = "123 \0"
        self.manage_source(code)
        self.assertEqual(123, self.lex.get_token().value)

    def test_check_type_of_value(self):
        code = "asdf 123 \0"
        self.manage_source(code)
        self.assertEqual(type(""), type(self.lex.get_token().value))
        self.assertEqual(type(0), type(self.lex.get_token().value))
