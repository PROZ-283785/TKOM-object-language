import source
import tokens
import lexer


def main():

    src = source.Source()
    fo = open("test1", "r", encoding='utf-8', newline='\n')
    src.set_data(fo)

    lex = lexer.Lexer(src)
    for i in range(0, 100):
        token = lex.get_token()
        print(token)
        if token.token_type == tokens.TokenType.t_eof:
            break


def test():
    return


if __name__ == "__main__":
    main()
    # test()

