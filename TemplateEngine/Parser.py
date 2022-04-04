from Lexer import *
from typing import List

class AST:
    pass

class Template(AST):
    def __init__(self) -> None:
        self.nodeList = []
    
    def __str__(self) -> str:
        ans = ""
        for node in self.nodeList:
            ans += str(node)
        return ans + "\n"

class Tag(AST):
    def __init__(self,tagName,argList) -> None:
        self.tagName = tagName
        self.argList = argList
    
    def __str__(self) -> str:
        return self.tagName + "::" + " ".join([str(arg) for arg in self.argList])

class Block(AST):
    def __init__(self,blockName,template):
        self.blockName = blockName
        self.template = template
    
    def __str__(self) -> str:
        return "Block:" + self.blockName + "\n" + str(self.template)

class Literal(AST):
    def __init__(self,text) -> None:
        self.text = text

    def __str__(self) -> str:
        return "Literal: " + self.text + "\n"

class Num(AST):
    def __init__(self,val) -> None:
        self.val = val

    def __str__(self) -> str:
        return str(self.val)

class Expression(AST):
    def __init__(self,name,subNameList,filterList) -> None:
        self.name = name
        self.subNameList = subNameList
        self.filterList = filterList
    
    def __str__(self) -> str:
        result = self.name
        if(self.subNameList != []):
            result += "."
            result += ".".join(self.subNameList)
        if(self.filterList != []):
            result += " | "
            result += " | ".join(self.filterList)
        return "Expression: " + result + "\n"

class IF(AST):
    def __init__(self,boolBlocks,elseBlock):
        self.boolBlocks = boolBlocks
        self.elseBlock = elseBlock

    def __str__(self) -> str:
        pairs = ["statement::" + str(block[0]) + "::\nblock:" + str(block[1]) for block in self.boolBlocks]
        return "IF: " + "\n".join(pairs) + "\n"

class BEXPR(AST):
    #def __init__(self,op,left,right):
    #    self.op = op
    #    self.left = left
    #    self.right = right
    def __init__(self,nameList):
        self.nameList = nameList
    
    def __str__(self) -> str:
        return " ".join([str(name) for name in self.nameList])

class UNARY(AST):
    def __init__(self,op,expr):
        self.op = op
        self.expr = expr

    def __str__(self):
        return self.op + ":" + str(self.expr)

class FOR(AST):
    def __init__(self,var,iter,body) -> None:
        self.var = var
        self.iter = iter
        self.body = body
    
    def __str__(self) -> str:
        return "For: " + str(self.var) + str(self.iter) + str(self.body)  + "END For\n"

class MACRO(AST):
    def __init__(self,macroName,valueList,macroBody) -> None:
        self.macroName = macroName
        self.valueList = valueList
        self.macroBody = macroBody
    
    def __str__(self) -> str:
        lis = "( " + ",".join(self.valueList) + " )"
        return "Macro: " + str(self.macroName) + lis + str(self.macroBody) + "END Macro\n"

class CALL(AST):
    def __init__(self,name,valueList) -> None:
        self.name = name
        self.valueList = valueList
    
    def __str__(self) -> str:
        print("CALL TEST::",self.valueList)
        lis = "( " + ",".join([str(name.name) for name in self.valueList]) + " )"
        return "Call: " + str(self.name) + lis

