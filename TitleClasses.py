# noinspection PyUnresolvedReferences
from llvmlite import ir

_int = int


class _Body:
    def __init__(self):
        self.iter = []

    def __getitem__(self, item):
        return self.iter[item]

    def exec(self):
        for line in self.iter:
            v = line.exec()
            if v in ["break", "exit"]:
                return v


def Body(*args):
    if len(args) == 1:
        b = _Body()
        b.iter.append(args[0])
        return b
    args[0].iter.append(args[1])
    return args[0]


class FunctionList:
    def __init__(self, *args):
        self.iter = []
        for i in args:
            # noinspection PyBroadException
            try:
                assert i.value == "pass"
            except Exception:
                if type(i) == FunctionList:
                    self.iter += i.iter
                else:
                    self.iter.append(i)

    def __getitem__(self, item):
        return self.iter[item]


class WordList:
    def __init__(self, *args):
        self.iter = []
        for i in args:
            # noinspection PyBroadException
            try:
                assert i.value == "pass"
            except Exception:
                if type(i) == WordList:
                    self.iter += i.iter
                else:
                    self.iter.append(i.value)

    def __len__(self):
        return len(self.iter)

    def __getitem__(self, item):
        return self.iter[item]


class ValList:
    def __init__(self, *args, func=None):
        self.u = False
        if func is not None:
            self.func = func
            self.u = True
        self.iter = []
        for i in args:
            # noinspection PyBroadException
            try:
                assert i.value == "pass"
            except Exception:
                if type(i) == ValList:
                    self.iter += i.iter
                else:
                    self.iter.append(i)

    def __len__(self):
        return len(self.iter)

    def __getitem__(self, item):
        if self.u:
            self.iter = self.func()
            self.u = False
        return self.iter[item]


# noinspection PyPep8Naming
def Type(t):
    class _Type:
        def __init__(self, builder, module, i):
            self.value = i
            self.t = t

        def exec(self):
            return self.t(self.value)

    return _Type


class Executer:
    def __init__(self, func):
        self.exec = func


def _Int(i):
    i = ir.Constant(ir.IntType(64), int(i))
    return i


def _Float(i):
    i = ir.Constant(ir.DoubleType(), float(i))
    return i


def num(x):
    if type(x) != str:
        return _Float(x)
    if "j" in x:
        return complex(x)
    if ("e" in x) or ("." in x):
        return _Float(x)
    return _Int(x)


Number = Type(num)
Integer = Type(_Int)


def GetString(arg):
    if type(arg) == Nan:
        print("NaN")
        return "NaN"
    if type(arg) == Bool:
        if arg.v:
            print("Verum")
            return "Verum"
        print("Mendacium")
        return "Mendacium"
    s = "".join(map(lambda x: chr(int(x.exec())), arg.iter))
    return s


class Nan(object):
    @staticmethod
    def exec():
        return None


class Bool:
    def __init__(self, v):
        self.v = v

    def exec(self):
        return self.v


class Getter:
    def __init__(self, v):
        self.v = v

    def exec(self):
        return self.v


class InputStream:
    def __init__(self):
        self.iter = []
        self.stream = input

    def EOL(self):
        return not len(self.iter)

    def get(self):
        if self.EOL():
            self.iter = list(self.stream())
        s = "".join(self.iter)
        self.iter = []
        return list(map(Number, s.split()))

    def bin_get(self):
        if self.EOL():
            self.iter = list(self.stream())
        s = ord(self.iter[0])
        self.iter = self.iter[1:]
        return s


class Evaluator:
    def __init__(self, func):
        self.eval = func
