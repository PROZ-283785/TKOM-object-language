from copy import deepcopy
from enum import Enum


class Environment:

    def __init__(self):
        """
            objects - key : name, value : Object
            functions - key : (name, amount_of_args), value : Function
        """
        self.objects = {}
        self.functions = {}


class Object:
    def __init__(self, attributes, methods, overridden_ops, base_obj: 'Identifier'):
        """
           attributes - key : name, value : Attribute
           methods - key : (name, amount_of_args), value : Function
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


# identyfikator, lewy_nawias, [ lista_argumentów ], prawy_nawias, [ dwukropek,
# identyfikator, lewy_nawias, [ lista_argumentów ], prawy_nawias ], blok;
# base_obj : Vehicle(argsy)
class Method:
    def __init__(self, identifier, list_of_args, base_obj=None, list_of_base_obj_args=None, block=None):
        self.identifier = identifier
        self.list_of_arguments = list_of_args
        self.base_object_constructor_call = base_obj
        self.arguments_passed_to_base_object = list_of_base_obj_args
        self.block = block

    def execute(self, context, is_constructor=False):
        if is_constructor:
            if context.virtual_table is None:
                object = context.objects[self.identifier.name]
                context.virtual_table = VirtualTable(self.identifier.name, object, context.objects)
            if context.objects[self.identifier.name].base_object is not None:
                # Car():Vehicle()
                if self.base_object_constructor_call is not None:
                    # obsluz klase nadrzedna wywolujac jej konstruktor
                    base_obj_name = self.base_object_constructor_call.name
                    # stwórz relacje miedzy argsami - powinno sprawdzić czy ilość się zgadza
                    try:
                        constructor_method = context.objects[base_obj_name].methods[
                            (base_obj_name, len(self.arguments_passed_to_base_object))]
                    except KeyError:
                        raise TypeError(
                            f"{base_obj_name}() missing function with "
                            f"{len(self.arguments_passed_to_base_object)} arguments") from None
                    constructor_method_args = constructor_method.list_of_arguments
                    linked_args = {arg.identifier.name: value.identifier for arg, value in
                                   zip(constructor_method_args, self.arguments_passed_to_base_object)}
                    permission_args = create_permission_dict_for_args(constructor_method_args)
                    new_context = Context(previous_context=context, virtual_table=context.virtual_table,
                                          look_previous_context=False, look_virtual_table=True, level=context.level + 1)
                    new_context.args = linked_args
                    new_context.args_permission = permission_args
                    constructor_method.execute(new_context, is_constructor=True)
            self.block.execute(context)
            # przypisz virt do zmiennej wyjsciowej
            for argument in self.list_of_arguments:
                if argument.has_out_keyword:
                    context.set_value(argument.identifier, context.virtual_table)
                    break
            return
        self.block.execute(context)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Name: {self.identifier.name} Args: {self.list_of_arguments} B_args:{self.arguments_passed_to_base_object}"


class Attribute:
    def __init__(self, identifier, has_getter, has_setter, value):
        self.identifier = identifier
        self.has_getter = has_getter
        self.has_setter = has_setter
        self.value = value.execute(None)

    def execute(self, context):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.identifier} {self.value.execute()}"


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
        # operator + (lhs, rhs, result out){}
        self.block.execute(context)
        return context.get_value(self.list_of_arguments[2].identifier)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.operator} {self.list_of_arguments}"


class Assignment:
    def __init__(self, has_this, identifier, value, line):
        self.has_this_keyword = has_this
        self.identifier = identifier
        self.arithmetic_expression = value
        self.line = line

    def execute(self, context):
        try:
            context.set_value(self.identifier, self.arithmetic_expression.execute(context))
        except Exception as e:
            raise Exception(f"{e.__class__.__name__} in line {self.line} -> {e}") from None


class Loop:
    def __init__(self, loop, block):
        self.loop = loop
        self.block = block

    def execute(self, context):
        new_context = Context(context, look_previous_context=True, level=context.level + 1)
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


def check_attributes_match(method_args: list, attributes: dict):
    for argument in method_args:
        if argument.identifier.name in attributes:
            raise NameError(
                f"'{argument.identifier.name}' -> Methods should have argument names different than attribute names!")


class MethodCall:
    def __init__(self, l_ident, r_ident, args, line):
        self.l_identifier = l_ident
        self.r_identifier = r_ident
        self.arguments = args
        self.line = line

    def execute(self, context):
        virtual_table = context.get_value(self.l_identifier)
        object = context.objects[virtual_table.object_type]
        try:
            method = object.methods[(self.r_identifier.name, len(self.arguments))]
        except KeyError:
            raise TypeError(
                f"Line {self.line} -> {self.r_identifier.name}() missing function with {len(self.arguments)} arguments") from None
        method_args = method.list_of_arguments
        check_attributes_match(method_args, object.attributes)
        linked_args = {arg.identifier.name: value.identifier for arg, value in zip(method_args, self.arguments)}
        permission_args = create_permission_dict_for_args(method_args)
        new_context = Context(context, virtual_table=virtual_table, look_virtual_table=True, level=context.level + 1)
        new_context.args = linked_args
        new_context.args_permission = permission_args
        method.execute(new_context)


class FunctionCall:
    def __init__(self, identifier, args, line):
        self.identifier = identifier
        self.arguments = args
        self.amount_of_args = len(self.arguments)
        self.line = line

    def execute(self, context):
        # może to być konstruktor
        if context.objects.get(self.identifier.name, None) is not None:
            try:
                constructor = context.objects[self.identifier.name].methods[(self.identifier.name, self.amount_of_args)]
            except KeyError:
                raise TypeError(
                    f"Line {self.line} -> {self.identifier.name}() missing function with {self.amount_of_args} arguments") from None
            con_args = constructor.list_of_arguments
            check_attributes_match(con_args, context.objects[self.identifier.name].attributes)
            linked_args = {arg.identifier.name: value.identifier for arg, value in zip(con_args, self.arguments)}
            permission_args = create_permission_dict_for_args(con_args)
            new_context = Context(context, level=context.level + 1)
            new_context.args = linked_args
            new_context.args_permission = permission_args
            context.objects[self.identifier.name].methods[(self.identifier.name, self.amount_of_args)].execute(
                new_context,
                is_constructor=True)
        else:
            try:
                function = context.functions[(self.identifier.name, self.amount_of_args)]
            except KeyError:
                raise TypeError(
                    f"Line {self.line} -> {self.identifier.name}() missing function with {self.amount_of_args} arguments") from None
            fun_args = function.list_of_arguments
            linked_args = {arg.identifier.name: value.identifier for arg, value in zip(fun_args, self.arguments)}
            permission_args = create_permission_dict_for_args(fun_args)
            new_context = Context(context, virtual_table=None, look_virtual_table=False, level=context.level + 1)
            new_context.args = linked_args
            new_context.args_permission = permission_args
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
                new_context = Context(context, look_previous_context=True, level=context.level + 1)
                block.execute(new_context)
                condition_found = True
                break
        if not condition_found and self.block_without_condition is not None:
            new_context = Context(context, look_previous_context=True, level=context.level + 1)
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
            result = execute_operator(result, operator, component, context)
            if result:
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
            result = execute_operator(result, operator, component, context)
        return result


class Component:
    def __init__(self, l_element, r_element_with_op):
        self.l_element = l_element
        self.r_elements_with_op = r_element_with_op  # [(*, element), (/, element) ...]

    def execute(self, context):
        result = self.l_element.execute(context)
        for operator, element in self.r_elements_with_op:
            result = execute_operator(result, operator, element, context)
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
    def __init__(self, l_ident, r_ident, line, has_this=False):
        self.has_this_keyword = has_this
        self.l_identifier = l_ident
        self.r_identifier = r_ident
        self.line = line

    def execute(self, context):
        virtual_table = context.get_value(self.l_identifier)
        if not isinstance(virtual_table, VirtualTable):
            raise Exception(f"Line {self.line} -> Attribute reference not referencing to the object type value!")
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
    def __init__(self, object_name, object: Object, env_objects: dict):
        self.object_type = object_name
        self.attributes, self.methods, self.overridden_operators = self.create_dicts(object, env_objects,
                                                                                     object.base_object)

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

    @staticmethod
    def create_dicts(object: Object, env_objects: dict, base_object_id: Identifier = None):
        attributes = deepcopy(object.attributes)
        methods = deepcopy(object.methods)
        overridden_operators = deepcopy(object.overridden_operators)
        while base_object_id is not None:
            base_object = env_objects.get(base_object_id.name, None)
            if base_object is None:
                raise NameError(f"{base_object_id.name} is not defined!")
            else:
                for key, value in base_object.attributes.items():
                    if key not in attributes:
                        attributes[key] = deepcopy(value)
                for key, value in base_object.methods.items():
                    if key not in methods:
                        methods[key] = value
                for key, value in base_object.overridden_operators.items():
                    if key not in overridden_operators:
                        overridden_operators[key] = value
            base_object_id = base_object.base_object
        return attributes, methods, overridden_operators


"""
    look_previous_context -> functions and methods cant look to previous context, when and loop can        
