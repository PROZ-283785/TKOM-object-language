from copy import copy

import env
import error_messages
import tokens


class Parser:

    def __init__(self, lex, environment):
        self.lexer = lex
        self.environment = environment
        self.current_token = None
        self.previous_token = None
        self.class_stack = []
        self.error_message_buffer = []
        self.error_handler = error_messages.Error(self.lexer.source)

    def consume_token(self):
        self.previous_token = copy(self.current_token)
        self.current_token = self.lexer.get_token()

    def parse(self):
        self.consume_token()
        while self.try_parse_identifier():
            # try:
            identifier = self.class_stack.pop()
            if not (self.try_parse_function(identifier) or self.try_parse_object(identifier)):
                raise Exception("Powinna być funkcja albo obiekt")
            # except Exception as e:
            #     print(e.args)
            #     break
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
        self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                     error_message=error_messages.right_parenthesis_message)
        extending_object = self.parse_extends()
        block = self.parse_block()
        function = env.Function(list_of_args, block, extending_object)
        self.environment.functions[(identifier.name, len(list_of_args))] = function
        return True

    def parse_block(self):
        # lewy_nawias_klamrowy, {instrukcja}, prawy_nawias_klamrowy
        self.execute(self.try_parse_token, tokens.TokenType.t_left_brace,
                     error_message=error_messages.left_brace_message)
        instructions = self.parse_instructions()
        self.execute(self.try_parse_token, tokens.TokenType.t_right_brace,
                     error_message=error_messages.right_brace_message)
        return env.Block(instructions)

    def try_parse_object(self, identifier):
        # [słowo_kluczowe_extends, identyfikator], lewy_nawias_klamrowy,
        # {atrybut | metoda | przeciążanie_operatora}, prawy_nawias_klamrowy
        base_object = self.parse_extends()
        methods = {}
        attributes = {}
        overridden_operators = {}
        if not self.try_parse_token(tokens.TokenType.t_left_brace):
            return False
        while not self.try_parse_token(tokens.TokenType.t_right_brace):
            if not (self.try_parse_method_or_attribute() or self.try_parse_operator_overloading()):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Musi byc atrybut, metoda lub przeciazenie")
            else:
                element = self.class_stack.pop()
                element_type = env.find_type(element)
                if element_type == 'Method':
                    methods[(element.identifier.name, len(element.list_of_arguments))] = element
                elif element_type == 'Attribute':
                    attributes[element.identifier.name] = element
                elif element_type == 'OverriddenOperator':
                    overridden_operators[element.operator] = element
        self.environment.objects[identifier.name] = env.Object(attributes, methods, overridden_operators, base_object)
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
        if not has_out:
            has_in = True
        self.class_stack.append(env.Argument(identifier, has_in, has_out))
        return True

    def parse_extends(self):
        if self.try_parse_keyword('extends'):
            self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
            return self.class_stack.pop()
        return None

    def parse_instructions(self):
        # przypisanie | wywołanie_funkcji_metody | instrukcja_warunkowa | pętla |
        # obsługa_wejścia_wyjścia
        instructions = []
        if self.try_parse_assignment_or_method_function_call() or self.try_parse_conditional_instruction() or \
                self.try_parse_loop() or self.try_parse_in_out():
            instructions.append(self.class_stack.pop())
            while self.try_parse_assignment_or_method_function_call() or self.try_parse_conditional_instruction() or \
                    self.try_parse_loop() or self.try_parse_in_out():
                instructions.append(self.class_stack.pop())
        return instructions

    def try_parse_method_or_attribute(self):
        if self.try_parse_identifier():
            identifier = self.class_stack.pop()
            if not (self.try_parse_method(identifier) or self.try_parse_attribute(identifier)):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Musi byc metoda lub atrybut")
            return True
        else:
            return False

    def try_parse_assignment_or_method_function_call(self):
        if self.try_parse_assignment_with_this():
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            return True
        if self.try_parse_identifier():
            identifier = self.class_stack.pop()
            if not (self.try_parse_function_or_method_call(identifier) or self.try_parse_assignment(identifier)):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Musi byc wywolanie lub przypisanie")
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            return True
        return False

    def try_parse_method(self, identifier):
        # lewy_nawias, [lista_argumentów], prawy_nawias, [dwukropek,
        #                                                 identyfikator, lewy_nawias, [lista_argumentów],
        #                                                 prawy_nawias], blok
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            return False
        list_of_args = self.parse_list_of_arguments()
        self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                     error_message=error_messages.right_parenthesis_message)
        base_obj = None
        list_of_base_obj_args = []
        if self.try_parse_token(tokens.TokenType.t_colon):
            self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
            base_obj = self.class_stack.pop()
            self.execute(self.try_parse_token, tokens.TokenType.t_left_parenthesis)
            list_of_base_obj_args = self.parse_list_of_arguments()
            self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                         error_message=error_messages.right_parenthesis_message)
        block = self.parse_block()
        self.class_stack.append(env.Method(identifier, list_of_args, base_obj, list_of_base_obj_args, block))
        return True

    def try_parse_operator_overloading(self):
        # słowo_kluczowe_operator, operator, lewy_nawias,
        # [lista_argumentów], prawy_nawias, blok
        if not self.try_parse_keyword('operator'):
            return False
        operator = self.parse_operator()
        self.execute(self.try_parse_token, tokens.TokenType.t_left_parenthesis,
                     error_message=error_messages.left_parenthesis_message)
        list_of_args = self.parse_list_of_arguments()
        self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                     error_message=error_messages.right_parenthesis_message)
        block = self.parse_block()
        self.class_stack.append(env.OverriddenOperator(operator, list_of_args, block))
        return True

    def try_parse_attribute(self, identifier):
        #  [lewy_nawias_klamrowy, [słowo_kluczowe_get, średnik],
        #                 [słowo_kluczowe_set, średnik], prawy_nawias_klamrowy],
        #                 operator_przypisania,
        # (stała_znakowa | słowo_kluczowe_none | operator_indeksu |
        #  wyrażenie_arytmetyczne), średnik;
        has_getter = False
        has_setter = False
        if self.try_parse_token(tokens.TokenType.t_left_brace):
            if self.try_parse_keyword('get'):
                if not self.try_parse_token(tokens.TokenType.t_semicolon):
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
                has_getter = True
            if self.try_parse_keyword('set'):
                if not self.try_parse_token(tokens.TokenType.t_semicolon):
                    self.error_message_buffer.append(
                        self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
                has_setter = True
            self.execute(self.try_parse_token, tokens.TokenType.t_right_brace,
                         error_message=error_messages.right_brace_message)
            self.execute(self.try_parse_token, tokens.TokenType.t_assignment,
                         error_message=error_messages.invalid_syntax_message)
        elif not self.try_parse_token(tokens.TokenType.t_assignment):
            return False
        # or self.try_parse_token(
        #                 tokens.TokenType.t_index)
        if not (self.try_parse_character_constant() or self.try_parse_keyword(
                'None') or self.try_parse_arithmetic_expression()):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak (stała_znakowa | słowo_kluczowe_none | operator_indeksu |  wyrażenie_arytmetyczne)")
        value = self.class_stack.pop()
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        self.class_stack.append(env.Attribute(identifier, has_getter, has_setter, value))
        return True

    def try_parse_assignment(self, identifier):
        # operator_przypisania, wyrażenie_arytmetyczne, średnik
        if self.try_parse_token(tokens.TokenType.t_assignment):
            if not(self.try_parse_arithmetic_expression() or self.try_parse_keyword('None') or self.try_parse_character_constant()):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Missing expression or None value or character constant")
            value = self.class_stack.pop()
            self.class_stack.append(env.Assignment(False, identifier, value))
            return True
        return False

    def try_parse_assignment_with_this(self):
        # [słowo_kluczowe_this, kropka], identyfikator, operator_przypisania,
        # wyrażenie_arytmetyczne
        if self.try_parse_keyword('this'):
            self.execute(self.try_parse_token, tokens.TokenType.t_dot, error_message=error_messages.dot_message)
            self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
            identifier = self.class_stack.pop()
            self.execute(self.try_parse_token, tokens.TokenType.t_assignment,
                         error_message=error_messages.assignment_operator_message)
            self.execute(self.try_parse_arithmetic_expression, error_message=error_messages.invalid_syntax_message)
            arithmetic_expr = self.class_stack.pop()
            self.class_stack.append(env.Assignment(True, identifier, arithmetic_expr))
            return True
        return False

    def try_parse_function_or_method_call(self, identifier):
        # wywołanie_metody | wywołanie_funkcji
        return self.try_parse_function_call(identifier) or self.try_parse_method_call(identifier)

    def try_parse_function_call(self, identifier):
        # lewy_nawias, [lista_argumentów], prawy_nawias, średnik
        if self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            list_of_args = self.parse_list_of_arguments()
            self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                         error_message=error_messages.right_parenthesis_message)
            self.class_stack.append(env.FunctionCall(identifier, list_of_args))
            return True
        return False

    def try_parse_method_call(self, l_identifier):
        # kropka, identyfikator, lewy_nawias, [lista_argumentów], prawy_nawias, średnik
        if self.try_parse_token(tokens.TokenType.t_dot):
            self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
            r_identifier = self.class_stack.pop()
            self.execute(self.try_parse_token, tokens.TokenType.t_left_parenthesis,
                         error_message=error_messages.left_parenthesis_message)
            list_of_args = self.parse_list_of_arguments()
            self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                         error_message=error_messages.right_parenthesis_message)
            self.class_stack.append(env.MethodCall(l_identifier, r_identifier, list_of_args))
            return True
        return False

    def try_parse_conditional_instruction(self):
        # słowo_kluczowe_when, warunek, blok,
        # {słowo_kluczowe_else, słowo_kluczowe_when, blok},
        # [słowo_kluczowe_else, warunek, blok]
        if not self.try_parse_keyword('when'):
            return False
        self.execute(self.try_parse_condition, error_message=error_messages.invalid_syntax_message)
        condition_with_block = [(self.class_stack.pop(), self.parse_block())]
        block_without_cond = None
        while self.try_parse_keyword('else'):
            if self.try_parse_keyword('when'):
                self.execute(self.try_parse_condition, error_message=error_messages.invalid_syntax_message)
                condition_with_block.append((self.class_stack.pop(), self.parse_block()))
            else:
                block_without_cond = self.parse_block()
                break
        self.class_stack.append(env.ConditionalInstruction(condition_with_block, block_without_cond))
        return True

    def try_parse_loop(self):
        # słowo_kluczowe_loop, lewy_nawias, ((this albo ident)przypisanie, średnik, warunek,
        #                                    średnik, krok | identyfikator, dwukropek, identyfikator),
        # prawy_nawias, blok
        if not self.try_parse_keyword('loop'):
            return False
        self.execute(self.try_parse_token, tokens.TokenType.t_left_parenthesis,
                     error_message=error_messages.left_parenthesis_message)
        if self.try_parse_assignment_with_this():
            assignment_with_this = self.class_stack.pop()
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            self.execute(self.try_parse_condition, error_message=error_messages.invalid_syntax_message)
            condition = self.class_stack.pop()
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            self.execute(self.try_parse_step, error_message=error_messages.invalid_syntax_message)
            step = self.class_stack.pop()
            self.class_stack.append(env.ConditionLoop(assignment_with_this, condition, step))
        else:
            if not self.try_parse_identifier():
                return False
            identifier = self.class_stack.pop()
            if not (self.try_parse_collection_loop(identifier) or self.try_parse_conditional_loop(identifier)):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
                raise Exception("Zla petla")
        self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                     error_message=error_messages.right_parenthesis_message)
        loop = self.class_stack.pop()
        block = self.parse_block()
        self.class_stack.append(env.Loop(loop, block))
        return True

    def try_parse_conditional_loop(self, identifier):
        if not self.try_parse_assignment(identifier):
            return False
        assignment = self.class_stack.pop()
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        self.execute(self.try_parse_condition, error_message=error_messages.invalid_syntax_message)
        condition = self.class_stack.pop()
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        self.execute(self.try_parse_step, error_message=error_messages.invalid_syntax_message)
        step = self.class_stack.pop()
        self.class_stack.append(env.ConditionLoop(assignment, condition, step))
        return True

    def try_parse_step(self):
        # identyfikator, operator_przypisania, wyrażenie_arytmetyczne
        if not self.try_parse_identifier():
            return False
        identifier = self.class_stack.pop()
        if self.try_parse_token(tokens.TokenType.t_assignment):
            self.execute(self.try_parse_arithmetic_expression, error_message=error_messages.invalid_syntax_message)
            arithmetic_expr = self.class_stack.pop()
            self.class_stack.append(env.Step(identifier, arithmetic_expr))
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
        self.execute(self.try_parse_token, tokens.TokenType.t_output,
                     error_message=error_messages.invalid_syntax_message)
        if self.try_parse_arithmetic_expression() or self.try_parse_character_constant():
            output_value = self.class_stack.pop()
            if not self.try_parse_token(tokens.TokenType.t_semicolon):
                self.error_message_buffer.append(
                    self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
            self.class_stack.append(env.Output(output_value))
        else:
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Powinno byc wyrazenie lub stala")
        return True

    def try_parse_arithmetic_expression(self):
        # składowa, {operator_dodawania, składowa};
        if self.try_parse_component():
            l_component = self.class_stack.pop()
            r_components = []
            while self.try_parse_token_from_group(tokens.t_addition_operators):
                operator = self.class_stack.pop()
                self.execute(self.try_parse_component, error_message=error_messages.invalid_syntax_message)
                component = self.class_stack.pop()
                r_components.append((operator, component))
            self.class_stack.append(env.ArithmeticExpression(l_component, r_components))
            return True
        return False

    def try_parse_component(self):
        # element, {operator_mnożenia, element}
        if self.try_parse_element():
            l_element = self.class_stack.pop()
            r_elements_with_op = []
            while self.try_parse_multiplication():
                multiplication_op = self.class_stack.pop()
                self.execute(self.try_parse_element, error_message=error_messages.invalid_syntax_message)
                element = self.class_stack.pop()
                r_elements_with_op.append((multiplication_op, element))
            self.class_stack.append(env.Component(l_element, r_elements_with_op))
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
            self.class_stack.append(env.Element(self.class_stack.pop()))
            return True
        if self.try_parse_token(tokens.TokenType.t_difference):
            if not self.try_parse_element():
                return False
            self.class_stack.append(env.Element(self.class_stack.pop(), has_negation_op=True))
            return True
        if self.try_parse_integer():
            self.class_stack.append(env.Element(self.class_stack.pop()))
            return True
        if self.try_parse_identifier():
            identifier = self.class_stack.pop()
            if self.try_parse_function_call(identifier) or self.try_parse_method_call_or_attribute_ref(identifier):
                self.class_stack.append(env.Element(self.class_stack.pop()))
                return True
            self.class_stack.append(env.Element(identifier))
            return True
        if self.try_parse_keyword('this'):
            self.execute(self.try_parse_attribute_reference, None, True,
                         error_message=error_messages.invalid_syntax_message)
            self.class_stack.append(env.Element(self.class_stack.pop()))
        return False

    # can have identifier or this operator
    def try_parse_attribute_reference(self, l_identifier, has_this):
        if self.try_parse_token(tokens.TokenType.t_dot):
            self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
            r_identifier = self.class_stack.pop()
            self.class_stack.append(env.AttributeReference(l_identifier, r_identifier, has_this))
            return True
        return False

    def try_parse_method_call_or_attribute_ref(self, l_identifier):
        # kropka, identyfikator - referencja
        # kropka, identyfikator, lewy_nawias, [ lista_argumentów ], prawy_nawias - wywołanie
        if self.try_parse_token(tokens.TokenType.t_dot):
            self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
            r_identifier = self.class_stack.pop()
            if self.try_parse_token(tokens.TokenType.t_left_parenthesis):
                list_of_args = self.parse_list_of_arguments()
                self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                             error_message=error_messages.right_parenthesis_message)
                self.class_stack.append(env.MethodCall(l_identifier, r_identifier, list_of_args))
            else:
                self.class_stack.append(env.AttributeReference(l_identifier, r_identifier))
            return True
        return False

    def try_parse_in(self):
        # słowo_kluczowe_in, operator_wczytywania, identyfikator, średnik
        if not self.try_parse_keyword('in'):
            return False
        self.execute(self.try_parse_token, tokens.TokenType.t_input,
                     error_message=error_messages.invalid_syntax_message)
        self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
        identifier = self.class_stack.pop()
        if not self.try_parse_token(tokens.TokenType.t_semicolon):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.semicolon_message))
        self.class_stack.append(env.Input(identifier))
        return True

    def try_parse_collection_loop(self, l_identifier):
        # dwukropek, identyfikator
        if not self.try_parse_token(tokens.TokenType.t_colon):
            return False
        self.execute(self.try_parse_identifier, error_message=error_messages.identifier_message)
        r_identifier = self.class_stack.pop()
        self.class_stack.append(env.CollectionLoop(l_identifier, r_identifier))
        return True

    def try_parse_condition(self):
        # składowa_warunku, {operator_logiczny, składowa_warunku}
        self.execute(self.try_parse_condition_component, error_message=error_messages.invalid_syntax_message)
        l_cond = self.class_stack.pop()
        r_conds = []
        while self.try_parse_token_from_group(tokens.t_logical_operators):
            logical_op = self.class_stack.pop()
            if not self.try_parse_condition_component():
                return False
            r_cond = self.class_stack.pop()
            r_conds.append((logical_op, r_cond))
        self.class_stack.append(env.Condition(l_cond, r_conds))
        return True

    def try_parse_condition_component(self):
        # czynnik, {operator_relacyjny, czynnik}
        self.execute(self.try_parse_factor, error_message=error_messages.invalid_syntax_message)
        l_factor = self.class_stack.pop()
        r_factors = []
        while self.try_parse_token_from_group(tokens.t_relational_operators):
            rel_operator = self.class_stack.pop()
            if not self.try_parse_factor():
                return False
            r_factor = self.class_stack.pop()
            r_factors.append((rel_operator, r_factor))
        self.class_stack.append(env.ConditionComponent(l_factor, r_factors))
        return True

    def try_parse_factor(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias) |
        # wyrażenie_arytmetyczne
        if not (self.try_parse_parenthesis_condition() or self.try_parse_arithmetic_expression()):
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak wyrazenia lub nawiasow")
        self.class_stack.append(env.Factor(self.class_stack.pop()))
        return True

    def try_parse_parenthesis_condition(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias)
        has_negation = False
        if self.try_parse_token(tokens.TokenType.t_negation):
            has_negation = True
        if not self.try_parse_token(tokens.TokenType.t_left_parenthesis):
            return False
        self.execute(self.try_parse_condition, error_message=error_messages.invalid_syntax_message)
        condition = self.class_stack.pop()
        self.execute(self.try_parse_token, tokens.TokenType.t_right_parenthesis,
                     error_message=error_messages.right_parenthesis_message)
        self.class_stack.append(env.ParenthesisCondition(has_negation, condition))
        return True

    def parse_operator(self):
        if self.current_token.token_type not in tokens.t_operator:
            self.error_message_buffer.append(
                self.error_handler.get_error(self.previous_token, error_messages.invalid_syntax_message))
            raise Exception("Brak operatora")
        operator = self.current_token.value
        self.consume_token()
        return operator

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
            self.class_stack.append(self.current_token.value)
            self.consume_token()
            return True
        return False

    def try_parse_keyword(self, key_name):
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == key_name:
            if key_name == 'None':
                self.class_stack.append(env.NoneKeyVal())
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
            self.class_stack.append(self.current_token.value)
            self.consume_token()
            return True
        return False

    def try_parse_integer(self):
        if self.current_token.token_type == tokens.TokenType.t_integer:
            self.class_stack.append(env.Integer(self.current_token.value))
            self.consume_token()
            return True
        return False

    def execute(self, function, *args, error_message=None):
        if not function(*args):
            if error_message is None:
                return False
            else:
                self.error_message_buffer.append(self.error_handler.get_error(self.previous_token, error_message))
                raise RuntimeError(error_message)
