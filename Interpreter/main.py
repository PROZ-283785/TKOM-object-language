import env
import interpreter
import pars
import source
import lexer


def main():
    src = source.StreamSource()
    fo = open("FirstExample", "r", encoding='utf-8', newline='\n')
    environment = env.Environment()
    src.set_data(fo)
    lex = lexer.Lexer(src)
    parser = pars.Parser(lex, environment)
    inter = interpreter.Interpreter(environment, parser)
    inter.interpret()


if __name__ == "__main__":
    main()




