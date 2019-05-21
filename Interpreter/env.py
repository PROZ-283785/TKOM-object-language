from copy import copy


class Environment:

    def __init__(self):
        """
            objects - key : name, value : Object
            functions - key : name, value : Function
        """
        self.objects = {}
        self.functions = {}


class Object:
    def __init__(self, attributes, methods, overridden_ops, base_obj):
        """
           attributes - key : name, value : Attribute
           methods - key : name, value : Function
           operators - key : operator, value : Operator
        """
        self.attributes = attributes
        self.methods = methods
        self.overridden_operators = overridden_ops
        self.base_object = base_obj

    def execute(self, context):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f" Attrs: {self.attributes} \n Methods: {self.methods} \n Overridden_ops: {self.overridden_operators} \n"


class Function:
    def __init__(self, list_of_args, block, ext_obj=None):
        self.list_of_arguments = list_of_args
        self.block = block
        self.extending_object = ext_obj

    def execute(self, context):
        self.block.execute(context)


class Method:
    def __init__(self, identifier, list_of_args, base_obj, list_of_base_obj_args, block):
        self.identifier = identifier
        self.list_of_arguments = list_of_args
        self.base_object = base_obj
        self.arguments_passed_to_base_object = list_of_base_obj_args
        self.block = block

    def execute(self, context, is_constructor=False, virtual_table=None):
        if is_constructor:
            if self.base_object is not None:
                # obsluz klase nadrzedna wywolujac jej konstruktor
                pass
            else:
                object = context.objects[self.identifier.name]
                virtual_table = VirtualTable(self.identifier.name, object)

            # create virt table
            # wykonaj block
            # przypisz virt do zmiennej wyjsciowej
            pass
        # wykonanie czegokolwiek na obiekcie wymaga aktualizacji virtual_table
        new_context = Context(context, virtual_table=virtual_table, level=context.level + 1)
        self.block.execute(new_context)
        for argument in self.list_of_arguments:
            if argument.has_out_keyword:
                new_context.set_value(argument.identifier, new_context.virtual_table)
                break

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Name: {self.identifier.name} Args: {self.list_of_arguments} Base_obj:{self.base_object} B_args:{self.arguments_passed_to_base_object}"


class Attribute:
    def __init__(self, identifier, has_getter, has_setter, value):
        self.identifier = identifier
        self.has_getter = has_getter
        self.has_setter = has_setter
        self.value = value.execute(None)
        self.type = find_type(value)

    def execute(self, context):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.identifier} {self.value.execute()} {self.type}"


class Integer:
    def __init__(self, value):
        self.value = value

    def execute(self, context):
        return self.value


class CharacterConstant:
    def __init__(self, value):
        self.value = value

    def execute(self, context):
        return self.value


class OverriddenOperator:
    def __init__(self, operator, list_of_args, block):
        self.operator = operator
        self.list_of_arguments = list_of_args
        self.block = block

    def execute(self, context):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.operator} {self.list_of_arguments}"


class Assignment:
    def __init__(self, has_this, identifier, value):
        self.has_this_keyword = has_this
        self.identifier = identifier
        self.arithmetic_expression = value

    def execute(self, context):
        context.set_value(self.identifier, self.arithmetic_expression.execute(context))


class Loop:
    def __init__(self, loop, block):
        self.loop = loop
        self.block = block

    def execute(self, context):
        new_context = Context(context)
        self.loop.execute(new_context, self.block)


class ConditionLoop:
    def __init__(self, assignment, condition, step):
        self.assignment = assignment
        self.condition = condition
        self.step = step

    def execute(self, context, block):
        self.assignment.execute(context)
        while self.condition.execute(context) != 0:
            block.execute(context)
            self.step.execute(context)


class CollectionLoop:
    def __init__(self, l_ident, r_ident):
        self.l_identifier = l_ident
        self.r_identifier = r_ident

    def execute(self, context):
        pass


