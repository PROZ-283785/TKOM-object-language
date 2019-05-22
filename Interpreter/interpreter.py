import env


class Interpreter:
    def __init__(self, environment, parser):
        self.environment = environment
        self.parser = parser

    def interpret(self):
        if self.parser.parse():
            starting_fun = 'main'
            if starting_fun in self.environment.functions:
                fails = env.move_extending_functions_to_objects(self.environment)
                if len(fails) != 0:
                    for fail in fails:
                        print(fail)
                    return
                main_context = env.Context(functions=self.environment.functions, objects=self.environment.objects)
                self.environment.functions[starting_fun].execute(main_context)
                # print()
            else:
                print("Missing main function!")
                return
