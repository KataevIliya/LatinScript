import math
# noinspection PyUnresolvedReferences
from llvmlite import ir, binding
from rply import ParserGenerator
from TitleClasses import *

err_list = """BaseException
Exception
TypeError
StopAsyncIteration
StopIteration
GeneratorExit
SystemExit
KeyboardInterrupt
ImportError
ModuleNotFoundError
OSError
EnvironmentError
IOError
EOFError
RuntimeError
RecursionError
NotImplementedError
NameError
UnboundLocalError
AttributeError
SyntaxError
IndentationError
TabError
LookupError
IndexError
KeyError
ValueError
UnicodeError
UnicodeEncodeError
UnicodeDecodeError
UnicodeTranslateError
AssertionError
ArithmeticError
FloatingPointError
OverflowError
ZeroDivisionError
SystemError
ReferenceError
MemoryError
BufferError
Warning
UserWarning
DeprecationWarning
PendingDeprecationWarning
SyntaxWarning
RuntimeWarning
FutureWarning
ImportWarning
UnicodeWarning
BytesWarning
ResourceWarning
ConnectionError
BlockingIOError
BrokenPipeError
ChildProcessError
ConnectionAbortedError
ConnectionRefusedError
ConnectionResetError
FileExistsError
FileNotFoundError
IsADirectoryError
NotADirectoryError
InterruptedError
PermissionError
ProcessLookupError
TimeoutError"""

# noinspection PyListCreation
keywords = ["mendacium", "mend", "verum", "nan", "et", "or", "as", "affirmo", "asynch", "exspect", "stop", "gradus",
            #  False      False   True     None   and   or    as    assert     async     await      break   class
            #    +         +        +       +      +    +     ~       +         ~         +           +      ~
            "continue", "define", "dele", "alter", "si", "praeter", "from", "importare", "in", "est", "non", "pass",
            # continue     def      del     else    if     except    from    import       in    is     not    pass
            #    -         +        +       +       +         +        ~         ~         +    +      +      +
            "vocare", "experiri", "donec", "with", "concedere", "munus", "incipere", "sarcina"]
#             raise     try        while    with    yield
#              +         +           +        -       +            +         +            +

functions = ["ostendo", "linea", "integra", "similis", "divide", "multiplicare", "mul", "subtrahe", "summatim",
             # print       str      //       eq types    /          *              *       -            +
             #  +          +        +          +          +            +           +       +            +
             "reliqua", "xor", "factorial", "plus", "minus", "pares", "modulus", "nullam", "lego", "maximum", "minimum",
             # %          ^        !          >        <       ==        abs        hash    input    max       min
             # +         +         +            +       +       +         +         +        +         +          +
             "quatenus", "sum", "look", "rotundatum", "totus", "mori", "aperta"]
#                pow      sum   bininp    round        int      exit     open
#               +          +         +        +         +        +        -


keywords += functions
keywords.append("finis")  # +
keywords.append("all")  # +
keywords.append("sign")  # +
keywords.sort(key=len, reverse=True)

# noinspection PyUnresolvedReferences
err_list = [__builtins__[i] for i in err_list.split("\n")]


