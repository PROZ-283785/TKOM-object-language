import source
import tokens
import lexer
from io import StringIO
import pprint


def main():

    src = source.Source()
    fo = open("test1", "r", encoding='utf-8', newline='\n')
    # fo = StringIO()
    # fo.write('112321312341234 tsdadfds  fasdfasdfasdfasdfasdfaasdfads fads \n')
    # fo.seek(0)
    src.set_data(fo)
    lex = lexer.Lexer(src)
    token = lex.get_token()
    print(token)
    while token.token_type != tokens.TokenType.t_eof:
        token = lex.get_token()
        print(token)


def test():
    src = source.Source()
    fo = open("test1", "r", encoding='utf-8', newline='\n')
    src.set_data(fo)
    print(src.get_data_range(25, 20))


if __name__ == "__main__":
    main()
    # test()

