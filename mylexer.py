from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: object
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r}, line={self.line}, col={self.col})"

KEYWORDS = {"int", "char", "void", "if", "else", "while", "for", "do", "break", "continue", "return"}
MULTI_OPS = ["==", "!=", "<=", ">=", "&&", "||", "<<", ">>", "+=", "-=", "*=", "/=", "%=", "++", "--"]
SINGLE_OPS = set("{}[]();,+-*/%<>=!~&|^#.")
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "\\": "\\", "'": "'", '"': '"'}

class LexerError(Exception): pass

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []
        self.defines = {}

    def current(self) -> str:
        return self.source[self.i] if self.i < len(self.source) else "\0"

    def peek(self, n: int = 1) -> str:
        return self.source[self.i + n] if (self.i + n) < len(self.source) else "\0"

    def advance(self) -> str:
        ch = self.current()
        self.i += 1
        if ch == "\n": self.line += 1; self.col = 1
        else: self.col += 1
        return ch

    def add(self, token_type: str, value: object, line: int, col: int):
        self.tokens.append(Token(token_type, value, line, col))

    def skip_preprocessor(self):
        """處理預處理指令（#define 等）"""
        self.advance()
        
        while self.current().isspace():
            self.advance()
        
        directive = []
        while self.current().isalpha() or self.current() == '_':
            directive.append(self.current())
            self.advance()
        directive_name = ''.join(directive)
        
        if directive_name == 'define':
            while self.current().isspace():
                self.advance()
            
            const_name = []
            while self.current().isalnum() or self.current() == '_':
                const_name.append(self.current())
                self.advance()
            const_name_str = ''.join(const_name)
            
            while self.current().isspace():
                self.advance()
            
            const_value = []
            while self.current() not in ('\n', '\0'):
                const_value.append(self.current())
                self.advance()
            const_value_str = ''.join(const_value).strip()
            
            try:
                self.defines[const_name_str] = int(const_value_str)
            except:
                pass
        else:
            while self.current() != '\n' and self.current() != '\0':
                self.advance()
        
        if self.current() == '\n':
            self.advance()

    def skip_comment(self):
        if self.current() == '/' and self.peek() == '/':
            while self.current() != '\n' and self.current() != '\0':
                self.advance()
            return True
        elif self.current() == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            while True:
                if self.current() == '\0':
                    raise LexerError(f"Unterminated comment at line {self.line}")
                if self.current() == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    return True
                self.advance()
        return False

    def tokenize(self):
        while self.current() != "\0":
            ch = self.current()
            if ch.isspace(): 
                self.advance()
                continue
            
            if ch == '#':
                self.skip_preprocessor()
                continue
            
            if ch == "'":
                self.read_char()
                continue
            
            if ch == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue
            
            matched = False
            for op in MULTI_OPS:
                if self.source.startswith(op, self.i):
                    line, col = self.line, self.col
                    for _ in op: self.advance()
                    self.add("OP", op, line, col)
                    matched = True; break
            if matched: continue
            
            if ch in SINGLE_OPS:
                line, col = self.line, self.col
                self.advance()
                self.add("OP", ch, line, col)
                continue
            
            if ch.isalpha() or ch == "_": self.read_identifier_or_keyword()
            elif ch.isdigit(): self.read_number()
            elif ch == '"': self.read_string()
            else: raise LexerError(f"Unexpected character {ch!r} at line {self.line}, col {self.col}")
            
        self.add("EOF", "", self.line, self.col)
        return self.tokens

    def read_identifier_or_keyword(self):
        line, col, start = self.line, self.col, self.i
        while self.current().isalnum() or self.current() == "_": self.advance()
        text = self.source[start:self.i]
        self.add("KEYWORD" if text in KEYWORDS else "IDENT", text, line, col)

    def read_number(self):
        line, col, start = self.line, self.col, self.i
        if self.current() == "0" and self.peek().lower() == "x":
            self.advance(); self.advance(); start = self.i
            while self.current().isdigit() or self.current().lower() in "abcdef": self.advance()
            self.add("HEX", int(self.source[start:self.i], 16), line, col)
        else:
            while self.current().isdigit(): self.advance()
            self.add("NUMBER", int(self.source[start:self.i]), line, col)

    def read_string(self):
        line, col = self.line, self.col
        self.advance()
        chars = []
        
        while self.current() != '"':
            if self.current() in ("\0", "\n"):
                raise LexerError(f"Unterminated string at line {line}, col {col}")
            
            if self.current() == "\\":
                self.advance()
                esc = self.current()
                if esc == "\0":
                    raise LexerError(f"Unterminated string at line {line}, col {col}")
                chars.append(ESCAPES.get(esc, esc))
                self.advance()
            else:
                chars.append(self.current())
                self.advance()
        
        self.advance()
        self.add("STRING", "".join(chars), line, col)

    def read_char(self):
        line, col = self.line, self.col
        self.advance()
        
        if self.current() in ("\0", "\n"):
            raise LexerError(f"Unterminated character literal at line {self.line}, col {self.col}")
        
        if self.current() == "\\":
            self.advance()
            esc_char = self.current()
            if esc_char == "\0":
                raise LexerError(f"Unterminated character literal at line {self.line}, col {self.col}")
            char_value = ord(ESCAPES.get(esc_char, esc_char))
            self.advance()
        else:
            char_value = ord(self.current())
            self.advance()
        
        if self.current() != "'":
            raise LexerError(f"Unterminated character literal at line {self.line}, col {self.col}")
        
        self.advance()
        self.add("CHAR", char_value, line, col)

def tokenize(source: str):
    return Lexer(source).tokenize()