class Parser:
    def __init__(self,tokenList: List[Token]) -> None:
        self.tokenList = tokenList
        self.currentIndex = 0
        self.currentToken = self.tokenList[self.currentIndex]
        self.dictList = {
            TokenType.LITERAL   : self.literal,
            TokenType.EXPR      : self.expression,
            TokenType.FOR       : self.forLoop,
            TokenType.IF        : self.ifStatement,
            TokenType.MACRO     : self.macro,
            TokenType.CALL      : self.call,
            TokenType.BLOCK     : self.block,
            TokenType.TAG       : self.tag
        }

    def error(self,msg):
        raise Exception(msg)

    def eat(self,tokenType):
        if(self.currentToken.tokenType != tokenType):
            self.error("Parser Error: Unexpected token {} with value {}".format(self.currentToken.tokenType,self.currentToken.tokenValue))
        else:
            self.currentIndex += 1
            self.currentToken = self.tokenList[self.currentIndex]

    def parser(self):
        template = self.template()
        if(self.currentToken.tokenType != TokenType.EOF):
            self.error("EEEEEEEERRRRRROOOOORRRRRRRR!!!!!!!!!!!!!!!")
        return template

    def template(self):
        template = Template()
        while(self.currentToken.tokenType != TokenType.EOF):
            if(self.currentToken.tokenType in self.dictList):
                template.nodeList.append(self.dictList[self.currentToken.tokenType]())
            else:
                break
        return template

    def literal(self):
        ans = Literal(self.currentToken.tokenValue)
        self.eat(TokenType.LITERAL)
        return ans

    def block(self):
        self.eat(TokenType.BLOCK)
        blockName = self.currentToken.tokenValue
        self.eat(TokenType.EXPR)
        self.eat(TokenType.CTAG)
        template = self.template()
        self.eat(TokenType.ENDBLOCK)
        self.eat(TokenType.CTAG)
        return Block(blockName,template)

    def tag(self):
        tagName = self.currentToken.tokenValue
        self.eat(TokenType.TAG)
        args = []
        while(self.currentToken.tokenType != TokenType.CTAG):
            args.append(self.expression(allowFilter=False))
        self.eat(TokenType.CTAG)
        return Tag(tagName,args)

    def expression(self,allowFilter=True): # 现在表达式只有变量名
        expression = self.currentToken.tokenValue
        self.eat(TokenType.EXPR)
        subNameList = []
        while(self.currentToken.tokenType == TokenType.DOT):
            self.eat(TokenType.DOT)
            subNameList.append(self.currentToken.tokenValue)
            self.eat(TokenType.EXPR)
        filterList = []
        if(allowFilter):
            while(self.currentToken.tokenType == TokenType.FILTER):
                self.eat(TokenType.FILTER)
                filterList.append(self.currentToken.tokenValue)
                self.eat(TokenType.EXPR)
        return Expression(expression,subNameList,filterList)

    def num(self):
        val = self.currentToken.tokenValue
        self.eat(TokenType.NUM)
        return Num(int(val))

    def forLoop(self):
        self.eat(TokenType.FOR)
        var = self.expression()
        if(var.subNameList != [] or var.filterList != []):
            self.error("Var of For cannot have subName or Filter")
        self.eat(TokenType.IN)
        iters = self.expression()
        if(iters.filterList != []):
            self.error("Iter of For cannot have subName or Filter")
        self.eat(TokenType.CTAG)
        body = self.template()
        self.eat(TokenType.ENDFOR)
        self.eat(TokenType.CTAG)
        return FOR(var,iters,body)

    def boolExpr(self):
        statement = []
        allowToken = {TokenType.LPAREN,TokenType.RPAREN,TokenType.NOT,TokenType.GT,TokenType.LT,TokenType.GTE,TokenType.LTE,TokenType.EQUAL,TokenType.NOTEQUAL,TokenType.AND,TokenType.OR}
        while(self.currentToken.tokenType == TokenType.EXPR or self.currentToken.tokenType in allowToken):
            if(self.currentToken.tokenType == TokenType.EXPR):
                statement.append(self.expression(allowFilter=False))
            else:
                statement.append(self.currentToken.tokenValue)
                self.eat(self.currentToken.tokenType)
        return BEXPR(statement)

    def ifStatement(self):
        boolBlock = list()
        elseBlock = None
        self.eat(TokenType.IF)
        bExpr = self.boolExpr()
        self.eat(TokenType.CTAG)
        block = self.template()
        boolBlock.append((bExpr,block))
        while(self.currentToken.tokenType == TokenType.ELIF):
            self.eat(TokenType.ELIF)
            bExpr = self.boolExpr()
            self.eat(TokenType.CTAG)
            block = self.template()
            boolBlock.append((bExpr,block))
        if(self.currentToken.tokenType == TokenType.ELSE):
            self.eat(TokenType.ELSE)
            self.eat(TokenType.CTAG)
            elseBlock = self.template()
        self.eat(TokenType.ENDIF)
        self.eat(TokenType.CTAG)
        return IF(boolBlock,elseBlock)

    def macro(self):
        self.eat(TokenType.MACRO)
        macroName = self.currentToken.tokenValue
        valueList = []
        self.eat(TokenType.EXPR)
        self.eat(TokenType.LPAREN)
        if(self.currentToken.tokenType == TokenType.RPAREN):
            self.eat(TokenType.RPAREN)
        else:
            valueList.append(self.currentToken.tokenValue)
            self.eat(TokenType.EXPR)
            while(self.currentToken.tokenType == TokenType.COMMA):
                self.eat(TokenType.COMMA)
                valueList.append(self.currentToken.tokenValue)
                self.eat(TokenType.EXPR)
            self.eat(TokenType.RPAREN)
        self.eat(TokenType.CTAG)
        #body
        body = self.template()
        self.eat(TokenType.ENDMACRO)
        self.eat(TokenType.CTAG)
        return MACRO(macroName,valueList,body)

    def call(self):
        self.eat(TokenType.CALL)
        name = self.currentToken.tokenValue
        valueList = []
        self.eat(TokenType.EXPR)
        self.eat(TokenType.LPAREN)
        if(self.currentToken.tokenType == TokenType.RPAREN):
            self.eat(TokenType.RPAREN)
        else:
            valueList.append(self.expression(False))
            while(self.currentToken.tokenType == TokenType.COMMA):
                self.eat(TokenType.COMMA)
                valueList.append(self.expression(False))
            self.eat(TokenType.RPAREN)
        self.eat(TokenType.CTAG)
        return CALL(name,valueList)
