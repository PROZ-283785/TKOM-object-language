
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
    def __init__(self, name, attributes, methods, overridden_ops, base_obj):
        """
           attributes - key : name, value : Attribute
           methods - key : name, value : Function
           operators - key : operator, value : Operator
        """
        self.name = name
        self.attributes = {}
        self.methods = {}
        self.overridden_operators = {}
        self.base_object = None


class Function:
    def __init__(self):
        self.name = None
        self.list_of_arguments = []
        self.block = []
        self.extending_object = None


class Attribute:
    def __init__(self):
        self.name = None
        self.has_getter = False
        self.has_setter = False
        self.type = None
        self.value = None


class Method:
    def __init__(self):
        self.name = None
        self.list_of_arguments = []
        self.base_object = None
        self.arguments_passed_to_base_object = []
        self.block = None


class OverriddenOperator:
    def __init__(self):
        self.operator = None
        self.list_of_arguments = []
        self.block = None


class Instruction:
    # ??parse_instruction powinno wrzucac jedna z mozliwosci
    def __init__(self):
        self.instr = None


class Assignment:
    def __init__(self):
        self.has_this_keyword = False
        self.name = None
        self.arithmetic_expression = None


class Loop:
    def __init__(self):
        self.loop = None
        self.block = None


class ConditionLoop:
    def __init__(self):
        self.assignment = None
        self.condition = None
        self.step = None


class CollectionLoop:
    def __init__(self):
        self.l_name = None
        self.r_name = None


class Argument:
    def __init__(self, name):
        self.name = name
        self.has_in_keyword = False
        self.has_out_keyword = False


class Block:
    def __init__(self):
        self.instructions = []


class MethodCall:
    def __init__(self):
        self.l_name = None
        self.r_name = None
        self.arguments = []


class FunctionCall:
    def __init__(self):
        self.name = None
        self.arguments = []
        self.extending_object = None


class ConditionalInstruction:
    # first cond - first block
    # poprawic strukture w pdfie
    def __init__(self):
        self.conditions = None
        self.blocks = None
        self.block_without_condition = None


class Input:
    def __init__(self):
        self.identifier = None


class Output:
    def __init__(self):
        self.source = None

    def execute(self):
        print(self.source.execute())


class Step:
    # function call?
    def __init__(self):
        self.identifier = None
        self.arithmetic_expression = None


class Condition:
    def __init__(self):
        self.l_condition_component = None
        self.r_condition_component = [] #[(||, component), (&&, component)]


class ConditionComponent:
    def __init__(self):
        self.l_factor = None
        self.r_factors = [] #[(<=, factor), (<, factor)]


class Factor:
    def __init__(self):
        self.has_negation = False
        self.cond_or_a_expr = None


class ArithmeticExpression:
    def __init__(self):
        self.l_component = None
        self.r_components = [] #[(+, component), (-, component)]

    def execute(self):
        result = self.l_component.execute()
        for operator, component in self.r_components:
            if operator == "+":
                result = result + component.execute()
            elif operator == "-":
                result = result - component.execute()
        return result


class Component:
    def __init__(self):
        self.l_element = None
        self.r_elements_with_op = [] #[(*, element), (/, element) ...]

    def execute(self):
        result = self.l_element.execute()
        for operator, element in self.r_elements_with_op:
            if operator == "*":
                result = result * element.execute()
            elif operator == "/":
                result = result / element.execute()
        return result


class Element:
    def __init__(self):
        self.has_negation_op = False
        self.element = None

    def execute(self):
        if self.has_negation_op:
            return (-1) * self.element.execute()
        return self.element.execute()


class AttributeReference:
    def __init__(self):
        self.has_this_keyword = False
        self.l_identifier = None
        self.r_identifier = None


class Integer:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class Identifier:
    def __init__(self):
        self.name = None

    def execute(self):
        return self.name


class CharacterConstant:
    def __init__(self):
        self.value = None

    def execute(self):
        return self.value
# takie rzeczcy jak wywolanie funkcji_metody nie wnosza nic do interpreter
# interesuje nas i tak execute na funkcji lub metodzie - po co tworzyc klase? moze przekazac dalej element i tyle








