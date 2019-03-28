

class Source:
    """
       Attributes:
           line: number of line
           column: position in line
           data_position: position used to access correct symbol in data
           data: source of text
           last_symbol: stored in case there is need to get same symbol more than once
    """
    def __init__(self):

        self.line = 1
        self.column = 0
        self.data = None
        self.last_symbol = ''

    def set_data(self, data):
        self.data = data
        # print(type(data))

    def next_symbol(self) -> str:

        symbol = self.data.read(1)

        if symbol == '':
            symbol = 'EOF'
        elif ord(symbol) == 13:
            self.line += 1
            self.column = 0
            # read second char ( windows end line)
            self.data.read(1)
            symbol = 'EOT'
        else:
            self.column += 1
        self.last_symbol = symbol
        # print(symbol)
        return symbol

    def get_last_symbol(self):
        return self.last_symbol
