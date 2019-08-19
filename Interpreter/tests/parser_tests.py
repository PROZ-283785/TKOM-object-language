import unittest

import env
import lexer
import pars
import source


class ParserTest(unittest.TestCase):
    def manage_source(self, code):
        self.src.set_data(code)

    def setUp(self):
        self.src = source.StringSource()
        self.lex = lexer.Lexer(self.src)
        self.environment = env.Environment()
        self.parser = pars.Parser(self.lex, self.environment)

    def test_function(self):
        code = "(){ a = 5; out<<a; } \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_function(env.Identifier("main")))

    def test_assignment(self):
        code = "= 5 + 3 * 2 + ( 7 * 9 ) \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_assignment(env.Identifier("a")))

    def test_object(self):
        code = " extends Vehicle { a= None; b = 10; } \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_object(env.Identifier("a")))

    def test_attribute(self):
        code = "{get; set} = \'abcde\'; \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_attribute(env.Identifier("a")))

    def test_function_call(self):
        code = "(a, b, c, d);\0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_function_call(env.Identifier("a")))

    def test_method_call(self):
        code = ".run(a, b, c, d)\0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_method_call(env.Identifier("a")))

    def test_conditional_instruction(self):
        code = "when( a > 10 ){ a = 3; } else when (a < 10){out<<'a'} else {} \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_conditional_instruction())

    def test_loop(self):
        code = "loop( i = 1; i <= 10; i = i + 1){ j = i;} \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_loop())

    def test_out(self):
        code = "out<<abc; \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_out())

    def test_in(self):
        code = "in>>a; \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_in())

    def test_arithmetic_expression(self):
        code = "5 + 3 * 2 + ( 7 * 9 ) + 2 --- 3 * --2 + ( 4 / 2) \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_arithmetic_expression())

    def test_conditional_expression(self):
        code = " 2 * 4 >= 5 * 3 / 2 || 2 * 4 <= 5 * 6\0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_condition())

    def test_attribute_reference(self):
        code = ".speed \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_attribute_reference(env.Identifier("a"), False))

    def test_operator_overloading(self):
        code = "operator + (lhs, rhs, result out){ result = 2 ;} \0"
        self.manage_source(code)
        self.parser.consume_token()
        self.assertEqual(True, self.parser.try_parse_operator_overloading())
