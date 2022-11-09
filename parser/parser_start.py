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

  '''
  I added this function to make sure that there is no unexpected EOF before
  the program has an END token.
  '''

  def __must_not_be(self, t):
    if self.__has(t):
      ct = self.__lexer.get_tok()
      print(
        f"Parser error at line {ct.line}, column {ct.col}.\nForbidden token {ct.token.name}"
      )
      sys.exit(-1)

    # print an error

  def __print_current_token(self):
    ct = self.__lexer.get_tok()
    print(f"{ct}")

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
    while not self.__has(Token.BEGIN):
      if self.__has(Token.PROC):
        self.__next()
        self.__fun()
        self.__next()
      elif self.__has(Token.NUMTYPE):
        self.__next()
        self.__fun_or_decl()
        self.__next()
      else:
        self.__must_be(Token.CHARTYPE)
        self.__next()
        self.__fun_or_decl()
        self.__next()

    self.__global_block()

  '''
  TODO:
  Implement a stack that stores each scope, so there's no need to hardcode different block levels.
  '''
  def __global_block(self):
    self.__must_be(Token.BEGIN)
    self.__next()
    while not self.__has(Token.END):
      self.__statement()
      
  def __block(self):
    self.__must_be(Token.BEGIN)
    self.__next()
    while not self.__has(Token.END):
      self.__statement()

    self.__next()

  def __statement(self):
    if self.__has(Token.VARIABLE):
      self.__next()
      self.__expr_assign_swap()
    elif self.__has(Token.BEGIN):
      self.__next()
      self.__block()
    elif self.__has(Token.NUMTYPE) or self.__has(Token.CHARTYPE):
      self.__next()
      self.__fun_or_decl()
    elif self.__has(Token.PROC):
      self.__next()
      self.__fun()
    elif self.__has(Token.IF):
      self.__next()
      self.__branch()
    elif self.__has(Token.WHILE):
      self.__next()
      self.__loop()

    elif self.__has(Token.PRINT):
      self.__next()
      self.__print()
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

  #Decides whether a statement beginning with a variable is an expression, 
  #assignment, or swap
  def __expr_assign_swap(self):
    if self.__has(Token.ASSIGN):
      self.__next()
      self.__expression()
    elif self.__has(Token.SWAP):
      self.__next()
      self.__swap()
    else:
      self.__factor2()
      self.__term2()
      self.__expression2()

  def __swap(self):
    self.__must_be(Token.VARIABLE)
    self.__next()
    if self.__has(Token.LBRACK):
      self.__next()
      self.__swap2()

  def __swap2(self):
    self.expression()
    if self.__has(Token.COMMA):
      self.__next()
      self.__expression()
    else:
      self.__must_be(Token.RBRACK)
      self.__next()

  
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
      self.__block()

  def __branch(self):
    self.__condition()
    self.__block()
    self.__branch2()

  def __branch2(self):
    if self.__has(Token.ELSE):
      self.__next()
      self.__block()

  def __loop(self):
    self.__condition()
    self.__block()

  def __condition(self):
    self.__expression()
    if self.__has(Token.EQ) or self.__has(Token.NOEQ) or self.__has(Token.LT) or self.__has(Token.LTE) or self.__has(Token.GT):
      self.__next()
      self.__expression()
    else:
      self.__must_be(Token.GTE)
      self.__next()
      self.__expression()

  def __print(self):
    self.__arg_list()

  def __arg_list(self):
    self.__expression()
    self.__arg_list2()
    
  def __arg_list2(self):
    if self.__has(Token.COMMA):
      self.__next()
      self.__expression()
      self.__arg_list2()
      
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
    elif self.__has(Token.DIV):
      self.__next()
      self.__factor()
      self.__term2()

  def __factor(self):
    self.__exponent()
    self.__factor2()

  def __factor2(self):
    if self.__has(Token.EXP):
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
      #TODO: Decide whether this is a variable by itself,
      #or a function call.
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