class Argument:
    def __init__(self, name, has_in, has_out):
        self.identifier = name
        self.has_in_keyword = has_in
        self.has_out_keyword = has_out

    def execute(self, context):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.identifier}"


class Block:
    # instrukcje -> przypisanie | wywołanie_funkcji_metody | instrukcja_warunkowa | pętla |
    # obsługa_wejścia_wyjścia;
    def __init__(self, instructions):
        self.instructions = instructions

    def execute(self, context):
        for instruction in self.instructions:
            instruction.execute(context)


class MethodCall:
    def __init__(self, l_ident, r_ident, args):
        self.l_identifier = l_ident
        self.r_identifier = r_ident
        self.arguments = args

    def execute(self, context):
        pass


class FunctionCall:
    def __init__(self, identifier, args):
        self.identifier = identifier
        self.arguments = args
        # self.extending_object = extending_obj

    def execute(self, context):
        # może to być konstruktor
        if context.objects.get(self.identifier.name, None) is not None:
            constructor = context.objects[self.identifier.name].methods[self.identifier.name]
            con_args = constructor.list_of_arguments
            linked_args = {arg.identifier.name: value.identifier for arg, value in zip(con_args, self.arguments)}
            new_context = Context(context, level=context.level + 1)
            new_context.args = linked_args
            context.objects[self.identifier.name].methods[self.identifier.name].execute(new_context, is_constructor=True)
        else:
            function = context.functions[self.identifier.name]
            fun_args = function.list_of_arguments
            linked_args = {arg.identifier.name: value.identifier for arg, value in zip(fun_args, self.arguments)}
            new_context = Context(context, level=context.level + 1)
            # print(f"Poziom: {new_context.level}")
            new_context.args = linked_args
            function.execute(new_context)


class ConditionalInstruction:
    # first cond - first block
    # poprawic strukture w pdfie
    def __init__(self, condition_with_block, block_without_cond):
        self.condition_with_block = condition_with_block
        self.block_without_condition = block_without_cond

    def execute(self, context):
        condition_found = False
        for condition, block in self.condition_with_block:
            if condition.execute(context) == 1:
                new_context = Context(context, level=context.level + 1)
                block.execute(new_context)
                condition_found = True
                break
        if not condition_found and self.block_without_condition is not None:
            new_context = Context(context, level=context.level + 1)
            self.block_without_condition.execute(new_context)


class Input:
    def __init__(self, identifier):
        self.identifier = identifier

    def execute(self, context):
        value = input()
        try:
            int_value = int(value)
            context.set_value(self.identifier, int_value)
        except ValueError:
            context.set_value(self.identifier, value)


class Output:
    def __init__(self, value):
        self.source = value

    def execute(self, context):
        print(self.source.execute(context))


class Step:
    # function call?
    def __init__(self, identifier, arithmetic_expr):
        self.identifier = identifier
        self.arithmetic_expression = arithmetic_expr

    def execute(self, context):
        context.set_value(self.identifier, self.arithmetic_expression.execute(context))


class Condition:
    def __init__(self, l_cond, r_conds):
        self.l_condition_component = l_cond
        self.r_condition_component = r_conds  # [(||, component), (&&, component)]

    def execute(self, context):
        result = self.l_condition_component.execute(context)
        for operator, component in self.r_condition_component:
            if operator == "||":
                result = result or component.execute(context)
            elif operator == "&&":
                result = result and component.execute(context)
        return result


class ConditionComponent:
    def __init__(self, l_factor, r_factors):
        self.l_factor = l_factor
        self.r_factors = r_factors  # [(<=, factor), (<, factor)]

    def execute(self, context):
        result = self.l_factor.execute(context)
        for operator, component in self.r_factors:
            if operator == "<=":
                if result <= component.execute(context):
                    result = 1
                else:
                    result = 0
            elif operator == "<":
                if result < component.execute(context):
                    result = 1
                else:
                    result = 0
            elif operator == ">":
                if result > component.execute(context):
                    result = 1
                else:
                    result = 0
            elif operator == ">=":
                if result >= component.execute(context):
                    result = 1
                else:
                    result = 0
            elif operator == "!=":
                if result != component.execute(context):
                    result = 1
                else:
                    result = 0
            elif operator == '==':
                if result == component.execute(context):
                    result = 1
                else:
                    result = 0
        return result


