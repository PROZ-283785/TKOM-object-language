import copy


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
        self.data_position = 0
        self.data = None
        self.last_symbol = ''

    def set_data(self, data):
        self.data = data

    def next_symbol(self) -> str:

        symbol = self.data.read(1)
        self.data_position += 1

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
        return symbol

    def get_last_symbol(self):
        return self.last_symbol

    def get_data_range(self, start_position, length):
        """
            Remember in which position was source, get data and come back to that position
        """
        data_position = self.data_position
        self.data.seek(start_position)
        output = self.data.read(length)
        self.data.seek(data_position)
        return output