"""


class Context:
    def __init__(self, previous_context=None, functions=None, objects=None, virtual_table: VirtualTable = None,
                 look_previous_context=False, look_virtual_table=True, level=1):
        self.level = level
        self.previous_context = previous_context
        self.local_variables = {}  # key -> identifier value->value
        self.args = {}  # key -> identifier.name value->identifier
        self.args_permission = {}
        self.can_look_previous_context = look_previous_context
        self.can_look_virtual_table = look_virtual_table
        if self.can_look_virtual_table and virtual_table is None and previous_context is not None:
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

    def set_value(self, identifier: Identifier, value):
        if identifier.name in self.args:
            if self.args_permission[identifier.name] == Permission.READ_ONLY:
                raise TypeError(f"Trying to set value to read-only argument '{identifier.name}'")
            related_identifier = self.args[identifier.name]
            if isinstance(related_identifier, Identifier):
                self.previous_context.set_value(related_identifier, value)
            elif isinstance(related_identifier, str):
                self.args[identifier.name] = value
            else:
                raise Exception("Something unexpected")
        elif self.virtual_table is not None and identifier.name in self.virtual_table.attributes:
            self.virtual_table.set_attribute_value(identifier.name, value)
        elif identifier.name in self.local_variables:
            self.local_variables[identifier.name] = value
        elif self.can_look_previous_context and self.previous_context is not None:
            # szukamy we wczesniejszych kontekstach
            if self.set_if_exists(self.previous_context, identifier, value):
                return
            else:
                self.local_variables[identifier.name] = value
        else:
            # trzeba utworzyć zmienna
            self.local_variables[identifier.name] = value

    # set_value in current context kiedy mamy when i zmienna z gory nadpisujemy
    # set_value in base_context kiedy arg jest out
    @staticmethod
    def set_if_exists(context, identifier: Identifier, value):
        while context is not None:
            if identifier.name in context.args:
                if context.args_permission[identifier.name] == Permission.READ_ONLY:
                    raise TypeError(f"Trying to set value to read-only argument '{identifier.name}'")
                related_identifier = context.args[identifier.name]
                if isinstance(related_identifier, Identifier):
                    context.previous_context.set_value(related_identifier, value)
                    return True
                elif isinstance(related_identifier, str):
                    context.args[identifier.name] = value
                else:
                    raise Exception("Something unexpected")
            elif context.virtual_table is not None and identifier.name in context.virtual_table.attributes:
                context.virtual_table.set_attribute_value(identifier.name, value)
                return True
            elif identifier.name in context.local_variables:
                context.local_variables[identifier.name] = value
                return True
            if context.can_look_previous_context:
                context = context.previous_context
            else:
                context = None
        return False

    def get_value(self, identifier: Identifier):
        if identifier.name in self.args:
            if self.args_permission[identifier.name] == Permission.WRITE_ONLY:
                raise TypeError(f"Trying to get value from write-only argument '{identifier.name}'")
            value = self.args[identifier.name]
            if isinstance(value, Identifier):
                return self.previous_context.get_value(value)
            else:
                return value
        elif self.virtual_table is not None and identifier.name in self.virtual_table.attributes:
            return self.virtual_table.get_attribute_value(identifier.name)
        elif identifier.name in self.local_variables:
            return self.local_variables[identifier.name]
        elif self.previous_context is not None:
            value = self.previous_context.get_value(identifier)
            return value
        raise NameError(f"{identifier.name} is not defined!")


def find_type(value):
    return value.__class__.__name__


def object_has_operator_overloaded(object_instance: VirtualTable, operator, objects: dict):
    object = objects.get(object_instance.object_type, None)
    if object is not None:
        for overridden_operator in object.overridden_operators:
            if overridden_operator == operator:
                return True
        raise TypeError(f"{object_instance.object_type} does not have operator {operator} overloaded!")
    else:
        raise NameError(f'{object_instance.object_type} is not defined!')


def move_extending_functions_to_objects(environment):
    fails = []
    identifiers_to_delete = []
    for identifier, function in environment.functions.items():
        extending_object = function.extending_object
        if extending_object is not None:
            extending_object_name = extending_object.name
            if environment.objects.get(extending_object_name, None) is None:
                fails.append(
                    f"Fail in function {identifier[0]} -> trying to extend non-existing object: "
                    f"{function.extending_object}")
            elif environment.objects[extending_object_name].methods.get(identifier, None) is not None:
                fails.append(f"Fail - function {identifier[0]} declared more than once")
            else:
                environment.objects[extending_object_name].methods[identifier] = function
                identifiers_to_delete.append(identifier)

    for identifier in identifiers_to_delete:
        del environment.functions[identifier]

    return fails


def check_extending_objects(environment):
    fails = []
    for identifier, obj in environment.objects.items():
        if obj.base_object is not None and obj.base_object.name not in environment.objects.keys():
            fails.append(f"Fail in object {identifier} -> trying to extend non-existing object: "
                         f"{obj.base_object.name}")
    return fails


def execute_operator(result, operator, component, context):
    if isinstance(result, VirtualTable):
        return execute_overloaded_operator(result, operator, component, context)
    else:
        try:
            rhs = component.execute(context)
            result = int(eval(f"{result}{operator}{rhs}"))
        except Exception as e:
            raise Exception(
                f"'{e.__class__.__name__}' while calculating {find_type(result)} {operator} {find_type(rhs)}") from None
        return result


def execute_overloaded_operator(result, operator: str, component: Component, context: Context):
    if object_has_operator_overloaded(result, operator, context.objects):
        overridden_operator_method = context.objects[result.object_type].overridden_operators[operator]
        method_args = overridden_operator_method.list_of_arguments
        linked_args = {method_args[0].identifier.name: result,
                       method_args[1].identifier.name: component.execute(context),
                       method_args[2].identifier.name: 'out'}
        permission_args = {
            method_args[0].identifier.name: Permission.READ_ONLY,
            method_args[1].identifier.name: Permission.READ_ONLY,
            method_args[2].identifier.name: Permission.READ_AND_WRITE
        }
        new_context = Context(context, look_virtual_table=False, level=context.level + 1)
        new_context.args = linked_args
        new_context.args_permission = permission_args
        return overridden_operator_method.execute(new_context)
    else:
        raise TypeError(f"{result.object_type} does not have operator {operator} overloaded")


def create_permission_dict_for_args(arguments: list):
    permission_dict = {}
    for arg in arguments:
        if arg.has_in_keyword and arg.has_out_keyword:
            permission_dict[arg.identifier.name] = Permission.READ_AND_WRITE
        elif arg.has_in_keyword:
            permission_dict[arg.identifier.name] = Permission.READ_ONLY
        else:
            permission_dict[arg.identifier.name] = Permission.WRITE_ONLY
    return permission_dict


class Permission(Enum):
    READ_ONLY = 1
    WRITE_ONLY = 2
    READ_AND_WRITE = 3
