from LatinScriptLexer import Lexer
from LatinScriptParser import Parser, CompileParser
from LatinScriptComplier import Compiler
import warnings
from sys import argv
from os import system

COMPILE = True
BUILD = True

warnings.simplefilter("ignore")


def open_file(name):
    with open(name, "r", encoding="utf-8") as f:
        _text_input = f.read().lower()

    if _text_input[0] != "$" or _text_input[-1] != "$":
        raise ValueError
    return _text_input.replace("$", " ")


text_input = open_file(argv[1])
lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

if not COMPILE:
    pg = Parser()
    pg.parse()
    parser = pg.get_parser()
    parser.parse(tokens).eval()
else:
    compiler = Compiler()
    module = compiler.module
    builder = compiler.builder
    printf = compiler.printf

    builder.

    pg = CompileParser(module, builder, printf)
    pg.parse()
    parser = pg.get_parser()
    parser.parse(tokens).eval()

    compiler.create_ir()
    compiler.save_ir("output.ll")
    if BUILD:
        system("llc -filetype=obj -relocation-model=pic output.ll")
        system("gcc output.o -o output")
        print("Выполнение файла:")
        system("./output")


# parser.parse(lexer.lex(open_file("test.ls")))
"""
t = lexer.lex(open_file("test.ls"))
for i in t:
    print(i)
"""
