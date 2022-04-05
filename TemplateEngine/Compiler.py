from .Parser import *

class CodeBuilder:
    def __init__(self,level = 0) -> None:
        self.functionList = dict()
        self.functionList['render'] = {"indent_level":0,"function":[]}
        self.code = self.functionList['render']
        self.code["indent_level"] = level
    
    def switchFunction(self,functionName):
        if(functionName not in self.functionList):
            self.functionList[functionName] = {"indent_level":0,"function":[]}
        self.code = self.functionList[functionName]

    def addLine(self, line):
        self.code["function"].append(" " * self.code["indent_level"] + line + "\n")
    
    def indent(self):
        #self.level += 4
        self.code["indent_level"] += 4

    def dedent(self):
        #self.level -= 4
        self.code["indent_level"] -= 4

    def addSection(self):
        section = CodeBuilder(self.code["indent_level"])
        self.code["function"].append(section)
        return section

    def getCode(self):
        for functionName in self.functionList:
            if(self.functionList[functionName]["indent_level"] != 0):
                raise Exception("CodeBuilder: function " + functionName + "'s indent level is not 0")
        return str(self)
    
    def __str__(self) -> str:
        ret = ""
        for functionName in self.functionList.keys():
            code = self.functionList[functionName]["function"]
            ret += "".join(str(line) for line in code)
            ret += "\n"
        return ret

class Compiler:
    def __init__(self) -> None:
        self.code = CodeBuilder()
        self.varDict = dict()
        self.varList = None
        self.buffer = []
        self.varSpaceList = []
    
    def intoVarSpace(self,functionName):
        self.varSpaceList.append(functionName) #FIXME: to real stack
        if(functionName not in self.varDict):
            self.varDict[functionName] = set()
        self.varList = self.varDict[functionName]

    def leaveVarSpace(self):
        self.varSpaceList.pop()
        if(len(self.varSpaceList) == 0):
            return ''
        self.varList = self.varDict[self.varSpaceList[-1]]
        return self.varSpaceList[-1]

    def flush(self):
        if(len(self.buffer) == 0): return
        if(len(self.buffer) == 1):
            self.code.addLine("result.append(%s)" % self.buffer[0])
        else:
            self.code.addLine("result.extend([%s])" % ",".join(self.buffer))
        self.buffer = []
    
    def compile(self,ast):
        self.function(ast,"render")
        result = self.code.getCode()
        self.code = CodeBuilder()
        self.varDict = dict()
        self.varList = None
        return result

    def function(self,ast,functionName):
        self.code.switchFunction(functionName)
        self.intoVarSpace(functionName)
        self.code.addLine("""def {name}(context,library,do_dots):""".format(name=functionName))
        self.code.indent()
        section = self.code.addSection()
        self.code.addLine("result = []")
        self.template(ast,[])
        for var in self.varList:
            section.addLine("c_{name} = context['{n}']".format(name=var,n=var))
        self.code.addLine("""return "".join(result)""")
        self.code.dedent()
        self.code.switchFunction(self.leaveVarSpace())

    
    def expression(self,node: Expression,toStr=True):
        if(node.name.isdigit()): return node.name
        name = "c_{n}".format(n=node.name)
        if(node.subNameList != []):
            args = ", ".join([repr(arg) for arg in node.subNameList])
            name = "do_dots({name},{args})".format(name=name,args=args)
        for filter in node.filterList: #FIXME:
            name = "library.filter['{f}']({n})".format(f=filter,n=name)
        if(toStr): name = "str({n})".format(n=name)
        return name

    def boolExpr(self,node):
        op_dict = {"gt":" > ","lt":" < ","gte":" >= ","lte":" <= ","eqa":" == ","neqa":" != ","and":" and ","or":" or ","not":"not ","(":"(",")":")"}
        statement = node.nameList
        ret = ""
        for name in statement:
            if(isinstance(name,Expression)):
                ret = ret + self.expression(name,toStr=False)
            else:
                name = op_dict[name]
                ret += name
        return ret

    def template(self,ast,tempVarList):
        for node in ast.nodeList:
            if(isinstance(node, Literal)):
                self.buffer.append(repr(node.text))
            if(isinstance(node, Expression)):
                self.buffer.append(self.expression(node))
                if(node.name not in tempVarList): self.varList.add(node.name)
            if(isinstance(node,Block)):
                self.flush()
                functionName = "block_" + node.blockName
                self.function(node.template,functionName)
                self.buffer.append("{name}(context,library,do_dots)".format(name=functionName))
            if(isinstance(node,FOR)):
                self.flush()
                self.code.addLine("for c_{var} in {iter}:".format(var=node.var.name,iter=self.expression(node.iter,False)))
                # self.varList.add(node.var.name)
                self.varList.add(node.iter.name)
                # self.tempVarList.add(node.var.name)
                tempVarList.append(node.var.name)
                self.code.indent()
                self.template(node.body,tempVarList)
                self.code.dedent()
            if(isinstance(node, IF)):
                self.flush()
                blockList = node.boolBlocks
                i = 0
                for block in blockList:
                    statement = block[0]
                    content = block[1]
                    if(i == 0):
                        self.code.addLine("if {}:".format(self.boolExpr(statement)))
                    else:
                        self.code.addLine("elif {}:".format(self.boolExpr(statement)))
                    i += 1
                    self.code.indent()
                    self.template(content,tempVarList)
                    self.code.dedent()
                if(node.elseBlock != None):
                    self.code.addLine("else:")
                    self.code.indent()
                    self.template(node.elseBlock,tempVarList)
                    self.code.dedent()
            if(isinstance(node,MACRO)):
                self.flush()
                name = node.macroName
                valueList = ["c_" + value for value in node.valueList]
                valueStr = ",".join(valueList)
                self.code.addLine("def macro_{name}({lis}):".format(name=name,lis=valueStr))
                self.code.indent()
                self.template(node.macroBody,node.valueList)
                self.code.dedent()
            if(isinstance(node,CALL)):
                self.flush()
                macroName = node.name
                lis = []
                for value in node.valueList:
                    if(value.name not in tempVarList): self.varList.add(value.name)
                    lis.append(self.expression(value,False))
                valueStr = ",".join(lis)
                self.code.addLine("macro_{name}({lis})".format(name=macroName,lis=valueStr))
            if(isinstance(node,Tag)):
                self.flush()
                tagName = node.tagName
                argList = ",".join([self.expression(arg) for arg in node.argList])
                # self.code.addLine("library.tag['{name}']({args})".format(name=tagName,args=argList))
                self.buffer.append("library.tag['{name}']({args})".format(name=tagName,args=argList))
        self.flush()
