from copy import copy

import env
import error_messages
import tokens


class Parser:

    def __init__(self, lex):
        self.lexer = lex
        self.current_token = lex.get_token()
        self.previous_token = None
        self.error_message_buffer = []
        self.error_handler = error_messages.Error(self.lexer.source)

    def consume_token(self):
        self.previous_token = copy(self.current_token)
        self.current_token = self.lexer.get_token()

    def parse(self):
        while self.current_token.token_type != tokens.TokenType.t_eof:
            if self.try_parse_identifier():
                if not(self.try_parse_function() or self.try_parse_object()):
                    raise Exception("Powinna być funkcja albo obiekt")
            else:
                break
        if len(self.error_message_buffer) == 0:
            return True
        else:
            for message in self.error_message_buffer:
                print(message)
            return False

    def try_parse_function(self):
        # lewy_nawias, [lista_argumentów], prawy_nawias
        # [słowo_kluczowe_extends, identyfikator], blok
        if not self.try_parse_left_parenthesis():
            return False
        self.try_parse_list_of_arguments()
        if not self.try_parse_right_parenthesis():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        self.try_parse_extends()
        self.try_parse_block()

    def try_parse_block(self):
        # lewy_nawias_klamrowy, {instrukcja}, prawy_nawias_klamrowy
        if not self.try_parse_left_brace():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_brace_message))
            raise Exception("Brak lewego nawiasu")
        self.try_parse_instructions()
        if not self.try_parse_right_brace():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_brace_message))
            raise Exception("Brak prawego nawiasu")
        return True

    def try_parse_object(self):
        # [słowo_kluczowe_extends, identyfikator], lewy_nawias_klamrowy,
        # {atrybut | metoda | przeciążanie_operatora}, prawy_nawias_klamrowy
        self.try_parse_extends()
        if not self.try_parse_left_brace():
            return False
        while not self.try_parse_right_brace():
            if not(self.try_parse_method_or_attribute() or self.try_parse_operator_overloading()):
                raise Exception("Musi byc atrybut, metoda lub przeciazenie")
        return True

    def try_parse_list_of_arguments(self):
        # { argument_z_przecinkiem }, argument
        if self.try_parse_argument():
            if self.try_parse_comma():
                if not self.try_parse_list_of_arguments():
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, "invalid syntax"))
                    raise Exception("Blednie podana lista argumentow")
            return True
        else:
            return False

    def try_parse_argument(self):
        # identyfikator, [ słowo_kluczowe_in ], [ słowo_kluczowe_out ]
        if not self.try_parse_identifier():
            return False
        if self.try_parse_in_keyword():
            pass
        if self.try_parse_out_keyword():
            pass
        return True

    def try_parse_extends(self):
        if self.try_parse_extends_keyword():
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Powinien byc ident po extends")
        return True

    def try_parse_instructions(self):
        # przypisanie | wywołanie_funkcji_metody | instrukcja_warunkowa | pętla |
        # obsługa_wejścia_wyjścia
        if self.try_parse_assignment_or_method_function_call() or self.try_parse_conditional_instruction() or self.try_parse_loop() or self.try_parse_in_out():
            while self.try_parse_assignment_or_method_function_call() or self.try_parse_conditional_instruction() or self.try_parse_loop() or self.try_parse_in_out():
                continue
            return True
        else:
            return False

    def try_parse_method_or_attribute(self):
        if self.try_parse_identifier():
            if not (self.try_parse_method() or self.try_parse_attribute()):
                raise Exception("Musi byc metoda lub atrybut")
            return True
        else:
            return False

    def try_parse_assignment_or_method_function_call(self):
        if self.try_parse_assignment_with_this():
            if not self.try_parse_semicolon():
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            return True
        if self.try_parse_identifier():
            if not (self.try_parse_function_or_method_call() or self.try_parse_assignment()):
                raise Exception("Musi byc wywolanie lub przypisanie")
            if not self.try_parse_semicolon():
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            return True
        return False

    def try_parse_method(self):
        # lewy_nawias, [lista_argumentów], prawy_nawias, [dwukropek,
        #                                                 identyfikator, lewy_nawias, [lista_argumentów],
        #                                                 prawy_nawias], blok
        if not self.try_parse_left_parenthesis():
            return False
        self.try_parse_list_of_arguments()
        if not self.try_parse_right_parenthesis():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        if self.try_parse_colon():
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Powinien byc identyfikator")
            if not self.try_parse_left_parenthesis():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
                raise Exception("Brak lewego nawiasu")
            self.try_parse_list_of_arguments()
            if not self.try_parse_right_parenthesis():
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                raise Exception("Brak prawego nawiasu")
        self.try_parse_block()
        return True

    def try_parse_operator_overloading(self):
        # słowo_kluczowe_operator, operator, lewy_nawias,
        # [lista_argumentów], prawy_nawias, blok
        if not self.try_parse_operator_keyword():
            return False
        self.try_parse_operator()
        if not self.try_parse_left_parenthesis():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
            raise Exception("Brak lewego nawiasu")
        self.try_parse_list_of_arguments()
        if not self.try_parse_right_parenthesis():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        self.try_parse_block()
        return True

    def try_parse_attribute(self):
        #  [lewy_nawias_klamrowy, [słowo_kluczowe_get, średnik],
        #                 [słowo_kluczowe_set, średnik], prawy_nawias_klamrowy],
        #                 operator_przypisania,
        # (stała_znakowa | słowo_kluczowe_none | operator_indeksu |
        #  wyrażenie_arytmetyczne), średnik;
        if self.try_parse_left_brace():
            if self.try_parse_get_keyword():
                if not self.try_parse_semicolon():
                    self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if self.try_parse_set_keyword():
                if not self.try_parse_semicolon():
                    self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if not self.try_parse_right_brace():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.right_brace_message))
                raise Exception("Brak prawego nawiasu")
            if not self.try_parse_assignment_operator():
                raise Exception("Powinno byc przypisanie")
        elif not self.try_parse_assignment_operator():
            return False
        if not (self.try_parse_character_constant() or self.try_parse_none_keyword() or self.try_parse_index() or self.try_parse_arithmetic_expression()):
            raise Exception("Brak (stała_znakowa | słowo_kluczowe_none | operator_indeksu |  wyrażenie_arytmetyczne)")
        if not self.try_parse_semicolon():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        return True

    def try_parse_assignment(self):
        # operator_przypisania, wyrażenie_arytmetyczne, średnik
        if self.try_parse_assignment_operator():
            if not self.try_parse_arithmetic_expression():
                raise Exception("Brak wyrazenia arytmetycznego")
            return True
        return False

    def try_parse_assignment_with_this(self):
        # [słowo_kluczowe_this, kropka], identyfikator, operator_przypisania,
        # wyrażenie_arytmetyczne
        if self.try_parse_this_keyword():
            if not self.try_parse_dot():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.dot_message))
                raise Exception("Musi byc kropka")
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Musi byc ident")
            if not self.try_parse_assignment_operator():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.assignment_operator_message))
            if not self.try_parse_arithmetic_expression():
                raise Exception("Brak wyr arytm")
            return True
        return False

    def try_parse_function_or_method_call(self):
        # wywołanie_metody | wywołanie_funkcji
        if self.try_parse_identifier():
            if not (self.try_parse_function_call() or self.try_parse_method_call()):
                raise Exception("Musi byc wywolana funkcja lub metoda")
            return True
        return False

    def try_parse_function_call(self):
        # lewy_nawias, [lista_argumentów], prawy_nawias, średnik
        if self.try_parse_left_parenthesis():
            self.try_parse_list_of_arguments()
            if not self.try_parse_right_parenthesis():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                raise Exception("Brak praweog nawiasu")
            return True
        return False

    def try_parse_method_call(self):
        # kropka, identyfikator, lewy_nawias, [lista_argumentów], prawy_nawias, średnik
        if self.try_parse_dot():
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Brak identyfikatora")
            if not self.try_parse_left_parenthesis():
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
                raise Exception("Brak lewego nawiasu")
            self.try_parse_list_of_arguments()
            if not self.try_parse_right_parenthesis():
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                raise Exception("Brak prawego nawiasu")
            return True
        return False

    def try_parse_conditional_instruction(self):
        # słowo_kluczowe_when, warunek, blok,
        # {słowo_kluczowe_else, słowo_kluczowe_when, blok},
        # [słowo_kluczowe_else, warunek, blok]
        if not self.try_parse_when():
            return False
        if not self.try_parse_condition():
            raise Exception("Brak warunku")
        self.try_parse_block()
        while self.try_parse_else():
            if self.try_parse_when():
                if not self.try_parse_condition():
                    raise Exception("Brak warunku")
                self.try_parse_block()
            else:
                self.try_parse_block()
                break
        return True
        
    def try_parse_loop(self):
        # słowo_kluczowe_loop, lewy_nawias, ((this albo ident)przypisanie, średnik, warunek,
        #                                    średnik, krok | identyfikator, dwukropek, identyfikator),
        # prawy_nawias, blok
        if not self.try_parse_loop_keyword():
            return False
        if not self.try_parse_left_parenthesis():
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
            raise Exception("Brak lewego nawiasu")
        if self.try_parse_assignment_with_this():
            if not self.try_parse_semicolon():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if not self.try_parse_condition():
                raise Exception("Brak warunku")
            if not self.try_parse_semicolon():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if not self.try_parse_step():
                raise Exception("Brak kroku")
        else:
            if not self.try_parse_identifier():
                return False
            if not (self.try_parse_collection_loop() or self.try_parse_conditional_loop()):
                raise Exception("Zla petla")
        if not self.try_parse_right_parenthesis():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        self.try_parse_block()
        return True

    def try_parse_conditional_loop(self):
        if not self.try_parse_assignment():
            return False
        if not self.try_parse_semicolon():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        if not self.try_parse_condition():
            raise Exception("Brak warunku")
        if not self.try_parse_semicolon():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        if not self.try_parse_step():
            raise Exception("Brak kroku")
        return True

    def try_parse_step(self):
        # identyfikator, operator_przypisania, (wyrażenie_arytmetyczne |
        #                                       wywołanie_funkcji_metody)
        if not self.try_parse_identifier():
            return False
        if not self.try_parse_assignment_operator():
            raise Exception("Brak operatora przypisania")
        if not (self.try_parse_arithmetic_expression() or self.try_parse_function_or_method_call()):
            raise Exception("Brak wyrazenia lub wywolania")
        return True

    def try_parse_in_out(self):
        # obsługa_wejścia | obsługa_wyjścia
        return self.try_parse_in() or self.try_parse_out()

    def try_parse_out(self):
        # słowo_kluczowe_out, operator_wczytywania, (wyrażenie_arytmetyczne |
        #                                           stała_znakowa), średnik
        if not self.try_parse_out_keyword():
            return False
        if not self.try_parse_output():
            raise Exception("Brak slowa out")
        if self.try_parse_arithmetic_expression() or self.try_parse_character_constant():
            if not self.try_parse_semicolon():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        else:
            raise Exception("Powinno byc wyrazenie lub stala")
        return True

    def try_parse_arithmetic_expression(self):
        # składowa, {operator_dodawania, składowa};
        if self.try_parse_component():
            while self.try_parse_addition():
                if not self.try_parse_component():
                    raise Exception("Powinna byc skladowa")
            return True
        return False

    def try_parse_component(self):
        # element, {operator_mnożenia, element}
        if self.try_parse_element():
            while self.try_parse_multiplication():
                if not self.try_parse_element():
                    raise Exception("Brak elementu")
            return True
        return False

    def try_parse_element(self):
        # int | identyfikator | wywołanie_funkcji_metody | odwołanie_do_atrybutu |
        # lewy_nawias, wyrażenie_arytmetyczne, prawy_nawias | operator_odejmowania, wyrażenie_arytmetyczne
        if self.try_parse_left_parenthesis():
            if not self.try_parse_arithmetic_expression():
                return False
            if not self.try_parse_right_parenthesis():
                return False
            return True
        if self.try_parse_difference():
            if not self.try_parse_arithmetic_expression():
                return False
            return True
        if self.try_parse_integer():
            return True
        if self.try_parse_identifier():
            if self.try_parse_function_call() or self.try_parse_method_call_or_attribute_ref():
                pass
            return True
        if self.try_parse_this_keyword():
            if not self.try_parse_attribute_reference():
                raise Exception("Powinno byc odwolanie do atrybutu")
        return False

    def try_parse_attribute_reference(self):
        if self.try_parse_dot():
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Brak identyfikatora")
            return True
        return False

    def try_parse_method_call_or_attribute_ref(self):
        # kropka, identyfikator - referencja
        # identyfikator, kropka, identyfikator, lewy_nawias, [ lista_argumentów ], prawy_nawias - wywołanie
        if self.try_parse_dot():
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Brak identyfikatora")
            if self.try_parse_left_parenthesis():
                self.try_parse_list_of_arguments()
                if not self.try_parse_right_parenthesis():
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                    raise Exception("Brak prawego nawiasu")
            return True
        return False

    def try_parse_in(self):
        # słowo_kluczowe_in, operator_wczytywania, identyfikator, średnik
        if not self.try_parse_in_keyword():
            return False
        if not self.try_parse_input():
            raise Exception("Brak >>")
        if not self.try_parse_identifier():
            raise Exception("Brak identyfikatora")
        if not self.try_parse_semicolon():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        return True

    def try_parse_collection_loop(self):
        # dwukropek, identyfikator
        if not self.try_parse_colon():
            return False
        if not self.try_parse_identifier():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
            raise Exception("Brak identyfikatora")
        return True

    def try_parse_condition(self):
        # składowa_warunku, {operator_logiczny, składowa_warunku}
        if not self.try_parse_condition_component():
            raise Exception("Brak składowej")
        while self.try_parse_logical_operators():
            if not self.try_parse_condition_component():
                return False
        return True

    def try_parse_condition_component(self):
        # czynnik, {operator_relacyjny, czynnik}
        if not self.try_parse_factor():
            raise Exception("Brak czynnika")
        while self.try_parse_relational_operators():
            if not self.try_parse_factor():
                return False
        return True

    def try_parse_factor(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias) |
        # wyrażenie_arytmetyczne
        if not (self.try_parse_parenthesis_expression() or self.try_parse_arithmetic_expression()):
            raise Exception("Brak wyrazenia lub nawiasow")
        return True

    def try_parse_parenthesis_expression(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias)
        negation = False
        if self.try_parse_logical_negation_operator():
           negation = True
        if not self.try_parse_left_parenthesis():
            return False
        if not self.try_parse_condition():
            raise Exception("Brak warunku")
        if not self.try_parse_right_parenthesis():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        return True

    def try_parse_operator(self):
        if self.current_token.token_type not in tokens.t_operator:
            raise Exception("Brak operatora")
        self.consume_token()
        return True

    def try_parse_identifier(self):
        if self.current_token.token_type != tokens.TokenType.t_identifier:
            return False
        self.consume_token()
        return True

    def try_parse_logical_negation_operator(self):
        if self.current_token.token_type == tokens.TokenType.t_negation:
            self.consume_token()
            return True
        return False

    def try_parse_logical_operators(self):
        if self.current_token.token_type in tokens.t_logical_operators:
            self.consume_token()
            return True
        return False

    def try_parse_relational_operators(self):
        if self.current_token.token_type in tokens.t_relational_operators:
            self.consume_token()
            return True
        return False

    def try_parse_none_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'None':
            self.consume_token()
            return True
        return False

    def try_parse_index(self):
        if self.current_token.token_type == tokens.TokenType.t_index:
            self.consume_token()
            return True
        return False

    def try_parse_assignment_operator(self):
        if self.current_token.token_type == tokens.TokenType.t_assignment:
            self.consume_token()
            return True
        return False

    def try_parse_this_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'this':
            self.consume_token()
            return True
        return False

    def try_parse_colon(self):
        if self.current_token.token_type == tokens.TokenType.t_colon:
            self.consume_token()
            return True
        return False

    def try_parse_left_parenthesis(self):
        if self.current_token.token_type == tokens.TokenType.t_left_parenthesis:
            self.consume_token()
            return True
        return False

    def try_parse_right_parenthesis(self):
        if self.current_token.token_type == tokens.TokenType.t_right_parenthesis:
            self.consume_token()
            return True
        return False

    def try_parse_right_brace(self):
        if self.current_token.token_type == tokens.TokenType.t_right_brace:
            self.consume_token()
            return True
        return False

    def try_parse_when(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'when':
            self.consume_token()
            return True
        return False

    def try_parse_input(self):
        if self.current_token.token_type == tokens.TokenType.t_input:
            self.consume_token()
            return True
        return False

    def try_parse_semicolon(self):
        if self.current_token.token_type == tokens.TokenType.t_semicolon:
            self.consume_token()
            return True
        return False

    def try_parse_left_brace(self):
        if self.current_token.token_type == tokens.TokenType.t_left_brace:
            self.consume_token()
            return True
        return False

    def try_parse_dot(self):
        if self.current_token.token_type == tokens.TokenType.t_dot:
            self.consume_token()
            return True
        return False

    def try_parse_character_constant(self):
        if self.current_token.token_type == tokens.TokenType.t_character_constant:
            self.consume_token()
            return True
        return False

    def try_parse_output(self):
        if self.current_token.token_type == tokens.TokenType.t_output:
            self.consume_token()
            return True
        return False

    def try_parse_addition(self):
        if self.current_token.token_type == tokens.TokenType.t_addition:
            self.consume_token()
            return True
        return False

    def try_parse_multiplication(self):
        if self.current_token.token_type in tokens.t_multiplication_operators:
            self.consume_token()
            return True
        return False

    def try_parse_difference(self):
        if self.current_token.token_type == tokens.TokenType.t_difference:
            self.consume_token()
            return True
        return False

    def try_parse_integer(self):
        if self.current_token.token_type == tokens.TokenType.t_integer:
            self.consume_token()
            return True
        return False

    def try_parse_out_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'out':
            self.consume_token()
            return True
        return False

    def try_parse_else(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'else':
            self.consume_token()
            return True
        return False

    def try_parse_comma(self):
        if self.current_token.token_type == tokens.TokenType.t_comma:
            self.consume_token()
            return True
        return False

    def try_parse_in_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'in':
            self.consume_token()
            return True
        return False

    def try_parse_extends_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'extends':
            self.consume_token()
            return True
        return False

    def try_parse_operator_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'operator':
            self.consume_token()
            return True
        return False

    def try_parse_get_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'get':
            self.consume_token()
            return True
        return False

    def try_parse_set_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'set':
            self.consume_token()
            return True
        return False

    def try_parse_loop_keyword(self):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'loop':
            self.consume_token()
            return True
        return False