class Factor:
    def __init__(self, cond_or_expr):
        self.cond_or_a_expr = cond_or_expr

    def execute(self, context):
        return self.cond_or_a_expr.execute(context)


class ParenthesisCondition:
    def __init__(self, has_negation, condition):
        self.has_negation = has_negation
        self.condition = condition

    def execute(self, context):
        if self.has_negation:
            if self.condition.execute(context) == 0:
                return 1
            else:
                return 0
        else:
            return self.condition.execute(context)


class ArithmeticExpression:
    def __init__(self, l_component, r_components_with_op):
        self.l_component = l_component
        self.r_components_with_op = r_components_with_op  # [(+, component), (-, component)]

    def execute(self, context):
        result = self.l_component.execute(context)
        for operator, component in self.r_components_with_op:
            if operator == "+":
                result = result + component.execute(context)
            elif operator == "-":
                result = result - component.execute(context)
        return result


class Component:
    def __init__(self, l_element, r_element_with_op):
        self.l_element = l_element
        self.r_elements_with_op = r_element_with_op  # [(*, element), (/, element) ...]

    def execute(self, context):
        result = self.l_element.execute(context)
        for operator, element in self.r_elements_with_op:
            if operator == "*":
                result = result * element.execute(context)
            elif operator == "/":
                result = result / element.execute(context)
        return result


class Element:
    def __init__(self, element, has_negation_op=False):
        self.has_negation_op = has_negation_op
        self.element = element

    def execute(self, context):
        if self.has_negation_op:
            return (-1) * self.element.execute(context)
        return self.element.execute(context)


class AttributeReference:
    def __init__(self, l_ident, r_ident, has_this=False):
        self.has_this_keyword = has_this
        self.l_identifier = l_ident
        self.r_identifier = r_ident

    def execute(self, context):
        virtual_table = context.get_value(self.l_identifier)
        if find_type(virtual_table) != 'VirtualTable':
            raise Exception("Attribute reference not referencing to the object type value!")
        return virtual_table.get_attribute_value(self.r_identifier.name)


class Identifier:
    def __init__(self, name):
        self.name = name

    def execute(self, context):
        return context.get_value(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}"


class NoneKeyVal:
    @staticmethod
    def execute(context):
        return None


class VirtualTable:
    def __init__(self, object_name, object: Object):
        self.object_type = object_name
        self.attributes = object.attributes
        self.methods = object.methods
        self.overridden_operators = object.overridden_operators

    def get_attribute_value(self, attribute_name: str):
        try:
            return self.attributes[attribute_name].value
        except KeyError:
            raise KeyError("Trying to get value from non-existing attribute")

    def set_attribute_value(self, attribute_name: str, value):
        try:
            self.attributes[attribute_name].value = value
        except KeyError:
            raise KeyError("Trying to get value from non-existing attribute")


# class ObjectContext:
#     def __init__(self, virtual_table: VirtualTable, level=1):
#         self.level = level
#         self.virtual_table = virtual_table
#         self.local_variables = {}
#         self.args = {}
#
#     def set_value(self, identifier: Identifier, value):
#         try:
#             self.virtual_table.set_attribute_value(identifier.name, value)
#         except KeyError:
#             if identifier.name in self.args:
#                 related_identifier = self.args[identifier.name]
#
#             else:
#                 self.local_variables[identifier.name] = value
#
#
#     def get_value(self, identifier: Identifier):
#         try:
#             return self.virtual_table.get_attribute_value(identifier.name)
#         except KeyError:
#             if identifier.name in self.args:
#                 return self.args[identifier.name]
#             elif identifier.name in self.local_variables:
#                 return self.local_variables[identifier.name]
#             else:
#                 raise Exception("Nie ma takeigo elementu")


