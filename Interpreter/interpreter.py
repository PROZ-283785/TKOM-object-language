import env


class Interpreter:
    def __init__(self, environment, parser):
        self.environment = environment
        self.parser = parser

    def interpret(self):
        if self.parser.parse():
            starting_fun = 'main'
            print(starting_fun)
            if starting_fun in self.environment.functions:
                env.move_extending_functions_to_objects(self.environment)
                main_context = env.Context(functions=self.environment.functions, objects=self.environment.objects)
                self.environment.functions[starting_fun].execute(main_context)
            else:
                raise RuntimeError("Missing main function!")
