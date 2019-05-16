from copy import copy

import env
import error_messages
import tokens


class Parser:

    def __init__(self, lex, environment):
        self.lexer = lex
        self.environment = environment
        self.current_token = self.lexer.get_token()
        self.previous_token = None
        self.class_stack = []
        self.error_message_buffer = []
        self.error_handler = error_messages.Error(self.lexer.source)

    def consume_token(self):
        self.previous_token = copy(self.current_token)
        self.current_token = self.lexer.get_token()

    def parse(self):
        while self.try_parse_identifier():
            try:
                identifier = self.class_stack.pop()
                if not(self.try_parse_function(identifier) or self.try_parse_object(identifier)):
                    raise Exception("Powinna być funkcja albo obiekt")
            except Exception as e:
                print(e.args)
                break
        if len(self.error_message_buffer) == 0:
            return True
        else:
            for message in self.error_message_buffer:
                print(message)
            return False

    def try_parse_function(self, identifier):
        # lewy_nawias, [lista_argumentów], prawy_nawias
        # [słowo_kluczowe_extends, identyfikator], blok
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            return False
        list_of_args = self.parse_list_of_arguments()
        if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        extending_object = self.parse_extends()
        block = self.parse_block()
        function = env.Function(list_of_args, block, extending_object)
        self.environment.functions[identifier.name] = function
        return True

    def parse_block(self):
        # lewy_nawias_klamrowy, {instrukcja}, prawy_nawias_klamrowy
        if not self.try_parse_token(tokens.TokenType.t_left_brace):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_brace_message))
            raise Exception("Brak lewego nawiasu")
        instructions = self.try_parse_instructions()
        if not self.try_parse_token(tokens.TokenType.t_right_brace):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_brace_message))
            raise Exception("Brak prawego nawiasu")
        return env.Block(instructions)

    def try_parse_object(self, identifier):
        # [słowo_kluczowe_extends, identyfikator], lewy_nawias_klamrowy,
        # {atrybut | metoda | przeciążanie_operatora}, prawy_nawias_klamrowy
        base_object = self.parse_extends()
        if not self.try_parse_token(tokens.TokenType.t_left_brace):
            return False
        while not self.try_parse_token(tokens.TokenType.t_right_brace):
            if not(self.try_parse_method_or_attribute() or self.try_parse_operator_overloading()):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Musi byc atrybut, metoda lub przeciazenie")
        self.environment.objects[identifier.name] = env.Object(base_object)
        return True

    def parse_list_of_arguments(self):
        # { argument_z_przecinkiem }, argument
        list_of_args = []
        if self.try_parse_argument():
            list_of_args.append(self.class_stack.pop())
            while self.try_parse_token(tokens.TokenType.t_comma):
                if self.try_parse_argument():
                    list_of_args.append(self.class_stack.pop())
                else:    
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, "invalid syntax"))
                    raise Exception("Blednie podana lista argumentow")
                
        return list_of_args

    def try_parse_argument(self):
        # identyfikator, [ słowo_kluczowe_in ], [ słowo_kluczowe_out ]
        if not self.try_parse_identifier():
            return False
        identifier = self.class_stack.pop()
        has_in = False
        if self.try_parse_keyword('in'):
            has_in = True
        has_out = False    
        if self.try_parse_keyword('out'):
            has_out = True
        self.class_stack.append(env.Argument(identifier, has_in, has_out))
        return True

    def parse_extends(self):
        if self.try_parse_keyword('extends'):
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Powinien byc ident po extends")
            return self.class_stack.pop()
        return None

    def try_parse_instructions(self):
        # przypisanie | wywołanie_funkcji_metody | instrukcja_warunkowa | pętla |
        # obsługa_wejścia_wyjścia
        instructions = []
        if self.try_parse_assignment_or_method_function_call() or self.try_parse_conditional_instruction() or self.try_parse_loop() or self.try_parse_in_out():
            instructions.append(self.class_stack.pop())
            while self.try_parse_assignment_or_method_function_call() or self.try_parse_conditional_instruction() or self.try_parse_loop() or self.try_parse_in_out():
                instructions.append(self.class_stack.pop())
        return instructions

    def try_parse_method_or_attribute(self):
        if self.try_parse_identifier():
            if not (self.try_parse_method() or self.try_parse_attribute()):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Musi byc metoda lub atrybut")
            return True
        else:
            return False

    def try_parse_assignment_or_method_function_call(self):
        if self.try_parse_assignment_with_this():
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            return True
        if self.try_parse_identifier():
            if not (self.try_parse_function_or_method_call() or self.try_parse_assignment()):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Musi byc wywolanie lub przypisanie")
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            return True
        return False

    def try_parse_method(self):
        # lewy_nawias, [lista_argumentów], prawy_nawias, [dwukropek,
        #                                                 identyfikator, lewy_nawias, [lista_argumentów],
        #                                                 prawy_nawias], blok
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            return False
        self.parse_list_of_arguments()
        if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        if self.try_parse_token(tokens.TokenType.t_colon):
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Powinien byc identyfikator")
            if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
                raise Exception("Brak lewego nawiasu")
            self.parse_list_of_arguments()
            if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                raise Exception("Brak prawego nawiasu")
        self.parse_block()
        return True

    def try_parse_operator_overloading(self):
        # słowo_kluczowe_operator, operator, lewy_nawias,
        # [lista_argumentów], prawy_nawias, blok
        if not self.try_parse_keyword('operator'):
            return False
        self.try_parse_operator()
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
            raise Exception("Brak lewego nawiasu")
        self.parse_list_of_arguments()
        if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        self.parse_block()
        return True

    def try_parse_attribute(self):
        #  [lewy_nawias_klamrowy, [słowo_kluczowe_get, średnik],
        #                 [słowo_kluczowe_set, średnik], prawy_nawias_klamrowy],
        #                 operator_przypisania,
        # (stała_znakowa | słowo_kluczowe_none | operator_indeksu |
        #  wyrażenie_arytmetyczne), średnik;
        if self.try_parse_token(tokens.TokenType.t_left_brace):
            if self.try_parse_keyword('get'):
                if not self.try_parse_token(tokens.TokenType.t_semicolon):
                    self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if self.try_parse_keyword('set'):
                if not self.try_parse_token(tokens.TokenType.t_semicolon):
                    self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if not self.try_parse_token(tokens.TokenType.t_right_brace):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.right_brace_message))
                raise Exception("Brak prawego nawiasu")
            if not self.try_parse_token(tokens.TokenType.t_assignment):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Powinno byc przypisanie")
        elif not self.try_parse_token(tokens.TokenType.t_assignment):
            return False
        if not (self.try_parse_character_constant() or self.try_parse_keyword('None') or self.try_parse_token(tokens.TokenType.t_index) or self.try_parse_arithmetic_expression()):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak (stała_znakowa | słowo_kluczowe_none | operator_indeksu |  wyrażenie_arytmetyczne)")
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        return True

    def try_parse_assignment(self):
        # operator_przypisania, wyrażenie_arytmetyczne, średnik
        if self.try_parse_token(tokens.TokenType.t_assignment):
            if not self.try_parse_arithmetic_expression():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Brak wyrazenia arytmetycznego")
            return True
        return False

    def try_parse_assignment_with_this(self):
        # [słowo_kluczowe_this, kropka], identyfikator, operator_przypisania,
        # wyrażenie_arytmetyczne
        if self.try_parse_keyword('this'):
            if not self.try_parse_token(tokens.TokenType.t_dot):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.dot_message))
                raise Exception("Musi byc kropka")
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Musi byc ident")
            if not self.try_parse_token(tokens.TokenType.t_assignment):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.assignment_operator_message))
            if not self.try_parse_arithmetic_expression():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Brak wyr arytm")
            return True
        return False

    def try_parse_function_or_method_call(self):
        # wywołanie_metody | wywołanie_funkcji
        return self.try_parse_function_call() or self.try_parse_method_call()

    def try_parse_function_call(self):
        # lewy_nawias, [lista_argumentów], prawy_nawias, średnik
        if self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            self.parse_list_of_arguments()
            if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                raise Exception("Brak praweog nawiasu")
            return True
        return False

    def try_parse_method_call(self):
        # kropka, identyfikator, lewy_nawias, [lista_argumentów], prawy_nawias, średnik
        if self.try_parse_token(tokens.TokenType.t_dot):
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Brak identyfikatora")
            if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
                raise Exception("Brak lewego nawiasu")
            self.parse_list_of_arguments()
            if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                raise Exception("Brak prawego nawiasu")
            return True
        return False

    def try_parse_conditional_instruction(self):
        # słowo_kluczowe_when, warunek, blok,
        # {słowo_kluczowe_else, słowo_kluczowe_when, blok},
        # [słowo_kluczowe_else, warunek, blok]
        if not self.try_parse_keyword('when'):
            return False
        if not self.try_parse_condition():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak warunku")
        self.parse_block()
        while self.try_parse_keyword('else'):
            if self.try_parse_keyword('when'):
                if not self.try_parse_condition():
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                    raise Exception("Brak warunku")
                self.parse_block()
            else:
                self.parse_block()
                break
        return True
        
    def try_parse_loop(self):
        # słowo_kluczowe_loop, lewy_nawias, ((this albo ident)przypisanie, średnik, warunek,
        #                                    średnik, krok | identyfikator, dwukropek, identyfikator),
        # prawy_nawias, blok
        if not self.try_parse_keyword('loop'):
            return False
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_messages.left_parenthesis_message))
            raise Exception("Brak lewego nawiasu")
        if self.try_parse_assignment_with_this():
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if not self.try_parse_condition():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Brak warunku")
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            if not self.try_parse_step():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Brak kroku")
        else:
            if not self.try_parse_identifier():
                return False
            if not (self.try_parse_collection_loop() or self.try_parse_conditional_loop()):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Zla petla")
        if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        self.parse_block()
        return True

    def try_parse_conditional_loop(self):
        if not self.try_parse_assignment():
            return False
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        if not self.try_parse_condition():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak warunku")
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        if not self.try_parse_step():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak kroku")
        return True

    def try_parse_step(self):
        # (identyfikator, operator_przypisania, wyrażenie_arytmetyczne) |
        #                                       wywołanie_funkcji_metody
        if not self.try_parse_identifier():
            return False
        if self.try_parse_token(tokens.TokenType.t_assignment):
            if not self.try_parse_arithmetic_expression():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Brak wyrazenia")
        elif self.try_parse_function_or_method_call():
            pass
        else:
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak wyrazenia lub wywolania")
        return True

    def try_parse_in_out(self):
        # obsługa_wejścia | obsługa_wyjścia
        return self.try_parse_in() or self.try_parse_out()

    def try_parse_out(self):
        # słowo_kluczowe_out, operator_wczytywania, (wyrażenie_arytmetyczne |
        #                                           stała_znakowa), średnik
        if not self.try_parse_keyword('out'):
            return False
        if not self.try_parse_token(tokens.TokenType.t_output):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak << ")
        output_value = None
        if self.try_parse_arithmetic_expression() or self.try_parse_character_constant():
            output_value = self.class_stack.pop()
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        else:
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Powinno byc wyrazenie lub stala")

        self.class_stack.append(env.Output(output_value))
        return True

    def try_parse_arithmetic_expression(self):
        # składowa, {operator_dodawania, składowa};
        if self.try_parse_component():
            while self.try_parse_token(tokens.TokenType.t_addition):
                if not self.try_parse_component():
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                    raise Exception("Powinna byc skladowa")
            return True
        return False

    def try_parse_component(self):
        # element, {operator_mnożenia, element}
        if self.try_parse_element():
            while self.try_parse_multiplication():
                if not self.try_parse_element():
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                    raise Exception("Brak elementu")
            return True
        return False

    def try_parse_element(self):
        # int | identyfikator | wywołanie_funkcji_metody | odwołanie_do_atrybutu |
        # lewy_nawias, wyrażenie_arytmetyczne, prawy_nawias | operator_odejmowania, wyrażenie_arytmetyczne
        if self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            if not self.try_parse_arithmetic_expression():
                return False
            if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
                return False
            return True
        if self.try_parse_token(tokens.TokenType.t_difference):
            if not self.try_parse_arithmetic_expression():
                return False
            return True
        if self.try_parse_integer():
            return True
        if self.try_parse_identifier():
            if self.try_parse_function_call() or self.try_parse_method_call_or_attribute_ref():
                pass
            return True
        if self.try_parse_keyword('this'):
            if not self.try_parse_attribute_reference():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Powinno byc odwolanie do atrybutu")
        return False

    def try_parse_attribute_reference(self):
        if self.try_parse_token(tokens.TokenType.t_dot):
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Brak identyfikatora")
            return True
        return False

    def try_parse_method_call_or_attribute_ref(self):
        # kropka, identyfikator - referencja
        # kropka, identyfikator, lewy_nawias, [ lista_argumentów ], prawy_nawias - wywołanie
        if self.try_parse_token(tokens.TokenType.t_dot):
            if not self.try_parse_identifier():
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
                raise Exception("Brak identyfikatora")
            if self.try_parse_token(tokens.TokenType.t_left_parenthesis):
                self.parse_list_of_arguments()
                if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
                    raise Exception("Brak prawego nawiasu")
            return True
        return False

    def try_parse_in(self):
        # słowo_kluczowe_in, operator_wczytywania, identyfikator, średnik
        if not self.try_parse_keyword('in'):
            return False
        if not self.try_parse_token(tokens.TokenType.t_input):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak >>")
        if not self.try_parse_identifier():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak identyfikatora")
        identifier = self.class_stack.pop()
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        self.class_stack.append(env.Input(identifier))
        return True

    def try_parse_collection_loop(self):
        # dwukropek, identyfikator
        if not self.try_parse_token(tokens.TokenType.t_colon):
            return False
        if not self.try_parse_identifier():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.identifier_message))
            raise Exception("Brak identyfikatora")
        return True

    def try_parse_condition(self):
        # składowa_warunku, {operator_logiczny, składowa_warunku}
        if not self.try_parse_condition_component():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak składowej")
        while self.try_parse_token_from_group(tokens.t_logical_operators):    
            if not self.try_parse_condition_component():
                return False
        return True

    def try_parse_condition_component(self):
        # czynnik, {operator_relacyjny, czynnik}
        if not self.try_parse_factor():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak czynnika")
        while self.try_parse_token_from_group(tokens.t_relational_operators):
            if not self.try_parse_factor():
                return False
        return True

    def try_parse_factor(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias) |
        # wyrażenie_arytmetyczne
        if not (self.try_parse_parenthesis_expression() or self.try_parse_arithmetic_expression()):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak wyrazenia lub nawiasow")
        return True

    def try_parse_parenthesis_expression(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias)
        negation = False
        if self.try_parse_token(tokens.TokenType.t_negation):
           negation = True
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            return False
        if not self.try_parse_condition():
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak warunku")
        if not self.try_parse_token(tokens.TokenType.t_right_parenthesis):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.right_parenthesis_message))
            raise Exception("Brak prawego nawiasu")
        return True

    def try_parse_operator(self):
        if self.current_token.token_type not in tokens.t_operator:
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak operatora")
        self.consume_token()
        return True

    def try_parse_identifier(self):
        if self.current_token.token_type == tokens.TokenType.t_identifier:
            self.class_stack.append(env.Identifier(self.current_token.value))
            self.consume_token()
            return True
        return False

    def try_parse_token(self, token_type):
        if self.current_token.token_type == token_type:
            self.consume_token()
            return True
        return False

    def try_parse_token_from_group(self, group_of_tokens):
        if self.current_token.token_type in group_of_tokens:
            self.consume_token()
            return True
        return False

    def try_parse_keyword(self, key_name):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == key_name:
            self.consume_token()
            return True
        return False

    def try_parse_character_constant(self):
        if self.current_token.token_type == tokens.TokenType.t_character_constant:
            self.class_stack.append(env.CharacterConstant(self.current_token.value))
            self.consume_token()
            return True
        return False

    def try_parse_multiplication(self):
        if self.current_token.token_type in tokens.t_multiplication_operators:
            self.consume_token()
            return True
        return False

    def try_parse_integer(self):
        if self.current_token.token_type == tokens.TokenType.t_integer:
            self.class_stack.append(env.Integer(self.current_token.value))
            self.consume_token()
            return True
        return False