class Context:
    def __init__(self, previous_context=None, functions=None, objects=None, virtual_table: VirtualTable = None,
                 level=1):
        self.level = level
        self.previous_context = previous_context
        self.local_variables = {}  # key -> identifier value->value
        self.args = {}  # key -> identifier.name value->identifier
        if virtual_table is None and previous_context is not None:
            self.virtual_table = previous_context.virtual_table
        else:
            self.virtual_table = virtual_table
        if functions is None and previous_context is not None:
            self.functions = previous_context.functions
        else:
            self.functions = functions
        if objects is None and previous_context is not None:
            self.objects = previous_context.objects
        else:
            self.objects = objects

    def set_value(self, identifier, value):
        if identifier.name in self.args:
            related_identifier = self.args[identifier.name]
            if find_type(related_identifier) == 'identifier':
                self.previous_context.set_value(related_identifier, value)
            else:
                raise Exception("Something unexpected")
        elif self.virtual_table is not None and identifier.name in self.virtual_table.attributes:
            self.virtual_table.set_attribute_value(identifier.name, value)
        elif identifier.name in self.local_variables:
            self.local_variables[identifier.name] = value
        elif self.previous_context is not None:
            # szukamy we wczesniejszych kontekstach
            if self.set_if_exists(self.previous_context, identifier, value):
                return

            # trzeba utworzyć zmienna
        self.local_variables[identifier.name] = value

    # set_value in current context kiedy mamy when i zmienna z gory nadpisujemy
    # set_value in base_context kiedy arg jest out
    @staticmethod
    def set_if_exists(context, identifier: Identifier, value):
        if identifier.name in context.args:
            related_identifier = context.args[identifier.name]
            if find_type(related_identifier) == 'identifier':
                context.previous_context.set_value(related_identifier, value)
                return True
            else:
                raise Exception("Something unexpected")
        elif context.virtual_table is not None and identifier.name in context.virtual_table.attributes:
            context.virtual_table.set_attribute_value(identifier.name, value)
            return True
        elif identifier.name in context.local_variables:
            context.local_variables[identifier.name] = value
            return True
        return False

    def get_value(self, identifier: Identifier):
        if identifier.name in self.args:
            value = self.args[identifier.name]
            if find_type(value) == 'identifier':
                return self.previous_context.get_value(value)
            else:
                return value
        elif self.virtual_table is not None and identifier.name in self.virtual_table.attributes:
            self.virtual_table.get_attribute_value(identifier.name)
        elif identifier.name in self.local_variables:
            return self.local_variables[identifier.name]
        else:
            value = self.previous_context.get_value(identifier)
            return value


def find_type(value):
    if value.__class__.__name__ == 'CharacterConstant':
        return 'char_const'
    elif value.__class__.__name__ == 'NoneKeyVal':
        return None
    elif value.__class__.__name__ == 'ArithmeticExpression':
        return 'int'
    elif value.__class__.__name__ == 'Identifier':
        return 'identifier'
    elif value.__class__.__name__ == 'Method' or 'Attribute' or 'OverriddenOperator' or 'VirtualTable':
        return value.__class__.__name__
    else:
        raise RuntimeError('Something unexpected happened' + str(value.__class__.__name__))


def move_extending_functions_to_objects(environment):
    identifiers_to_delete = []
    for identifier, function in environment.functions.items():
        extending_object = function.extending_object
        if extending_object is not None:
            extending_object_name = extending_object.name
            if environment.objects.get(extending_object_name, None) is None:
                raise Exception("Brak obiektu!")
            elif environment.objects[extending_object_name].methods.get(identifier, None) is not None:
                raise Exception("Nadpisywanie metody!")
            else:
                environment.objects[extending_object_name].methods[identifier] = function
                identifiers_to_delete.append(identifier)

    for identifier in identifiers_to_delete:
        del environment.functions[identifier]
