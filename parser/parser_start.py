"""
This is a recursive descent parser for the calc
language. 

To write a parser:

    1.) Construct the basic interface (lexer, next, has, must_be).
    2.) Convert each BNF rule into a mutually recursive function.
    3.) Add data structures to build the parse tree.
"""
import sys
from lexer import Token, Lexer


class Parser:
  """
    Parser state will follow the lexer state.
    We consume the stream token by token.
    Match our tokens, if no match is possible, 
    print an error and stop parsing.
    """

  def __init__(self, lexer):
    self.__lexer = lexer

  def __next(self):
    """
        Advance the lexer.
        """
    self.__lexer.next()

  def __has(self, t):
    """
        Return true if t matches the current token.
        """
    ct = self.__lexer.get_tok()
    return ct.token == t

  def __must_be(self, t):
    """
        Return true if t matches the current token.
        Otherwise, we print an error message and
        exit.
        """
    if self.__has(t):
      return True

    # print an error
    ct = self.__lexer.get_tok()
    print(
      f"Parser error at line {ct.line}, column {ct.col}.\nReceived token {ct.token.name} expected {t.name}"
    )
    sys.exit(-1)

  def parse(self):
    """
        Attempt to parse a program.
        """
    self.__program()

  '''
    TOKEN LIST:
    ###########
    INVALID
    EOF
    LPAREN
    RPAREN
    PROC
    COMMA
    LBRACK
    RBRACK
    BEGIN
    END
    INTLIT
    NUMTYPE
    CHARTYPE
    ASSIGN
    SWAP
    IF
    ELSE
    WHILE
    EQ
    NOEQ
    LT
    LTE
    GT
    GTE
    PLUS
    MINUS
    TIMES
    DIV
    EXP
    PRINT
    READ
    FLOATLIT
    CHARLIT
    STRING
    VARIABLE
    #################
    '''

  def __program(self):
    self.__next()

    while not self.__has(Token.EOF):
      self.__statement()

  def __statement(self):
    if self.__has(Token.VARIABLE):
      self.__next()
      self.__ao_expression()
    elif self.__has(Token.NUMTYPE) or self.__has(Token.CHARTYPE):
      self.__next()
      self.__fun_or_decl()
    elif self.__has(Token.PROC):
      self.__next()
      self.__fun()
    elif self.__has(Token.LPAREN):
      self.__next()
      self.__expression()
      self.__must_be(Token.RPAREN)
      self.__next()
    elif self.__has(Token.INTLIT):
      self.__next()
      self.__factor2()
      self.__term2()
      self.__expression2()
    elif self.__has(Token.FLOATLIT):
      self.__next()
      self.__factor2()
      self.__term2()
      self.__expression2()
    else:
      self.__must_be(Token.READ)
      self.__read()

  def __fun_or_decl(self):
    self.__must_be(Token.VARIABLE)
    self.__next()
    if self.__has(Token.LPAREN):
      self.__next()
      self.__fun2()
    elif self.__has(Token.LBRACK):
      self.__next()
      self.__bounds()

  def __decl(self):
    if self.__has(Token.LBRACK):
      self.__next()
      self.__bounds()
    else:
      self.__next()

  def __bounds(self):
    self.__must_be(Token.INTLIT)
    self.__next()
    if self.__has(Token.COMMA):
      self.__next()
      self.__bounds()
    else:
      self.__must_be(Token.RBRACK)
      self.__next()

  def __fun(self):
    self.__must_be(Token.VARIABLE)
    self.__next()
    self.__must_be(Token.LPAREN)
    self.__next()
    self.__fun2()

  def __fun2(self):
    if self.__has(Token.NUMTYPE) or self.__has(Token.CHARTYPE):
      self.__next()
      self.__must_be(Token.VARIABLE)
      self.__next()
      if self.__has(Token.RPAREN):
        self.__next()
      else:
        self.__must_be(Token.COMMA)
        self.__fun2()
    else:
      self.__must_be(Token.RPAREN)
      self.__next()

  def __ao_expression(self):
    if self.__has(Token.EQUAL):
      self.__next()
      self.__expression()
    else:
      self.__factor2()
      self.__term2()
      self.__expression2()

  def __expression(self):
    self.__term()
    self.__expression2()

  def __expression2(self):
    if self.__has(Token.PLUS):
      self.__next()
      self.__term()
      self.__expression2()
    elif self.__has(Token.MINUS):
      self.__next()
      self.__term()
      self.__expression2()

  def __term(self):
    self.__factor()
    self.__term2()

  def __term2(self):
    if self.__has(Token.TIMES):
      self.__next()
      self.__factor()
      self.__term2()
    elif self.__has(Token.DIVIDE):
      self.__next()
      self.__factor()
      self.__term2()

  def __factor(self):
    self.__exponent()
    self.__factor2()

  def __factor2(self):
    if self.__has(Token.POW):
      self.__next()
      self.__factor()

  def __exponent(self):
    if self.__has(Token.LPAREN):
      self.__next()
      self.__expression()
      self.__must_be(Token.RPAREN)
      self.__next()
    elif self.__has(Token.VARIABLE):
      self.__next()
    elif self.__has(Token.INTLIT):
      self.__next()
    elif self.__must_be(Token.FLOATLIT):
      self.__next()

  def __read(self):
    self.__must_be(Token.READ)
    self.__next()
    self.__must_be(Token.VARIABLE)
    self.__next()


# unit test
if __name__ == "__main__":
  p = Parser(Lexer())
  p.parse()
