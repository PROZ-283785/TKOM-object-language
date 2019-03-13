import source


def main():

    src = source.Source()
    fo = open("test1", "r", encoding='utf-8', newline='\n')
    src.set_data(fo)

    while True:
        symbol = src.next_symbol()
        print("{position}:{line}:{column}:{symbol}".format(position=src.data_position, line=src.line, column=src.column,
                                                         symbol=symbol), end="\n")
        if symbol == 'EOF':
            break


if __name__ == "__main__":
    main()
