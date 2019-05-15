import env
import pars
import source
import tokens
import lexer


def main():

    src = source.StreamSource()
    fo = open("test", "r", encoding='utf-8', newline='\n')
    environment = env.Environment()
    src.set_data(fo)
    lex = lexer.Lexer(src)
    parser = pars.Parser(lex, environment)

    print(parser.parse())

    # print(environment.functions)
    # print(environment.objects)

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


def test():
    els = [(1, 2), (2, 3)]
    for el1, el2 in els:
        print(el1)
        print(el2)


if __name__ == "__main__":
    # main()
    test()
