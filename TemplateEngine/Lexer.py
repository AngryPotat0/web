from enum import Enum

class TokenType(Enum):
    CTAG        =   'CTAG'
    STR         =   'str'
    LITERAL     =   'LITERAL'
    NUM         =   'Num'
    EXPR        =   'EXPR'
    TAG         =   'TAG'
    FILTER      =   '|'
    DOT         =   '.'
    LPAREN      =   '('
    RPAREN      =   ')'
    COMMA       =   ','
    EQUAL       =   'eqa'
    NOTEQUAL    =   'neqa'
    GT          =   'gt'
    LT          =   'lt'
    GTE         =   'gte'
    LTE         =   'lte'
    AND         =   'and'
    OR          =   'or'
    NOT         =   'not'
    ELIF        =   'elif'
    IF          =   'if'
    ELSE        =   'else'
    ENDIF       =   'endif'
    FOR         =   'for'
    IN          =   'in'
    ENDFOR      =   'endfor'
    MACRO       =   'macro'
    ENDMACRO    =   'endmacro'
    CALL        =   'call'
    BLOCK       =   'block'
    ENDBLOCK    =   'endblock'
    EXTENDS     =   'extends'
    EOF         =   'EOF'

def reserved_keywords():
    token_list = list(TokenType)
    start = token_list.index(TokenType.EQUAL)
    end = token_list.index(TokenType.EOF)
    reserved_keywords = {
        token_type.value : token_type
        for token_type in token_list[start:end]
    }
    return reserved_keywords

class Token:
    def __init__(self, tokenType, tokenValue) -> None:
        self.tokenType = tokenType
        self.tokenValue = tokenValue
    
    def __str__(self):
        return '{type},{value}'.format(type=self.tokenType, value=self.tokenValue)

class Lexer:
    def __init__(self, text) -> None:
        self.text = text
        self.currentIndex = 0
        self.currentChar = self.text[self.currentIndex]
        self.lenOfText = len(text)
        self.tokenList = []
        self.reserved_keywords = reserved_keywords()

    def next(self):
        self.currentIndex += 1
        if(self.currentIndex >= self.lenOfText):
            self.currentChar = None
        else:
            self.currentChar = self.text[self.currentIndex]
    
    def peek(self):
        pos = self.currentIndex + 1
        if(pos >= self.lenOfText):
            return None
        return self.text[pos]
    
    def skipWhiteSpace(self):
        while(self.currentChar != None and self.currentChar == ' '):
            self.next()

    def expression(self): #FIXME:
        self.next()
        self.next() #eat {{
        expr = ''
        while(self.currentChar != None and (self.currentChar.isalpha() or self.currentChar.isdigit() or self.currentChar in ('.', '|',' '))):
            if(self.currentChar == ' '):
                self.skipWhiteSpace()
                continue
            if(self.currentChar == '.'):
                self.tokenList.append(Token(TokenType.EXPR,expr))
                expr = ''
                self.tokenList.append(Token(TokenType.DOT,'.'))
                self.next()
                continue
            if(self.currentChar == '|'):
                self.tokenList.append(Token(TokenType.EXPR,expr))
                expr = ''
                self.tokenList.append(Token(TokenType.FILTER,'|'))
                self.next()
                continue
            expr += self.currentChar
            self.next()
        if(self.currentChar == '}' and self.peek() == '}'):
            self.next()
            self.next()
        else:
            raise Exception("Unexpected char {a} at index {b}\n".format(a=self.currentChar,b=self.currentIndex))
        self.tokenList.append(Token(TokenType.EXPR,expr))

    def note(self):
        self.next()
        self.next() #eat {#
        while(self.currentChar != None and (self.currentChar != '#' or self.peek() != '}')):
            if(self.currentChar == '\\'):
                self.next()
            self.next()
        self.next()
        self.next()

    def tag(self):
        self.next()
        self.next() #eat {%
        temp = ''
        flag = 1

        def addToken(word):
            nonlocal flag
            if(word == ''): return
            if(word in self.reserved_keywords):
                self.tokenList.append(Token(self.reserved_keywords[word],word))
            else:
                if(flag != 1):
                    self.tokenList.append(Token(TokenType.EXPR,word))
                else:
                    self.tokenList.append(Token(TokenType.TAG,word))
            flag = 0
                    
        while(self.currentChar != None and (self.currentChar.isalpha() or self.currentChar.isdigit() or self.currentChar in (' ','(',')',',','.'))):
            if(self.currentChar in (' ','(',')',',','.')):
                if(temp != ''):
                    addToken(temp)
                    temp = ''
                if(self.currentChar == '('):
                    self.tokenList.append(Token(TokenType.LPAREN,'('))
                elif(self.currentChar == ')'):
                    self.tokenList.append(Token(TokenType.RPAREN,')'))
                elif(self.currentChar == ','):
                    self.tokenList.append(Token(TokenType.COMMA,','))
                elif(self.currentChar == '.'):
                    self.tokenList.append(Token(TokenType.DOT,'.'))
                if(self.currentChar == ' '):
                    self.skipWhiteSpace()
                else:
                    self.next()
                continue
            temp += self.currentChar
            self.next()
        if(self.currentChar == '%' and  self.peek() == '}'):
            self.next()
            self.next()
        else:
            raise Exception("Unexpected char {} at index {}\n".format(self.currentChar,self.currentIndex))
        if(self.currentChar == '\n'):
            self.next()

    def literal(self):
        literal = ''
        while(self.currentChar != None and self.currentChar != '{'):
            if(self.currentChar == '\\'):
                literal += self.peek()
            else:
                literal += self.currentChar
            self.next()
        self.tokenList.append(Token(TokenType.LITERAL,literal))

    def extends(self):
        while(self.currentChar != None and (self.currentChar != '@' or self.peek() != '}')):
            self.next()
        self.next()
        self.next()
    
    def lexer(self):
        while(True):
            if(self.currentChar == None):
                self.tokenList.append(Token(TokenType.EOF,'EOF'))
                break
            if(self.currentChar == '\n'):
                self.next()
                continue
            if(self.currentChar == '{'): #LLBRACE OR LTAG
                nextChar = self.peek()
                if(nextChar == '{'): #expression
                    self.expression()
                elif(nextChar == '%'): #tag
                    self.tag()
                    self.tokenList.append(Token(TokenType.CTAG,'CTAG'))
                elif(nextChar == '#'): #注释
                    self.note()
                elif(nextChar == '@'):
                    self.extends()
                else:
                    raise Exception("Unexpected char at index {}".format(self.currentIndex + 1))
            self.literal()
        
        return self.tokenList