class CompileParser:
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator(
            # Список всех токенов, принятых парсером.
            [
                "OPEN_FIGURE",
                "CLOSE_FIGURE",
                "WORD",
                "NUMBER",
                "STRING"
            ] + [i.upper() for i in keywords],
        )
        self.var_dict = {}
        self.func_list = {}
        self.keywords = {i: None for i in keywords}
        self.package_name = "sum"
        self.yield_list = []
        self.input_list = InputStream()
        self.input = input
        self.module = module
        self.builder = builder
        self.printf = printf

    def print(self, *args):
        value = " ".join(map(str, args))
        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%i \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        # Вызов ф-ии Print
        self.builder.call(self.printf, [fmt_arg, value])

    def full_dict(self):
        return set(self.keywords) | set(self.func_list)

    def parse(self):
        @self.pg.production("main : MUNUS function_list INCIPERE body FINIS")
        def main(p):
            def action():
                for line in p[3]:
                    if line.exec() == "exit":
                        break

            return Evaluator(action)

        @self.pg.production("package : SARCINA WORD MUNUS function_list")
        def package(p):
            self.package_name = p[1].value

        @self.pg.production("body : body code_line")
        @self.pg.production("body : code_line")
        def body(p):
            return Body(*p)

        @self.pg.production("function_list : function_list function")
        @self.pg.production("function_list : function")
        def function_list(p):
            return FunctionList(*p)

        @self.pg.production("function : DEFINE WORD word_list EST INCIPERE body FINIS")
        def function(p):
            self.func_list[p[1].value] = p[5], p[2]

        @self.pg.production("word_list : word_list WORD")
        @self.pg.production("word_list : WORD")
        def word_list(p):
            return WordList(*p)

        @self.pg.production("val_list : val_list val_list")
        @self.pg.production("val_list : val_list value")
        @self.pg.production("val_list : value")
        def val_list(p):
            return ValList(*p)

        @self.pg.production("val_list : STRING")
        def val_list(p):
            return ValList(*map(lambda x: Getter(ord(x)), p[0].value[1:-1]))

        @self.pg.production("val_list : EXSPECT OPEN_FIGURE func_reset CLOSE_FIGURE")
        @self.pg.production("val_list : EXSPECT OPEN_FIGURE body CLOSE_FIGURE")
        def val_list(p):
            def action():
                self.yield_list.append([])
                p[2].exec()
                return self.yield_list.pop()

            return ValList(func=action)

        @self.pg.production("value : NUMBER")
        def int_value(p):
            return Number(p[0].value)

        @self.pg.production("value : NON value")
        def int_value(p):
            def action():
                t = p[1].exec()
                if type(t) == bool:
                    return not t
                else:
                    return ~t

            return Executer(action)

        @self.pg.production("value : WORD")
        def var_value(p):
            def action():
                return self.var_dict[p[0].value]

            return Executer(action)

        @self.pg.production("value : MENDACIUM")
        @self.pg.production("value : MEND")
        @self.pg.production("value : VERUM")
        def bool_value(p):
            bd = {"mendacium": False, "mend": False, "verum": True}
            return Bool(bd[p[0].value])

        # noinspection PyUnusedLocal
        @self.pg.production("value : NAN")
        def bool_value(p):
            return Nan()

        @self.pg.production("func_reset : WORD val_list")
        def func_reset(p):
            def action():
                self.var_dict["eventum"] = Nan()
                if len(self.func_list[p[0].value][1]) != len(p[1]):
                    raise ValueError
                for name, val in zip(self.func_list[p[0].value][1], p[1]):
                    if name in self.full_dict():
                        raise ValueError
                    self.var_dict[name] = val.exec()
                self.func_list[p[0].value][0].exec()
                return self.var_dict["eventum"]

            return Executer(action)

        @self.pg.production("value : OPEN_FIGURE func_reset CLOSE_FIGURE")
        def comm_value(p):
            def action():
                return p[1].exec()

            return Executer(action)

        @self.pg.production("value : OPEN_FIGURE SI value value ALTER value CLOSE_FIGURE")
        def if_else_value(p):
            def action():
                if bool(p[2].exec()):
                    return p[3].exec()
                else:
                    return p[5].exec()

            return Executer(action)

        @self.pg.production("code_line : func_reset ALL")
        def code_line0(p):
            return p[0]

        @self.pg.production("code_line : SI value INCIPERE body FINIS ALL")
        def if_code_line(p):
            def action():
                if bool(p[1].exec()):
                    return p[3].exec()

            return Executer(action)

        @self.pg.production("code_line : DONEC value INCIPERE body FINIS ALL")
        def if_code_line(p):
            def action():
                while bool(p[1].exec()):
                    t = p[3].exec()
                    if t == "exit":
                        return t
                return 0

            return Executer(action)

        @self.pg.production("code_line : SI value INCIPERE body FINIS ALTER INCIPERE body FINIS ALL")
        def if_else_code_line(p):
            def action():
                if bool(p[1].exec()):
                    return p[3].exec()
                else:
                    return p[7].exec()

            return Executer(action)

        @self.pg.production("code_line : EXPERIRI INCIPERE body FINIS PRAETER value INCIPERE body FINIS ALL")
        def try_except_code_line(p):
            def action():
                try:
                    return p[2].exec()
                except err_list[p[5].exec()]:
                    return p[7].exec()

            return Executer(action)

        @self.pg.production("code_line : EXPERIRI INCIPERE body FINIS PRAETER INCIPERE body FINIS ALL")
        def try_all_excepts_code_line(p):
            def action():
                # noinspection PyBroadException
                try:
                    return p[2].exec()
                except tuple(err_list):
                    return p[6].exec()

            return Executer(action)

        # noinspection PyUnusedLocal
        @self.pg.production("code_line : MORI ALL")
        def exit_code_line(p):
            def action():
                return "exit"

            return Executer(action)

        # noinspection PyUnusedLocal
        @self.pg.production("code_line : STOP ALL")
        def exit_code_line(p):
            def action():
                return "break"

            return Executer(action)

        @self.pg.production("code_line : VOCARE value ALL")
        def VOCARE(p):
            def action():
                raise err_list[p[1].exec()]

            return Executer(action)

        @self.pg.production("code_line : CONCEDERE value ALL")
        def CONCEDERE(p):
            def action():
                v = p[1].exec()
                self.yield_list[-1].append(Getter(v))
                return v

            return Executer(action)

        # noinspection PyUnusedLocal
        @self.pg.production("code_line : PASS")
        def PASS(p):
            def action():
                pass

            return Executer(action)

        @self.pg.production("code_line : AFFIRMO value value ALL")
        def AFFIRMO(p):
            def action():
                if not bool(p[1].exec()):
                    raise err_list[p[2].exec()]

            return Executer(action)

        @self.pg.production("code_line : WORD EST SIGN value ALL")
        def code_line1(p):
            def action():
                if p[0].value in self.full_dict():
                    raise ValueError
                self.var_dict[p[0].value] = p[3].exec()

            return Executer(action)

        @self.pg.production("func_reset : OSTENDO val_list")
        def OSTENDO(p):
            def action():
                print_list = []
                for t in p[1]:
                    tt = t.exec()
                    if type(tt) == complex:
                        print_list.append(repr(tt)[1:-1])
                    elif tt is None:
                        print_list.append("NaN")
                    elif type(tt) == bool:
                        if tt:
                            print_list.append("Verum")
                        else:
                            print_list.append("Mendacium")
                    else:
                        print_list.append(str(tt))
                print(*print_list)
                return hash(" ".join(print_list))

            return Executer(action)

        @self.pg.production("func_reset : LINEA val_list")
        def LINEA(p):
            def action():
                s = GetString(p[1])
                self.print(s)
                self.var_dict["eventum"] = hash(s)
                return self.var_dict["eventum"]

            return Executer(action)

        @self.pg.production("func_reset : DELE WORD")
        def DELE(p):
            def action():
                v = self.var_dict[p[1].value]
                del self.var_dict[p[1].value]
                return v

            return Executer(action)

        @self.pg.production("func_reset : ET val_list")
        def ET(p):
            def action():
                if len(p[1]) == 0:
                    return Bool(False)
                ans = p[1][0].exec()
                for i in p[1][1:]:
                    try:
                        ans = ans & i.exec()
                    except TypeError:
                        ans = bool(p[1][0].exec())
                        # noinspection PyAssignmentToLoopOrWithParameter
                        for i in p[1][1:]:
                            ans = ans and i.exec()
                        self.var_dict["eventum"] = Bool(bool(ans))
                        return self.var_dict["eventum"].exec()
                self.var_dict["eventum"] = Getter(ans)
                return self.var_dict["eventum"].exec()

            return Executer(action)

        @self.pg.production("func_reset : OR val_list")
        def OR(p):
            def action():
                if len(p[1]) == 0:
                    return Bool(False)
                ans = p[1][0].exec()
                for i in p[1][1:]:
                    try:
                        k = i.exec()
                        assert type(k) != bool
                        ans = ans | k
                    except (TypeError, AssertionError):
                        ans = bool(p[1][0].exec())
                        # noinspection PyAssignmentToLoopOrWithParameter
                        for i in p[1][1:]:
                            ans = ans or i.exec()
                        self.var_dict["eventum"] = Bool(bool(ans))
                        return self.var_dict["eventum"].exec()
                self.var_dict["eventum"] = Getter(ans)
                return self.var_dict["eventum"].exec()

            return Executer(action)

        @self.pg.production("func_reset : IN value OPEN_FIGURE val_list CLOSE_FIGURE")
        def IN(p):
            def action():
                t = p[1].exec()
                for i in p[3]:
                    if t == i.exec():
                        return True
                return False

            return Executer(action)

        @self.pg.production("value : TOTUS value")
        def TOTUS(p):
            def action():
                self.var_dict["eventum"] = Integer(p[1].exec())
                return self.var_dict["eventum"].exec()

            return Executer(action)

        @self.pg.production("func_reset : INTEGRA value value")
        def INTEGRA(p):
            def action():
                return p[1].exec() // p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : SIMILIS val_list")
        def SIMILIS(p):
            def action():
                t = type(p[1][0].exec())
                for i in p[1][1:]:
                    tt = type(i.exec())
                    if t != tt:
                        return False
                return True

            return Executer(action)

        @self.pg.production("func_reset : DIVIDE value value")
        def DIVIDE(p):
            def action():
                return p[1].exec() / p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : MULTIPLICARE value value")
        @self.pg.production("func_reset : MUL value value")
        def MULTIPLICARE(p):
            def action():
                return p[1].exec() * p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : SUBTRAHE value value")
        def SUBTRAHE(p):
            def action():
                return p[1].exec() - p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : SUMMATIM value value")
        def SUMMATIM(p):
            def action():
                return p[1].exec() + p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : RELIQUA value value")
        def RELIQUA(p):
            def action():
                return p[1].exec() % p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : XOR value value")
        def XOR(p):
            def action():
                return p[1].exec() ^ p[2].exec()

            return Executer(action)

        @self.pg.production("value : FACTORIAL value")
        def FACTORIAL(p):
            def action():
                return math.factorial(p[1].exec())

            return Executer(action)

        @self.pg.production("func_reset : value PLUS value")
        def PLUS(p):
            def action():
                return p[0].exec() > p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : value MINUS value")
        def MINUS(p):
            def action():
                return p[0].exec() < p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : value PARES value")
        def PARES(p):
            def action():
                return p[0].exec() == p[2].exec()

            return Executer(action)

        @self.pg.production("func_reset : QUATENUS value value")
        def QUATENUS(p):
            def action():
                try:
                    return math.pow(p[1].exec(), p[2].exec())
                except TypeError as e:
                    if str(e) == "can't convert complex to float":
                        return pow(p[1].exec(), p[2].exec())
                    raise TypeError(e)

            return Executer(action)

        @self.pg.production("value : MODULUS value")
        def MODULUS(p):
            def action():
                return abs(p[1].exec())

            return Executer(action)

        @self.pg.production("func_reset : NULLAM val_list")
        def NULLAM(p):
            def action():
                return hash(p[1])

            return Executer(action)

        # noinspection PyUnusedLocal
        @self.pg.production("value : LOOK")
        def LOOK_val(p):
            def action():
                return self.input_list.bin_get()

            return Executer(action)

        # noinspection PyUnusedLocal
        @self.pg.production("value : LEGO")
        def LEGO_val(p):
            def action():
                return self.input_list.get()[0].exec()

            return Executer(action)

        @self.pg.production("code_line : LOOK word_list ALL")
        def LOOK(p):
            def action():
                for w in p[1]:
                    if w in self.full_dict():
                        raise ValueError
                    self.var_dict[w] = self.input_list.bin_get()

            return Executer(action)

        @self.pg.production("code_line : LEGO word_list ALL")
        def LEGO(p):
            def action():
                it = iter(self.input_list.get())
                for t in p[1]:
                    if t in self.full_dict():
                        raise ValueError
                    self.var_dict[t] = next(it).exec()

            return Executer(action)

        @self.pg.production("func_reset : MAXIMUM val_list")
        def MAXIMUM(p):
            def action():
                return max(map(lambda x: x.exec(), p[1]))

            return Executer(action)

        @self.pg.production("func_reset : MINIMUM val_list")
        def MINIMUM(p):
            def action():
                return min(map(lambda x: x.exec(), p[1]))

            return Executer(action)

        @self.pg.production("func_reset : SUM val_list")
        def SUM(p):
            def action():
                return sum(map(lambda x: x.exec(), p[1]))

            return Executer(action)

        @self.pg.production("func_reset : ROTUNDATUM value value")
        def ROTUNDATUM(p):
            def action():
                return round(p[1].exec(), p[2].exec())

            return Executer(action)

        @self.pg.production("code_line : WITH APERTA val_list INCIPERE body FINIS")
        def open_code_line(p):
            def action():
                file_name = GetString(p[2])
                f = open(file_name)
                _input = self.input
                self.input = f.readline
                self.input_list.stream = self.input
                if p[4].exec() == "exit":
                    return "exit"
                self.input = _input
                self.input_list.stream = self.input

            return Executer(action)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()


class Parser:
    pass
