import unittest
from pprint import pprint

import env
import interpreter
import pars
import source
import tokens
import lexer
from tests import interpreter_tests

def main():
    src = source.StreamSource()
    fo = open("test", "r", encoding='utf-8', newline='\n')
    environment = env.Environment()
    src.set_data(fo)
    lex = lexer.Lexer(src)
    parser = pars.Parser(lex, environment)
    inter = interpreter.Interpreter(environment, parser)
    inter.interpret()

    print()
    # pprint(environment.functions)
    # pprint(environment.objects)
    # token = lex.get_token()
    # print(token)
    # i = 0
    # tester = Tester(lex.source)
    # while token.token_type != tokens.TokenType.t_eof:
    #
    #     token = lex.get_token()
    #     if i % 2 == 0:
    #
    #         print(tester.source.get_data_range(token.position_in_file, 10))
    #     i = i + 1
    #     print(token)


def test(function, *args, error_message=None):
    print(*args)
    if not function(*args):
        if error_message is None:
            return False
        else:
            raise RuntimeError(error_message)
    return True


def fun2():
    return True


def fun(a, b, c):
    b = c
    return a == b


class Env:
    def __init__(self, number):
        self.value = number

    def notify(self, object):
        print(f"moje:{self.value} cudze:{object.__class__.__name__}")


class Base:
    shared_element = Env(2)

    def __init__(self, value):
        self.value = value


class DerivedClass(Base):

    def __init__(self, value):
        super().__init__(value)
        self.size = 10
        self.name = "Tom"

        self.shared_element.notify(self)


class Car:
    def __init__(self, speed):
        self.speed = speed

    def __add__(self, other):
        return self.speed + other.speed


def testowa():
    car = Car(50)
    anotherCar = Car(100)
    thirdCar = Car(200)
    print(car + anotherCar + thirdCar)


if __name__ == "__main__":

    main()
    # print(test(fun2, error_message=None))
    # testowa()



