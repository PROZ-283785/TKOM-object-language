import pars
import source
import tokens
import lexer


def main():

    src = source.StreamSource()
    fo = open("test", "r", encoding='utf-8', newline='\n')
    # fo = StringIO()
    # fo.write('112321312341234 tsdadfds  fasdfasdfasdfasdfasdfaasdfads fads \n')
    # fo.seek(0)
    # src = source.StringSource()
    # fo = "in \nin \0"
    src.set_data(fo)
    lex = lexer.Lexer(src)
    parser = pars.Parser(lex)
    try:
        print(parser.parse())
    except Exception:
        for error_message in parser.error_message_buffer:
            print(error_message)


    # token = lex.get_token()
    # print(token)
    # while token.token_type != tokens.TokenType.t_eof:
    #     token = lex.get_token()
    #     print(token)


def test():
    pass
    # src = source.Source()
    # fo = open("test1", "r", encoding='utf-8', newline='\n')
    # src.set_data(fo)
    # print(src.get_data_range(25, 20))
    # src = source.StreamSource()
    str = 'ca\nper'
    print(str[1:3:])


if __name__ == "__main__":
    main()
    # test()

