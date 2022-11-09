import sys
from enum import Enum, auto
from collections import namedtuple


class Token(Enum):
  '''
    Calculate grammar tokens.
    '''
  INVALID = auto()
  EOF = auto()
  LPAREN = auto()
  RPAREN = auto()
  PROC = auto()
  COMMA = auto()
  LBRACK = auto()
  RBRACK = auto()
  BEGIN = auto()
  END = auto()
  INTLIT = auto()
  NUMTYPE = auto()
  CHARTYPE = auto()
  ASSIGN = auto()
  SWAP = auto()
  IF = auto()
  ELSE = auto()
  WHILE = auto()
  EQ = auto()
  NOEQ = auto()
  LT = auto()
  LTE = auto()
  GT = auto()
  GTE = auto()
  PLUS = auto()
  MINUS = auto()
  TIMES = auto()
  DIV = auto()
  EXP = auto()
  PRINT = auto()
  READ = auto()
  FLOATLIT = auto()
  CHARLIT = auto()
  STRING = auto()
  VARIABLE = auto()


TokenDetail = namedtuple('TokenDetail',
                         ('token', 'lexeme', 'value', 'line', 'col'))


class Lexer:

  def __init__(self, lex_file=sys.stdin):
    #set up scanning
    self.__lex_file = lex_file
    self.__line = 1
    self.__col = 0
    self.__cur_char = None

    #scan first char
    self.consume()

    #store current token
    self.__tok = TokenDetail(Token.INVALID, '', None, 0, 0)

  def consume(self):
    #Consume character from stream, makes it the lexer's current character
    self.__cur_char = self.__lex_file.read(1)
    self.__col += 1
    if self.__cur_char == '\n':
      self.__col = 0
      self.__line += 1

  def skip_space_and_comments(self):
    while self.__cur_char.isspace() or self.__cur_char == '#':
      if self.__cur_char == '#':
        # consume the rest of the line
        while self.__cur_char and self.__cur_char != '\n':
          self.consume()

      # consume all the whitespace
      while self.__cur_char.isspace():
        self.consume()

  def get_char(self):
    return str(self.__cur_char)

  def get_line(self):
    return self.__line

  def get_col(self):
    return self.__col

  def get_tok(self):
    return self.__tok

  def __create_tok(self, token, lexeme=None, value=None, line=None, col=None):
    if not lexeme:
      lexem = self.__cur_char
    if not line:
      line = self.__line
    if not col:
      col = self.__col

    return TokenDetail(token, lexeme, value, line, col)

  def __lex_single(self):
    t = [
      ('(', Token.LPAREN),
      (')', Token.RPAREN),
      (',', Token.COMMA),
      ('[', Token.LBRACK),
      (']', Token.RBRACK),
      ('+', Token.PLUS),
      ('-', Token.MINUS),
      ('/', Token.DIV),
      ("=", Token.EQ),
      ("~=", Token.NOEQ),
    ]
    for tok in t:
      if self.__cur_char == tok[0]:
        self.__tok = self.__create_tok(tok[1])
        self.consume()
        return True

    return False

  def __lex_multi_fixed(self):
    t = [
      (":=", Token.ASSIGN),
      (":=:", Token.SWAP),
      ("<", Token.LT),
      ("<=", Token.LTE),
      (">", Token.GT),
      (">=", Token.GTE),
      ("*", Token.TIMES),
      ("**", Token.EXP),
    ]

    cur_lex = ""
    line = self.__line
    col = self.__col
    while len(t) > 1:
      trial_lex = cur_lex + self.__cur_char

      t_old = t
      t = [tok for tok in t if tok[0].startswith(trial_lex)]

      if len(t) == 0:
        t = t_old
        break
      else:
        cur_lex = trial_lex
        self.consume()

    if len(cur_lex) == 0:
      return False

    t = [tok for tok in t if tok[0] == cur_lex]

    if len(t) < 1:
      self.__tok = self.__create_tok(Token.INVALID,
                                     lexeme=cur_lex,
                                     line=line,
                                     col=col)
    else:
      self.__tok = self.__create_tok(t[0][1],
                                     lexeme=cur_lex,
                                     line=line,
                                     col=col)

    return True

  def __lex_other(self):
    if self.__cur_char.isdigit() or self.__cur_char == ".":
      return self.__lex_number()
    elif self.__cur_char.isalpha() or self.__cur_char == "_":
      return self.__lex_keyword_or_var()
    elif self.__cur_char == "\"":
      return self.__lex_string()
    elif self.__cur_char == "\'":
      return self.__lex_char()
    return False

  def __lex_number(self):
    cur_lex = ""
    line = self.__line
    col = self.__col

    while self.__cur_char.isdigit():
      cur_lex += self.__cur_char
      self.consume()

    t = Token.INTLIT

    if self.__cur_char == ".":
      t = Token.FLOATLIT
      cur_lex += self.__cur_char
      self.consume()
      while self.__cur_char.isdigit():
        cur_lex += self.__cur_char
        self.consume()

    if cur_lex[-1] == '.':
      t = Token.INVALID

    if t == Token.INTLIT:
      v = int(cur_lex)
    elif t == Token.FLOATLIT:
      v = float(cur_lex)
    else:
      v = None

    self.__tok = self.__create_tok(t, cur_lex, v, line, col)
    return True

  def __lex_string(self):
    cur_lex = ''
    self.consume()
    line = self.__line
    col = self.__col

    while self.__cur_char != '\"':
      cur_lex += self.__cur_char
      self.consume()

    self.consume()

    self.__tok = self.__create_tok(Token.STRING, cur_lex, line=line, col=col)
    return True

  def __lex_char(self):
    isvalidchar = True
    cur_lex = ''
    self.consume()
    line = self.__line
    col = self.__col

    while self.__cur_char != '\'':
      cur_lex += self.__cur_char
      self.consume()

    self.consume()

    if len(cur_lex) == 1:
      self.__tok = self.__create_tok(Token.CHARLIT,
                                     cur_lex,
                                     line=line,
                                     col=col)

    elif len(cur_lex) == 2:
      escs = ["\\n", "\\t", "\\\'", "\\\""]
      isvalidchar = False
      for esc in escs:
        if esc in cur_lex:
          isvalidchar = True

    else:
      isvalidchar = False

    if isvalidchar:
      self.__tok = self.__create_tok(Token.CHARLIT,
                                     cur_lex,
                                     line=line,
                                     col=col)
    else:
      self.__tok = self.__create_tok(Token.INVALID)

    print(cur_lex)
    return True

  def __lex_keyword_or_var(self):
    kw = [
      ("PROC", Token.PROC),
      ("BEGIN", Token.BEGIN),
      ("END", Token.END),
      ("NUMBER", Token.NUMTYPE),
      ("CHARLIT", Token.CHARTYPE),
      ("IF", Token.IF),
      ("ELSE", Token.ELSE),
      ("WHILE", Token.WHILE),
      ("PRINT", Token.PRINT),
      ("READ", Token.READ),
    ]

    # ^^^^^ Modify only the keyword list to use this function ^^^^^^^

    # start things off
    cur_lex = ''
    line = self.__line
    col = self.__col

    # accumulate all consistent characters
    while self.__cur_char.isalpha() or self.__cur_char.isdigit(
    ) or self.__cur_char == '_':
      cur_lex += self.__cur_char
      self.consume()

    # check if it's a keyword
    kw = [tok for tok in kw if tok[0] == cur_lex]
    if len(kw) == 1:
      t = kw[0][1]
    else:
      t = Token.VARIABLE

    self.__tok = self.__create_tok(t, cur_lex, line=line, col=col)
    return True

  def next(self):
    self.skip_space_and_comments()

    if not self.__cur_char:
      self.__tok = self.__create_tok(Token.EOF)
      return self.__tok
    elif self.__lex_single():
      return self.__tok
    elif self.__lex_multi_fixed():
      return self.__tok
    elif self.__lex_other():
      return self.__tok

    # Catch all
    self.__tok = self.__create_tok(Token.INVALID)
    self.consume()

    return self.__tok


if __name__ == '__main__':
  lex = Lexer()

  while lex.get_tok().token != Token.EOF:
    print(lex.next())
