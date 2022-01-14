from rply import LexerGenerator
from LatinScriptParser import keywords
import re


class Lexer:
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # Игнорируем пробелы
        self.lexer.ignore(re.compile("[^a-z0-9.{}\-\"\']+"))
        # Ключевые слова
        for keyword in keywords:
            self.lexer.add(keyword.upper(), re.compile("(?<=[^a-z])" + keyword + "(?=[^a-z])"))
        # Скобки
        self.lexer.add("OPEN_FIGURE", re.compile("{"))
        # noinspection DuplicatedCode
        self.lexer.add("CLOSE_FIGURE", re.compile("}"))
        # Все остальное
        self.lexer.add("STRING", re.compile("\".+\""))
        self.lexer.add("STRING", re.compile("\'.+\'"))
        self.lexer.add("WORD", re.compile("(?<=[^a-z])[a-z]+(?=[^a-z])"))
        self.lexer.add("NUMBER", re.compile("-?[0-9.]+(e[+-]?[0-9]*)?j?"))

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
