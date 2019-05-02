import tokens


class Parser:

    def __init__(self, lex):
        self.lexer = lex
        self.current_token = lex.get_token()

    def consume_token(self):
        self.current_token = self.lexer.get_token()

    def consume_identifier(self):
        if self.current_token.token_type != tokens.TokenType.t_identifier:
            raise Exception("Powinien być identyfikator")
        self.consume_token()

    def parse(self):
        while self.current_token.token_type != tokens.TokenType.t_eof:
            self.consume_identifier()
            self.try_parse_function()
            self.try_parse_object()
        return "OK"

    def try_parse_function(self):
        if self.current_token.token_type != tokens.TokenType.t_left_parenthesis:
            return False
        self.consume_token()
        self.try_parse_list_of_arguments()
        if self.current_token.token_type != tokens.TokenType.t_right_parenthesis:
            raise Exception("Powiniene byc prawy nawias")
        self.consume_token()
        self.try_parse_extends()
        if not self.try_parse_block():
            raise Exception("Powinien byc blok")
        return True

    def try_parse_block(self):
        if not self.try_parse_left_brace():
            raise Exception("Blok - brak lewgo otwierajacego")
        self.try_parse_instructions()
        if not self.try_parse_right_brace():
            raise Exception("Powinien byc prawy klamrowy")
        return True

    def try_parse_object(self):
        self.try_parse_extends()
        if self.current_token.token_type != tokens.TokenType.t_left_brace:
            return
        self.consume_token()
        while self.current_token.token_type != tokens.TokenType.t_right_brace:
            self.try_parse_method_or_attribute()
            self.try_parse_operator_overloading()
        self.consume_token()

    def try_parse_list_of_arguments(self):
        # { argument_z_przecinkiem }, argument
        if self.try_parse_argument():
            if self.current_token.token_type == tokens.TokenType.t_comma:
                self.consume_token()
                self.try_parse_list_of_arguments()

    def try_parse_argument(self):
        # identyfikator, [ słowo_kluczowe_in ], [ słowo_kluczowe_out ]
        if self.current_token.token_type != tokens.TokenType.t_identifier:
            return False
        self.consume_token()
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'in':
            self.consume_token()
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'out':
            self.consume_token()
        return True

    def try_parse_extends(self):
        if self.current_token.value == 'extends':
            self.consume_token()
            if self.current_token.token_type != tokens.TokenType.t_identifier:
                raise Exception("Powinien byc ident po extends")
            self.consume_token()

    def try_parse_instructions(self):
        # przypisanie | wywołanie_funkcji_metody | instrukcja_warunkowa | pętla |
        # obsługa_wejścia_wyjścia
        if self.try_parse_assignment() or self.try_parse_function_or_method_call() or self.try_parse_conditional_instruction() or self.try_parse_loop() or self.try_parse_in_out():
            while self.try_parse_assignment() or self.try_parse_function_or_method_call() or self.try_parse_conditional_instruction() or self.try_parse_loop() or self.try_parse_in_out():
                continue
            return True
        else:
            return False

    def try_parse_method_or_attribute(self):
        self.try_parse_identifier()
        self.try_parse_method()
        self.try_parse_attribute()

    def try_parse_method(self):
        # lewy_nawias, [lista_argumentów], prawy_nawias, [dwukropek,
        #                                                 identyfikator, lewy_nawias, [lista_argumentów],
        #                                                 prawy_nawias], blok
        if self.current_token.token_type != tokens.TokenType.t_left_parenthesis:
            return False
        self.consume_token()
        self.try_parse_list_of_arguments()
        if self.current_token.token_type != tokens.TokenType.t_right_parenthesis:
            raise Exception("Powinien byc prawy nawias okragly")
        self.consume_token()
        if self.current_token.token_type == tokens.TokenType.t_colon:
            self.consume_token()
            if self.current_token.token_type != tokens.TokenType.t_identifier:
                raise Exception("Powinien byc identyfikator")
            self.consume_token()
            if self.current_token.token_type != tokens.TokenType.t_left_parenthesis:
                raise Exception("Powinien byc otwierajacy")
            self.consume_token()
            self.try_parse_list_of_arguments()
            if self.current_token.token_type != tokens.TokenType.t_right_parenthesis:
                raise Exception("Powinien byc prawy okragly")
            self.consume_token()
        self.try_parse_block()
        return True

    def try_parse_operator_overloading(self):
        # słowo_kluczowe_operator, operator, lewy_nawias,
        # [lista_argumentów], prawy_nawias, blok
        if self.current_token.value != 'operator':
            return False
        self.consume_token()
        self.try_parse_operator()
        if self.current_token.token_type != tokens.TokenType.t_left_parenthesis:
            raise Exception("Powinien byc lewy otwierajacy")
        self.consume_token()
        self.try_parse_list_of_arguments()
        if self.current_token.token_type != tokens.TokenType.t_right_parenthesis:
            raise Exception("Powininien byc prawy zamykajacy")
        self.consume_token()
        self.try_parse_block()
        return True

    def try_parse_attribute(self):
        #  [lewy_nawias_klamrowy, [słowo_kluczowe_get, średnik],
        #                 [słowo_kluczowe_set, średnik], prawy_nawias_klamrowy],
        #                 operator_przypisania,
        # (stała_znakowa | słowo_kluczowe_none | operator_indeksu |
        #  wyrażenie_arytmetyczne), średnik;
        if self.current_token.token_type == tokens.TokenType.t_left_brace:
            self.consume_token()
            if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'get':
                self.consume_token()
                if self.current_token.token_type != tokens.TokenType.t_semicolon:
                    raise Exception("Powinien byc srednik")
                self.consume_token()
            if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'set':
                self.consume_token()
                if self.current_token.token_type != tokens.TokenType.t_semicolon:
                    raise Exception("Powinien byc srednik")
            if self.current_token.token_type != tokens.TokenType.t_right_brace:
                raise Exception("Powinien byc prawy klamrowy")
            self.consume_token()
            if self.current_token.token_type != tokens.TokenType.t_assignment:
                raise Exception("Powinno byc przypisanie")
        elif self.current_token.token_type != tokens.TokenType.t_assignment:
            return False
        #todo

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

    def try_parse_assignment(self):
        # [słowo_kluczowe_this, kropka], identyfikator, operator_przypisania,
        # wyrażenie_arytmetyczne
        pass

    def try_parse_function_or_method_call(self):
        # wywołanie_metody | wywołanie_funkcji
        pass

    def try_parse_conditional_instruction(self):
        # słowo_kluczowe_when, warunek, blok,
        # {słowo_kluczowe_else, słowo_kluczowe_when, blok},
        # [słowo_kluczowe_else, warunek, blok]
        if not self.try_parse_when():
            return False
        if not self.try_parse_condition():
            raise Exception("Brak warunku")
        if not self.try_parse_block():
            raise Exception("Brak bloku")
        
    def try_parse_loop(self):
        # słowo_kluczowe_loop, lewy_nawias, (przypisanie, średnik, warunek,
        #                                    średnik, krok | identyfikator, dwukropek, identyfikator),
        # prawy_nawias, blok
        if self.current_token.token_type != tokens.TokenType.t_key_value or self.current_token.value != 'loop':
            return False
        self.consume_token()
        if not self.try_parse_left_parenthesis():
            raise Exception("Brak lewej klamry")
        if self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'this':
            self.consume_token()
            if not self.try_parse_dot():
                raise Exception("Brak kropki")
        else:
            if not self.try_parse_identifier():
                return False
        if not self.try_parse_collection_loop(): # or self.try_parse_second_loop()
            raise Exception("Zla petla")
        if not self.try_parse_right_parenthesis():
            raise Exception("Brak prawego nawiasu")
        if not self.try_parse_block():
            raise Exception("Zly blok")
        return True

    def try_parse_in_out(self):
        # obsługa_wejścia | obsługa_wyjścia
        return self.try_parse_in() or self.try_parse_out()

    def try_parse_out(self):
        # słowo_kluczowe_out, operator_wczytywania, (wyrażenie_arytmetyczne |
        #                                           stała_znakowa), średnik
        if not (self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'out'):
            return False
        self.consume_token()
        if not self.try_parse_output():
            raise Exception("Brak slowa out")
        if self.try_parse_arithmetic_expression() or self.try_parse_character_constant():
            if self.current_token.token_type != tokens.TokenType.t_semicolon:
                raise Exception("Powinien byc srednik!")
            self.consume_token()
        else:
            raise Exception("Powinno byc wyrazenie lub stala")
        return True

    def try_parse_output(self):
        if self.current_token.token_type != tokens.TokenType.t_output:
            return False
        self.consume_token()
        return True

    def try_parse_arithmetic_expression(self):
        pass

    def try_parse_character_constant(self):
        if self.current_token.token_type == tokens.TokenType.t_character_constant:
            self.consume_token()
            return True
        return False

    def try_parse_in(self):
        # słowo_kluczowe_in, operator_wczytywania, identyfikator, średnik
        if not (self.current_token.token_type == tokens.TokenType.t_key_value and self.current_token.value == 'in'):
            return False
        self.consume_token()
        if not self.try_parse_input():
            raise Exception("Brak >>")
        if not self.try_parse_identifier():
            raise Exception("Brak identyfikatora")
        if not self.try_parse_semicolon():
            raise Exception("Brak średnika")
        return True

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

    def try_parse_collection_loop(self):
        # dwukropek, identyfikator
        if not self.try_parse_colon():
            return False
        if not self.try_parse_identifier():
            raise Exception("Brak identyfikatora")
        return True

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

    def try_parse_condition(self):
        # składowa_warunku, {operator_logiczny, składowa_warunku}
        if not self.try_parse_condition_component():
            raise Exception("Brak składowej")
        #todo

    def try_parse_condition_component(self):
        # czynnik, {operator_relacyjny, czynnik}
        if not self.try_parse_factor():
            raise Exception("Brak czynnika")
        #todo

    def try_parse_factor(self):
        # ([operator_negacji], lewy_nawias, warunek, prawy_nawias) |
        # wyrażenie_arytmetyczne
        if not (self.try_parse_arithmetic_expression() or self.try_parse_parenthesis_expression()):
            raise Exception("Brak wyrazenia lub nawiasow")
        return True

    def try_parse_parenthesis_expression(self):
        negation = False
        if self.try_parse_logical_negation_operator():
           negation = True
        if not self.try_parse_left_parenthesis():
            return False
        if not self.try_parse_condition():
            raise Exception("Brak warunku")
        if not self.try_parse_right_parenthesis():
            raise Exception("Brak prawego okraglego")
        return True

    def try_parse_logical_negation_operator(self):
        if self.current_token.token_type == tokens.TokenType.t_negation:
            self.consume_token()
            return True
        return False




    # Zaznacz które komponenty muszą byc a które są opcjonalne bo masz wybory
    # i czy sa takie ktore w jednym miejscu sa opcjonalne a w innym nie
    # Moze wtedy przeniesc wyjatki na sam dol
    # Jak obsluzyc to dalej?
    #











