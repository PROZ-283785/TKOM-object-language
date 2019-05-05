
class Environment:

    def __init__(self):
        """
            objects - key : name, value : Object
            functions - key : name, value : Function
        """
        self.objects = {}
        self.functions = {}
        self.context_stack = []


class Object:
    def __init__(self):
        """
           attributes - key : name, value : Attribute
           methods - key : name, value : Function
           operators - key : operator, value : Operator
        """
        self.attributes = {}
        self.methods = {}
        self.overridden_operators = {}
        self.base_object = None


class Function:
    def __init__(self):
        self.list_of_arguments = []
        self.list_of_instructions = []


class Attribute:
    def __init__(self):
        self.has_getter = False
        self.has_setter = False
        self.type = None
        self.value = None

















