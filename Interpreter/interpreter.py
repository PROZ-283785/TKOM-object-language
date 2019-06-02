import env


class Interpreter:
    def __init__(self, environment, parser):
        self.environment = environment
        self.parser = parser

    def interpret(self):
        if self.parser.parse():
            starting_fun = ('main', 0)
            if starting_fun in self.environment.functions:
                fails = env.move_extending_functions_to_objects(self.environment)
                fails = fails + env.check_extending_objects(self.environment)
                if fails:
                    for fail in fails:
                        print(fail)
                    return
                main_context = env.Context(functions=self.environment.functions, objects=self.environment.objects)
                try:
                    self.environment.functions[starting_fun].execute(main_context)
                except Exception as e:
                    print(f"{e.__class__.__name__}: {e}")
            else:
                print("Missing main function!")
                return
