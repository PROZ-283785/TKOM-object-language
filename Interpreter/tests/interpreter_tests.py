import io
import sys
import unittest
import env
import interpreter
import pars
import lexer
import source


class InterpreterTest(unittest.TestCase):

    def manage_source(self, code):
        self.src.set_data(code)

    def setUp(self):
        self.src = source.StringSource()
        self.lex = lexer.Lexer(self.src)
        self.environment = env.Environment()
        self.parser = pars.Parser(self.lex, self.environment)
        self.program = interpreter.Interpreter(self.environment, self.parser)
        self.output = io.StringIO()
        sys.stdout = self.output

    def test_assignment(self):
        code = "main(){ a = 5; out<<a; } \0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("5\n", self.output.getvalue())

    def test_when(self):
        code = "main(){ a = 5; when( a > 3 ){ out<<a; } } \0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("5\n", self.output.getvalue())

    def test_when_with_else(self):
        code = "main() {" \
               " a = 10; when( a > 10){}else{ out<<a; } } \0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("10\n", self.output.getvalue())

    def test_loop(self):
        code = "main() {" \
               " a = 0; loop( i = 1; i < 3; i = i + 1){ a = a + i;} out<<a; } \0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("3\n", self.output.getvalue())

    def test_loop_with_when(self):
        code = "main(){" \
               "a = 0; loop( i = 1; i < 3; i = i + 1){ " \
               "when( i > 1) { a = a + i;} else{ } }" \
               "out<<a; } \0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("2\n", self.output.getvalue())

    def test_recursion(self):
        code = "main(){x = 2; y = 6; z = 0; power(x, y, z); out<< z;}" \
               "power(x, y, z out){ when( y == 1 ){ z = x; } else { c = y - 1; d = None; power(x, c, d); z = x * d;}}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("64\n", self.output.getvalue())

    def test_recursion2(self):
        code = "main(){ c = 0; d = 5; sum(d, c); out<< c;}" \
               "sum(b in, c out){ when( b >= 1 ){ a = b - 1; d = 0; sum(a, d); c = d + b; } else { c = 0; }}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("15\n", self.output.getvalue())

    def test_changing_value_using_two_functions(self):
        code = "main(){ a = 5; x = None; f(a, x); out<<x;}" \
               "f(a, x out){ b = a + 2; f1(b, x);}" \
               "f1(a, y out){ y = a + 5;}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("12\n", self.output.getvalue())

    def test_creating_new_object_and_getting_value(self):
        code = "main(){ car = None; sp = 10 + 10 * 2; Car(sp, car); out<<car.speed;}" \
               "Car{ speed = None; Car(newSpeed, car out){ when(newSpeed < 100){ when(newSpeed < 50){ when(newSpeed<20)" \
               "{ speed = 20; } else { speed = 50; } } else { speed = 100; } } else { speed = newSpeed; } } }\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("50\n", self.output.getvalue())

    def test_creating_two_objects_of_same_type(self):
        code = "main(){ car = None; sp = 10 + 10 * 2; Car(sp, car); anotherCar = None; sp = 100; Car(sp, anotherCar);" \
               "out<<anotherCar.speed;} Car{ speed = None; Car(newSpeed, car out){ when(newSpeed < 100){ " \
               "when(newSpeed < 50){ when(newSpeed < 20){ speed = 20; } else { speed = 50; } } else { speed = 100; } }" \
               "else { speed = newSpeed; } }}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("100\n", self.output.getvalue())

    def test_extending_non_existing_object(self):
        code = "main(){} setSpeed() extends Car{}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("Fail in function setSpeed -> trying to extend non-existing object: Car\n",
                         self.output.getvalue())

    def test_missing_main(self):
        code = "amin(){}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("Missing main function!\n", self.output.getvalue())

    def test_function_overloading(self):
        code = "main(){ a = 1; b = 2; c = 3; wypiszSume(a, b, c);}" \
               "wypiszSume(a, b, c){ d = a + b + c; out<<d;}" \
               "wypiszSume(a, b){ d = a + b; out<<d;}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("6\n", self.output.getvalue())

    def test_multilevel_inheritance(self):
        code = "main(){ testCar = None; testSpeed = 80; Car(testSpeed, testCar); car = None; sp = 10 + 10 * 2; age = 50; tires = 4; sth = 999; Car(sp, age, tires, sth, car); out<<car.age; out<<car.tires; anotherCar = None; sp = 100; age = age + 20; sth = 1; Car(sp, age, tires, sth, anotherCar); out<<anotherCar.age;}" \
               "Movable { whatever = None; Movable(whateverNew){ whatever = whateverNew; }}" \
               "Vehicle extends Movable{ age = 20; tires = None; Vehicle(newAge, newTires, whatever):Movable(whatever){ age = newAge; tires = newTires; }}" \
               "Car extends Vehicle{ speed = None; Car(newSpeed, car out){ speed = newSpeed; } Car(newSpeed, age, newTires, whatever, car out):Vehicle(age, newTires, whatever){ speed = newSpeed; }}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("50\n4\n70\n", self.output.getvalue())

    def test_operator_overloaded(self):
        code = "main(){ truck = None; anotherTruck = None; sp1 = 50; sp2 = 100; Truck(sp1, truck);" \
               "Truck(sp2, anotherTruck); newTruck = truck + anotherTruck; out<<newTruck.speed;}" \
               "Truck{ speed = 50; Truck(newSpeed, truck out){ speed = newSpeed; } operator + (lhs, rhs, newTruck out)" \
               "{ newSpeed = lhs.speed + rhs.speed; Truck(newSpeed, newTruck); }}\0"
        self.manage_source(code)
        self.program.interpret()
        self.assertEqual("150\n", self.output.getvalue())

    def test_trying_to_use_operator_not_overloaded(self):
        code = "main(){ truck = None; anotherTruck = None; sp1 = 50; sp2 = 100; Truck(sp1, truck);" \
               "Truck(sp2, anotherTruck); newTruck = truck + anotherTruck; out<<newTruck.speed;}" \
               "Truck{ speed = 50; Truck(newSpeed, truck out){ speed = newSpeed; }}\0"
        self.manage_source(code)
        with self.assertRaises(TypeError): self.program.interpret()
